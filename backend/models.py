from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Numeric, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from .database import Base

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(254), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False, default='user')
    created_at = Column(DateTime, nullable=False, default=now)
    __table_args__ = (CheckConstraint("role IN ('user','admin')", name='ck_user_role'),)

class Category(Base):
    __tablename__ = 'ewaste_categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

class Centre(Base):
    __tablename__ = 'recycling_centres'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    address = Column(String(500), nullable=False)
    phone = Column(String(30), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

class CollectionRequest(Base):
    __tablename__ = 'collection_requests'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    centre_id = Column(Integer, ForeignKey('recycling_centres.id', ondelete='RESTRICT'), index=True)
    address = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default='Pending', index=True)
    pickup_date = Column(Date)
    created_at = Column(DateTime, nullable=False, default=now)
    user = relationship(User)
    centre = relationship(Centre)
    items = relationship('RequestItem', cascade='all, delete-orphan', order_by='RequestItem.id')
    history = relationship('StatusHistory', cascade='all, delete-orphan', order_by='StatusHistory.id')
    __table_args__ = (CheckConstraint("status IN ('Pending','Scheduled','Collected','Recycled')", name='ck_request_status'), CheckConstraint("status = 'Pending' OR (centre_id IS NOT NULL AND pickup_date IS NOT NULL)", name='ck_request_schedule'))

class RequestItem(Base):
    __tablename__ = 'request_items'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('collection_requests.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('ewaste_categories.id', ondelete='RESTRICT'), nullable=False)
    condition = Column(String(20), nullable=False)
    quantity = Column(Integer, nullable=False)
    estimated_weight = Column(Numeric(10,2), nullable=False)
    actual_weight = Column(Numeric(10,2))
    category = relationship(Category)
    __table_args__ = (CheckConstraint('quantity > 0', name='ck_item_quantity'), CheckConstraint('estimated_weight > 0', name='ck_estimated_weight'), CheckConstraint('actual_weight IS NULL OR actual_weight > 0', name='ck_actual_weight'), CheckConstraint("`condition` IN ('Working','Damaged','Non-functional')", name='ck_item_condition'))

class StatusHistory(Base):
    __tablename__ = 'status_history'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('collection_requests.id', ondelete='CASCADE'), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    changed_by = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    changed_at = Column(DateTime, nullable=False, default=now)
    note = Column(String(500), nullable=False, default='')
    __table_args__ = (CheckConstraint("status IN ('Pending','Scheduled','Collected','Recycled')", name='ck_history_status'),)
