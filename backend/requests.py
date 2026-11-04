from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session, selectinload
from .database import get_db
from .models import CollectionRequest, RequestItem, StatusHistory, Category, Centre, User
from .schemas import RequestInput, WorkflowInput
from .auth import current_user, admin

router = APIRouter(prefix='/api/requests', tags=['Collection requests'])
def serialize(r):
    return {'id':r.id, 'user_name':r.user.name,'address':r.address,'status':r.status,'pickup_date':r.pickup_date,'created_at':r.created_at,'centre_id':r.centre_id,'centre_name':r.centre.name if r.centre else None,
        'items':[{'id':i.id,'category_id':i.category_id,'category':i.category.name,'condition':i.condition,'quantity':i.quantity,'estimated_weight':float(i.estimated_weight),'actual_weight':float(i.actual_weight) if i.actual_weight is not None else None} for i in r.items],
        'history':[{'status':h.status,'changed_at':h.changed_at,'note':h.note} for h in r.history]}
def get_request(db, request_id, user, lock=False):
    stmt = select(CollectionRequest).where(CollectionRequest.id == request_id)
    if lock:
        stmt = stmt.with_for_update()
    r = db.scalar(stmt)
    if not r or (user.role != 'admin' and r.user_id != user.id):
        raise HTTPException(404, 'Collection request not found.')
    return r
@router.get('')
def list_requests(status: str | None = None, q: str = '', centre_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    stmt = select(CollectionRequest).join(User).options(selectinload(CollectionRequest.items).selectinload(RequestItem.category),selectinload(CollectionRequest.history),selectinload(CollectionRequest.centre),selectinload(CollectionRequest.user))
    if user.role != 'admin': stmt = stmt.where(CollectionRequest.user_id == user.id)
    if status: stmt = stmt.where(CollectionRequest.status == status)
    if centre_id: stmt = stmt.where(CollectionRequest.centre_id == centre_id)
    if q: stmt = stmt.where(or_(CollectionRequest.address.contains(q, autoescape=True), User.name.contains(q, autoescape=True), CollectionRequest.id == (int(q) if q.isdigit() else -1)))
    return [serialize(r) for r in db.scalars(stmt.order_by(CollectionRequest.created_at.desc(), CollectionRequest.id.desc())).all()]
@router.post('', status_code=201)
def create_request(data: RequestInput, db: Session = Depends(get_db), user: User = Depends(current_user)):
    ids = {i.category_id for i in data.items}
    if set(db.scalars(select(Category.id).where(Category.id.in_(ids)))) != ids:
        raise HTTPException(422, 'Choose valid item categories.')
    r = CollectionRequest(user_id=user.id,address=data.address,items=[RequestItem(**i.model_dump()) for i in data.items])
    r.history.append(StatusHistory(status='Pending',changed_by=user.id,note='Collection request submitted.'))
    db.add(r)
    db.commit()
    return serialize(r)
@router.get('/{request_id}')
def detail(request_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return serialize(get_request(db,request_id,user))
@router.patch('/{request_id}/workflow')
def workflow(request_id: int, data: WorkflowInput, db: Session = Depends(get_db), user: User = Depends(admin)):
    r = get_request(db,request_id,user,lock=True)
    expected = {'Pending':'Scheduled','Scheduled':'Collected','Collected':'Recycled'}.get(r.status)
    if data.status != expected:
        raise HTTPException(409, 'Invalid transition. Follow Pending → Scheduled → Collected → Recycled.')
    if data.status == 'Scheduled':
        centre = db.get(Centre,data.centre_id) if data.centre_id else None
        if not centre or not centre.active or not data.pickup_date or data.pickup_date < date.today():
            raise HTTPException(422, 'Choose an active centre and a pickup date today or later.')
        r.centre_id, r.pickup_date = centre.id, data.pickup_date
    elif data.status == 'Collected':
        weights = {w.item_id:w.actual_weight for w in data.weights}
        if len(weights) != len(data.weights) or set(weights) != {i.id for i in r.items}:
            raise HTTPException(422, 'Provide one actual weight for every item row.')
        for item in r.items: item.actual_weight = weights[item.id]
    r.status = data.status
    r.history.append(StatusHistory(status=data.status,changed_by=user.id,note=data.note or f'Request marked {data.status.lower()}.'))
    db.commit()
    return serialize(r)
