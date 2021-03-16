from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker

import config
from models import DiscordUser

engine_config = f'{config.DB_DATABASE_TYPE_1}://{config.DB_USER_1}:{config.DB_PASSWORD_1}@{config.DB_HOST_1}:{config.DB_PORT_1}/{config.DB_DATABASE_1}'
engine = create_engine(engine_config, echo=False)
Session = sessionmaker(bind=engine)


def discord_user_create(check_user):
    """Check if user exist"""
    try:
        session = Session()
        user_status = session.query(exists().where(DiscordUser.member_id == check_user.member_id)).scalar()
        print(f"New connection was created")
    except:
        print(f"Cant created connect to db, user was not create{check_user}")

        """If new user -> creat"""
    if user_status:
        print(f"User already {check_user.member_name} exists.")

    if not user_status and session:
        session.add(check_user)
        try:
            session.commit()
            print(f"User {check_user} was create in db")
        except:
            print(f"User {check_user} was not create in db")
            session.rollback()
            raise
        finally:
            session.close()
            print(f"Session close.")


def add_time_log(record):
    session = Session()
    session.add(record)
    try:
        session.commit()
    except:
        print(f"{record}--ERROR")
        session.rollback()
        raise
    finally:
        session.close()
