from sqlalchemy.schema import CreateTable, CreateIndex
from pathlib import Path
from .database import engine, Base
from . import models
from sqlalchemy import select
from .database import SessionLocal

CATEGORY_NAMES = ['Mobile phones','Laptops','Computers','Televisions','Printers','Batteries','Other electronics']

def initialize():
    Base.metadata.create_all(engine)
    with SessionLocal.begin() as db:
        existing = set(db.scalars(select(models.Category.name)))
        db.add_all(models.Category(name=name) for name in CATEGORY_NAMES if name not in existing)

def export_schema():
    statements = ['-- EcoCollect | MySQL 8.4 | InnoDB / utf8mb4', 'CREATE DATABASE IF NOT EXISTS ecocollect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;', 'USE ecocollect;']
    for table in Base.metadata.sorted_tables:
        statements.append(str(CreateTable(table).compile(engine)).strip() + ' ENGINE=InnoDB;')
        statements.extend(str(CreateIndex(i).compile(engine))+';' for i in table.indexes)
    Path('database/schema.sql').write_text('\n\n'.join(statements)+'\n',encoding='utf-8')
if __name__ == '__main__':
    export_schema()
    initialize()
    print('MySQL tables initialized. Run python -m backend.seed to load fictional demonstration data.')
