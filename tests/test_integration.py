"""Real-MySQL integration tests. All inserted rows are rolled back after each test."""
import uuid
from datetime import date, timedelta
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from backend.main import app
from backend.database import engine, get_db
from backend.models import User, Category, Centre, CollectionRequest, RequestItem, StatusHistory
from backend.auth import password_hasher

@pytest.fixture()
def ctx():
    connection=engine.connect()
    transaction=connection.begin()
    db=Session(bind=connection,join_transaction_mode='create_savepoint',expire_on_commit=False)
    suffix=uuid.uuid4().hex[:12]
    users=[User(name='Test Admin',email=f'admin-{suffix}@example.com',role='admin',password_hash=password_hasher.hash('Testing123!')),User(name='Test User',email=f'user-{suffix}@example.com',role='user',password_hash=password_hasher.hash('Testing123!'))]
    cat=Category(name=f'Test devices {suffix}'); centre=Centre(name=f'Test centre {suffix}',address='10 Test Street, Fictional City',phone='5550100000')
    db.add_all([*users,cat,centre]); db.commit()
    def test_db():
        try:
            yield db
        except Exception:
            db.rollback()
            raise
    app.dependency_overrides[get_db]=test_db
    with TestClient(app,raise_server_exceptions=False) as client:
        headers=[]
        for u in users:
            r=client.post('/api/auth/login',json={'email':u.email,'password':'Testing123!'})
            assert r.status_code==200,r.text
            headers.append({'Authorization':'Bearer '+r.json()['token']})
        yield client,db,users,cat,centre,*headers
    app.dependency_overrides.clear(); db.close(); transaction.rollback(); connection.close()

def payload(cat):
    return {'address':'42 Test Avenue, Fictional City','items':[{'category_id':cat.id,'condition':'Damaged','quantity':2,'estimated_weight':'3.50'},{'category_id':cat.id,'condition':'Working','quantity':1,'estimated_weight':'1.25'}]}

def test_registration_and_login(ctx):
    c,db,*_=ctx
    email=f'reg-{uuid.uuid4().hex}@example.com'
    r=c.post('/api/auth/register',json={'name':'New Member','email':email,'password':'Strong123!'})
    assert r.status_code==201
    assert r.json()['user']['role']=='user'
    stored=db.scalar(select(User).where(User.email==email))
    assert stored.password_hash!='Strong123!' and password_hasher.verify('Strong123!',stored.password_hash)
    assert c.post('/api/auth/login',json={'email':email,'password':'Strong123!'}).status_code==200
    assert c.post('/api/auth/login',json={'email':email,'password':'wrong'}).status_code==401
    assert c.post('/api/auth/register',json={'name':'Other','email':email,'password':'Strong123!'}).status_code==409

def test_permissions_and_ownership(ctx):
    c,db,users,cat,centre,ah,uh=ctx
    assert c.get('/api/requests').status_code==401
    assert c.get('/api/reports',headers=uh).status_code==403
    assert c.post('/api/centres',headers=uh,json={'name':'X'}).status_code==403
    r=c.post('/api/requests',headers=ah,json=payload(cat)).json()
    assert c.get(f"/api/requests/{r['id']}",headers=uh).status_code==404
    assert all(x['id']!=r['id'] for x in c.get('/api/requests',headers=uh).json())
    assert c.delete(f"/api/requests/{r['id']}",headers=uh).status_code==404
    assert c.patch(f"/api/requests/{r['id']}/workflow",headers=uh,json={'status':'Recycled'}).status_code==403

