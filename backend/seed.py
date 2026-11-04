from datetime import timedelta, date
from sqlalchemy import select
from .database import SessionLocal
from .models import User, Category, Centre, CollectionRequest, RequestItem, StatusHistory, now
from .auth import password_hasher
from .demo_locations import collection_address, CENTRE_ADDRESSES

def seed():
    with SessionLocal.begin() as db:
        if db.scalar(select(User.id).limit(1)):
            print('Seed skipped: users already exist. Existing data preserved.'); return
        people=[User(name=n,email=e,password_hash=password_hasher.hash(p),role=r) for n,e,p,r in [
            ('Romit Singh','admin@example.com','EcoAdmin123!','admin'),
            ('Soumyajit Mandal','soumyajit@example.com','EcoUser123!','user'),
            ('Sourja Sinha','sourja@example.com','EcoUser123!','user'),
            ('Harsh Kumar Jha','harsh@example.com','EcoUser123!','user'),
            ('Sayandip Rout','sayandip@example.com','EcoUser123!','user'),
            ('Aditya Chaubey','aditya@example.com','EcoUser123!','user')]]
        from .init_db import CATEGORY_NAMES
        categories=[]
        for name in CATEGORY_NAMES:
            category=db.scalar(select(Category).where(Category.name==name))
            categories.append(category or Category(name=name))
        centres=[Centre(name=n,address=a,phone=p) for n,a,p in [('GreenLoop Recycling','12, Park Street, Kolkata','080-5550-0101'),('CircuitCycle Hub','48, Salt Lake, Kolkata','080-5550-0102'),('EarthFirst Recovery','7, Howrah, West Bengal','080-5550-0103')]]
        db.add_all(people+categories+centres); db.flush()
        stages=['Pending','Scheduled','Collected','Recycled']
        for k in range(18):
            stage=k%4; created=now()-timedelta(days=22-k)
            r=CollectionRequest(user_id=people[1+k%(len(people)-1)].id,address=collection_address(k),status=stages[stage],created_at=created,centre_id=centres[k%3].id if stage else None,pickup_date=(date.today()+timedelta(days=1+k%3) if stage==1 else created.date()+timedelta(days=1)) if stage else None)
            for j in range(1+k%2):
                weight=round(1.25+(k+j)%7*1.7,2)
                r.items.append(RequestItem(category_id=categories[(k+j)%7].id,condition=['Working','Damaged','Non-functional'][(k+j)%3],quantity=1+(k+j)%3,estimated_weight=weight,actual_weight=round(weight*.92,2) if stage>=2 else None))
            for s in range(stage+1):
                r.history.append(StatusHistory(status=stages[s],changed_by=people[1+k%(len(people)-1)].id if s==0 else people[0].id,changed_at=created+timedelta(hours=12*s),note='Fictional demonstration record.'))
            db.add(r)
    print('Seeded 18 requests, 6 demo accounts, 7 categories and 3 centres.')
if __name__=='__main__': seed()
