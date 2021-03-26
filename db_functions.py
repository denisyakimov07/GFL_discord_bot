import os

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker


from models import DiscordUser

from dotenv import load_dotenv
load_dotenv()

MYSQL_STRING = os.getenv("MYSQL_STRING")

engine_config = MYSQL_STRING
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
            print(f"Session close (discord_user_create).")


def add_record_log(record):
    try:
        session = Session()
        print(f"New connection was created")
    except:
        print(f"Cant created connect to db.")
    if session:
        session.add(record)
        try:
            session.commit()
            print(f"New log added.")
        except:
            print(f"New record {record} was not added.")
            session.rollback()
            raise
        finally:
            session.close()
            print(f"Session close (add_record_log).")



