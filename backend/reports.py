from fastapi import APIRouter, Depends
from sqlalchemy import select, func, distinct
from sqlalchemy.orm import Session
from .database import get_db
from .auth import current_user, admin
from .models import CollectionRequest as R, RequestItem as I, Category, Centre, User

router = APIRouter(prefix='/api',tags=['Reports'])
def summary(db,user):
    scope = [] if user.role == 'admin' else [R.user_id == user.id]
    statuses = dict(db.execute(select(R.status,func.count(R.id)).where(*scope).group_by(R.status)).all())
    weights = db.execute(select(func.coalesce(func.sum(I.actual_weight),0),func.coalesce(func.sum(I.estimated_weight),0)).join(R,I.request_id==R.id).where(*scope)).one()
    cats = db.execute(select(Category.name,func.sum(I.estimated_weight),func.coalesce(func.sum(I.actual_weight),0),func.sum(I.quantity)).join(I,I.category_id==Category.id).join(R,R.id==I.request_id).where(*scope).group_by(Category.id,Category.name).order_by(func.sum(I.estimated_weight).desc())).all()
    return {'total_requests':sum(statuses.values()),'pending_requests':statuses.get('Pending',0),'completed_requests':statuses.get('Recycled',0),'collected_requests':statuses.get('Collected',0)+statuses.get('Recycled',0),'actual_weight':float(weights[0]),'estimated_weight':float(weights[1]),'total_users':db.scalar(select(func.count(User.id)).where(User.role=='user')) if user.role=='admin' else None,'active_centres':db.scalar(select(func.count(Centre.id)).where(Centre.active==True)), 'statuses':[{'name':s,'value':statuses.get(s,0)} for s in ['Pending','Scheduled','Collected','Recycled']], 'categories':[{'name':a,'estimated_weight':float(b),'actual_weight':float(c),'quantity':int(d)} for a,b,c,d in cats]}
@router.get('/dashboard')
def dashboard(db: Session = Depends(get_db),user: User = Depends(current_user)):
    return summary(db,user)
@router.get('/reports')
def reports(db: Session = Depends(get_db),user: User = Depends(admin)):
    data=summary(db,user)
    # Aggregate items before joining centres to avoid multiplying request counts.
    item_totals=select(I.request_id,func.sum(I.actual_weight).label('weight')).group_by(I.request_id).subquery()
    rows=db.execute(select(Centre.name,func.count(R.id),func.coalesce(func.sum(item_totals.c.weight),0)).outerjoin(R,R.centre_id==Centre.id).outerjoin(item_totals,R.id==item_totals.c.request_id).group_by(Centre.id,Centre.name)).all()
    data['centres']=[{'name':n,'requests':c,'actual_weight':float(w)} for n,c,w in rows]
    return data