def test_complete_collection_workflow(ctx):
    c,db,users,cat,centre,ah,uh=ctx
    baseline=c.get('/api/dashboard',headers=uh).json()
    result=c.post('/api/requests',headers=uh,json=payload(cat)); assert result.status_code==201,result.text
    r=result.json(); path=f"/api/requests/{r['id']}"
    assert len(r['items'])==2 and len(r['history'])==1
    db.expire_all(); assert db.get(CollectionRequest,r['id']).address==payload(cat)['address']
    assert c.patch(path+'/workflow',headers=ah,json={'status':'Recycled'}).status_code==409
    assert c.patch(path+'/workflow',headers=ah,json={'status':'Scheduled','centre_id':centre.id,'pickup_date':str(date.today()-timedelta(days=1))}).status_code==422
    result=c.patch(path+'/workflow',headers=ah,json={'status':'Scheduled','centre_id':centre.id,'pickup_date':str(date.today()+timedelta(days=1))}); assert result.status_code==200,result.text
    assert result.json()['centre_name']==centre.name
    assert c.delete(path,headers=uh).status_code==409
    assert c.patch(path+'/workflow',headers=ah,json={'status':'Collected','weights':[]}).status_code==422
    result=c.patch(path+'/workflow',headers=ah,json={'status':'Collected','weights':[{'item_id':i['id'],'actual_weight':'2.50'} for i in r['items']]}); assert result.status_code==200,result.text
    assert c.patch(path+'/workflow',headers=ah,json={'status':'Recycled'}).status_code==200
    final=c.get(path,headers=uh).json(); assert [h['status'] for h in final['history']]==['Pending','Scheduled','Collected','Recycled']
    d=c.get('/api/dashboard',headers=uh).json()
    assert d['total_requests']==baseline['total_requests']+1 and d['actual_weight']==baseline['actual_weight']+5
    assert d['completed_requests']==baseline['completed_requests']+1
    report=c.get('/api/reports',headers=ah).json()
    row=next(x for x in report['centres'] if x['name']==centre.name)
    assert row['requests']==1 and row['actual_weight']==5

def test_foreign_key_check_constraints_and_rollback(ctx):
    c,db,users,cat,centre,ah,uh=ctx
    r=c.post('/api/requests',headers=uh,json=payload(cat)).json()
    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.add(RequestItem(request_id=r['id'],category_id=2147483647,condition='Working',quantity=1,estimated_weight=1)); db.flush()
    with pytest.raises(OperationalError, match='ck_item_quantity'):
        with db.begin_nested():
            db.add(RequestItem(request_id=r['id'],category_id=cat.id,condition='Working',quantity=0,estimated_weight=1)); db.flush()
    history_count=db.scalar(select(func.count(StatusHistory.id)).where(StatusHistory.request_id==r['id']))
    with patch.object(db,'commit',side_effect=RuntimeError('Injected commit failure')):
        response=c.patch(f"/api/requests/{r['id']}/workflow",headers=ah,json={'status':'Scheduled','centre_id':centre.id,'pickup_date':str(date.today())})
        assert response.status_code==500
    db.expire_all()
    assert db.get(CollectionRequest,r['id']).status=='Pending'
    assert db.scalar(select(func.count(StatusHistory.id)).where(StatusHistory.request_id==r['id']))==history_count

def test_centres_and_delete(ctx):
    c,db,users,cat,centre,ah,uh=ctx
    body={'name':'New '+uuid.uuid4().hex,'address':'55 Fictional Road, Demo City','phone':'5550100200','active':True}
    response=c.post('/api/centres',headers=ah,json=body); assert response.status_code==201
    cid=response.json()['id']; body['active']=False
    assert c.put(f'/api/centres/{cid}',headers=ah,json=body).status_code==200
    r=c.post('/api/requests',headers=uh,json=payload(cat)).json()
    assert c.patch(f"/api/requests/{r['id']}/workflow",headers=ah,json={'status':'Scheduled','centre_id':cid,'pickup_date':str(date.today())}).status_code==422
    assert c.delete(f"/api/requests/{r['id']}",headers=uh).status_code==204
    assert db.scalar(select(func.count(RequestItem.id)).where(RequestItem.request_id==r['id']))==0

def test_validation_and_health(ctx):
    c,db,users,cat,centre,ah,uh=ctx
    assert c.get('/api/health').json()['database']=='MySQL'
    body=payload(cat); body['items'][0]['estimated_weight']=-1
    assert c.post('/api/requests',headers=uh,json=body).status_code==422
    body=payload(cat); body['items'][0]['category_id']=2147483647
    assert c.post('/api/requests',headers=uh,json=body).status_code==422
    body=payload(cat); body['items']=[]
    assert c.post('/api/requests',headers=uh,json=body).status_code==422
    assert c.get('/api/requests?q=%27%20OR%201=1',headers=uh).status_code==200
