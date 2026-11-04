
import os
import ssl
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

url = URL.create(
    "mysql+pymysql",
    username=os.getenv("DB_USER", "ecocollect"),
    password=os.getenv("DB_PASSWORD", ""),
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "ecocollect"),
    query={"charset": "utf8mb4"},
)

connect_args = {}

ca_path = os.getenv("DB_SSL_CA")

if ca_path:
    ssl_context = ssl.create_default_context(cafile=ca_path)
    ssl_context.check_hostname = True
    connect_args["ssl"] = ssl_context

engine = create_engine(
    url,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as db:
        try:
            yield db
        except Exception:
            db.rollback()
            raise
