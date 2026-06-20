from app.database.base import Base, import_models
from app.database.session import engine


def init_db() -> None:
    """Create tables for local bootstrap only.

    Production deployments should use Alembic migrations instead of calling
    this function at application startup.
    """
    import_models()
    Base.metadata.create_all(bind=engine)
