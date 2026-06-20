AstroLogicAI backend migration scaffold.

Current deployment can continue importing the legacy root `main:app`.
New deployment targets may use `backend.app.main:app`, which delegates to the
legacy app while modules are migrated gradually.

Migration order:
1. Keep legacy imports working through compatibility shims.
2. Move database/session/config/security into `backend/app`.
3. Move models and schemas behind shims.
4. Split routes from `api/api.py` into `backend/app/api/v1`.
5. Move business logic into `backend/app/services`.
6. Replace direct SQLAlchemy access in routes with repositories.
7. Move astrology and AI engines last, after route/service parity tests exist.
