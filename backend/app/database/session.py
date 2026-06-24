# from collections.abc import Generator

# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session, sessionmaker

# from ..core.config import settings


# engine = create_engine(
#     settings.database_url,
#     pool_pre_ping=True,
#     pool_size=settings.database_pool_size,
#     max_overflow=settings.database_max_overflow,
#     pool_recycle=settings.database_pool_recycle_seconds,
#     future=True,
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine,
#     class_=Session,
#     expire_on_commit=False,
#     future=True,
# )


# def get_db() -> Generator[Session, None, None]:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()



# from collections.abc import Generator

# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session, sessionmaker

# from ..core.config import settings

# if settings.database_url.startswith("sqlite"):
#     engine = create_engine(
#         settings.database_url,
#         connect_args={"check_same_thread": False},
#         future=True,
#     )
# else:
#     engine = create_engine(
#         settings.database_url,
#         pool_pre_ping=True,
#         pool_size=settings.database_pool_size,
#         max_overflow=settings.database_max_overflow,
#         pool_recycle=settings.database_pool_recycle_seconds,
#         future=True,
#     )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine,
#     class_=Session,
#     expire_on_commit=False,
#     future=True,
# )


# def get_db() -> Generator[Session, None, None]:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()



from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_recycle=settings.database_pool_recycle_seconds,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
    expire_on_commit=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()