from sqlalchemy import create_engine


import config

engine_config = f'{config.DB_DATABASE_TYPE}://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:5432/{config.DB_DATABASE}'
engine = create_engine(engine_config, echo=True)