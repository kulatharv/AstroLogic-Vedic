AstroLogicAI/
│
├── frontend/                         ← Empty for now (Next.js later)
│
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── main.py                  ← current main.py
│   │   │
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── constants.py
│   │   │   └── logger.py
│   │   │
│   │   │
│   │   ├── api/                     ← current api/
│   │   │   ├── api.py
│   │   │   ├── blogs.py
│   │   │   ├── horoscope_routes.py
│   │   │   └── schemas/
│   │   │
│   │   │
│   │   ├── auth/
│   │   │   ├── auth_routes.py
│   │   │   ├── jwt_handler.py
│   │   │   ├── auth_service.py
│   │   │   ├── password_handler.py
│   │   │   └── dependencies.py
│   │   │
│   │   │
│   │   ├── astro_engine/            ← current astro_engine/
│   │   │   │
│   │   │   ├── calculations/
│   │   │   │
│   │   │   ├── charts/
│   │   │   │   ├── chart_engine.py
│   │   │   │   ├── kundali_engine.py
│   │   │   │   └── navamsa.py
│   │   │   │
│   │   │   ├── dasha/
│   │   │   │   ├── dasha.py
│   │   │   │   └── dasha_activation.py
│   │   │   │
│   │   │   ├── prediction/
│   │   │   │   ├── prediction_engine.py
│   │   │   │   ├── horoscope_engine.py
│   │   │   │   ├── event_engine.py
│   │   │   │   └── domain_engine.py
│   │   │   │
│   │   │   ├── strengths/
│   │   │   │   ├── shadbala.py
│   │   │   │   ├── strength_eval.py
│   │   │   │   └── functional_nature.py
│   │   │   │
│   │   │   ├── yogas/
│   │   │   │
│   │   │   ├── transits/
│   │   │   │
│   │   │   ├── houses/
│   │   │   │
│   │   │   ├── divisional/
│   │   │   │
│   │   │   ├── datasets/
│   │   │   │
│   │   │   └── utils/
│   │   │
│   │   │
│   │   ├── ai_engine/               ← current ai_layer/
│   │   │   ├── llm_service.py
│   │   │   ├── prompt_builder.py
│   │   │   ├── rag_service.py
│   │   │   ├── prompts/
│   │   │   ├── embeddings/
│   │   │   ├── memory/
│   │   │   └── providers/
│   │   │
│   │   │
│   │   ├── rule_engine/             ← current rule_engine/
│   │   │   ├── predictor.py
│   │   │   ├── rules.py
│   │   │   ├── strength.py
│   │   │   └── confidence.py
│   │   │
│   │   │
│   │   ├── services/                ← current services/
│   │   │   ├── horoscope_service.py
│   │   │   ├── user_service.py
│   │   │   ├── prediction_service.py
│   │   │   └── ai_service.py
│   │   │
│   │   │
│   │   ├── models/                  ← current models/
│   │   │   ├── user_model.py
│   │   │   ├── blog_model.py
│   │   │   ├── kundali_model.py
│   │   │   ├── feedback_model.py
│   │   │   └── activity_model.py
│   │   │
│   │   │
│   │   ├── schemas/                 ← current schemas/
│   │   │   ├── chart_schema.py
│   │   │   ├── auth_schema.py
│   │   │   ├── user_schema.py
│   │   │   └── feedback_schema.py
│   │   │
│   │   │
│   │   ├── database/                ← current database/
│   │   │   ├── db.py
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   │
│   │   │
│   │   ├── middleware/
│   │   │   ├── auth_middleware.py
│   │   │   ├── activity_middleware.py
│   │   │   └── logging_middleware.py
│   │   │
│   │   │
│   │   ├── utils/                   ← current utils/
│   │   │   ├── helpers.py
│   │   │   ├── validators.py
│   │   │   └── date_utils.py
│   │   │
│   │   │
│   │   ├── templates/               ← KEEP TEMPORARILY
│   │   │
│   │   └── static/                  ← KEEP TEMPORARILY
│   │
│   │
│   ├── tests/
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env
│   └── alembic.ini
│
│
├── docs/
│
├── docker-compose.yml
│
├── README.md
│
└── .gitignore