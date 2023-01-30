import datetime
import os

from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Get MariaDB connection details from environment variables
DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]

# Replace with your MariaDB connection string
DATABASE_URL = f'mariadb://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}'

Base = declarative_base()


class InternetStatus(Base):
    __tablename__ = "internet_status"

    id = Column(Integer, primary_key=True, index=True)
    internet = Column(String(50), index=True)
    dns = Column(String(50), index=True)
    firewall = Column(String(50), index=True)
    nas = Column(String(50), index=True)
    ifconfig_me = Column(String(1000))
    created_at = Column(DateTime, default=datetime.datetime.now)


class AnaReport(Base):
    __tablename__ = "ana_report"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    pop = Column(Boolean, nullable=False, default=False)
    pee = Column(Boolean, nullable=False, default=False)
    eat = Column(Boolean, nullable=False, default=False)
    eat_quality = Column(Integer, nullable=True, default=0)
    sleep_time = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now)


# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# create table
Base.metadata.create_all(bind=engine)

# Create a SQLAlchemy session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def check_save_to_database(internet, dns, firewall, nas, ifconfig_me):
    # Get a new session
    session = SessionLocal()

    # Create a new InternetStatus object
    internet_status = InternetStatus(
        internet=internet,
        dns=dns,
        firewall=firewall,
        nas=nas,
        ifconfig_me=ifconfig_me
    )

    # Add the object to the session
    session.add(internet_status)

    # Commit the transaction
    session.commit()

    # Close the session
    session.close()


def ana_save_to_database(poop, pee, eat, eat_quality, sleep_time):
    # Get a new session
    session = SessionLocal()

    # Create a new InternetStatus object
    ana_report = AnaReport(
        poop=poop,
        pee=pee,
        eat=eat,
        eat_quality=eat_quality,
        sleep_time=sleep_time,
    )

    # Add the object to the session
    session.add(ana_report)

    # Commit the transaction
    session.commit()

    # Close the session
    session.close()
