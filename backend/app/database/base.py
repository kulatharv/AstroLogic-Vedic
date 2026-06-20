from sqlalchemy.orm import declarative_base


Base = declarative_base()


def import_models() -> None:
    """Import all SQLAlchemy models so Alembic sees complete metadata."""
    from app.models import blog_model, user_model  # noqa: F401
