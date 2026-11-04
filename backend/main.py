from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, text, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from .database import get_db
from .models import User, Category, Centre, CollectionRequest
from .schemas import Register, Login, CentreInput
from .auth import password_hasher, token_for, current_user, admin, user_dict
from .requests import router as request_router
from .reports import router as report_router

app = FastAPI(title='EcoCollect API',version='1.0.0')
app.include_router(request_router)
app.include_router(report_router)
@app.exception_handler(IntegrityError)
async def integrity_error(request: Request, exc):
    return JSONResponse(status_code=409,content={'detail':'This record conflicts with existing data. Check duplicate names or email addresses.'})
@app.exception_handler(OperationalError)
async def database_error(request: Request, exc):
    if exc.orig.args[0] == 3819:
        return JSONResponse(status_code=422,content={'detail':'A database constraint rejected this value.'})
    return JSONResponse(status_code=503,content={'detail':'MySQL is unavailable. Start the database and check the backend .env configuration.'})
@app.get('/api/health')
def health(db: Session = Depends(get_db)):
    db.execute(text('SELECT 1'))
    return {'status':'ok','database':'MySQL'}
@app.post('/api/auth/register',status_code=201)
def register(data: Register,db: Session = Depends(get_db)):
    user=User(name=data.name,email=str(data.email).lower(),password_hash=password_hasher.hash(data.password),role='user')
    db.add(user); db.commit()
    return {'token':token_for(user),'user':user_dict(user)}
@app.post('/api/auth/login')
def login(data: Login,db: Session = Depends(get_db)):
    user=db.scalar(select(User).where(User.email==str(data.email).lower()))
    if not user or not password_hasher.verify(data.password,user.password_hash):
        raise HTTPException(401,'Email or password is incorrect.')
    return {'token':token_for(user),'user':user_dict(user)}
@app.get('/api/auth/me')
def me(user: User = Depends(current_user)):
    return user_dict(user)
@app.get('/api/categories')
def categories(db: Session = Depends(get_db),user: User = Depends(current_user)):
    return [{'id':c.id,'name':c.name} for c in db.scalars(select(Category).order_by(Category.id))]
@app.get('/api/centres')
def centres(db: Session = Depends(get_db),user: User = Depends(admin)):
    rows=db.execute(select(Centre,func.count(CollectionRequest.id)).outerjoin(CollectionRequest,CollectionRequest.centre_id==Centre.id).group_by(Centre.id)).all()
    return [{'id':c.id,'name':c.name,'address':c.address,'phone':c.phone,'active':c.active,'request_count':n} for c,n in rows]
@app.post('/api/centres',status_code=201)
def add_centre(data: CentreInput,db: Session = Depends(get_db),user: User = Depends(admin)):
    centre=Centre(**data.model_dump()); db.add(centre); db.commit()
    return {'id':centre.id}
@app.put('/api/centres/{centre_id}')
def edit_centre(centre_id: int,data: CentreInput,db: Session = Depends(get_db),user: User = Depends(admin)):
    centre=db.get(Centre,centre_id)
    if not centre: raise HTTPException(404,'Centre not found.')
    for k,v in data.model_dump().items(): setattr(centre,k,v)
    db.commit(); return {'id':centre.id}
@app.delete('/api/requests/{request_id}',status_code=204)
def delete_pending(request_id: int,db: Session = Depends(get_db),user: User = Depends(current_user)):
    from .requests import get_request
    r=get_request(db,request_id,user,lock=True)
    if r.status!='Pending': raise HTTPException(409,'Only pending requests can be deleted.')
    db.delete(r); db.commit()
