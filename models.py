import os
import datetime
from datetime import timedelta

from sqlalchemy import (Boolean, Column, DateTime, Integer, String,
                        create_engine)
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
    poop = Column(Boolean, nullable=False, default=False)
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


def ana_report():
    # Get a new session
    session = SessionLocal()

    # Query the database
    results = session.query(AnaReport).all()

    # Close the session
    session.close()

    return results


def ana_create_report():
    # Get a new session
    session = SessionLocal()

    # Query the database
    data = session.query(AnaReport).filter(AnaReport.created_at >= (
        datetime.datetime.now() - datetime.timedelta(days=1))).all()

    # Close the session
    session.close()

    # Initialize variables to keep track of the count and sum of values
    poop_count = pee_count = eat_count = 0
    sleep_time = 0
    eat_quality = 0
    last_poop = last_pee = last_eat = last_sleep = "Never happened."

    # Loop over the list of objects and retrieve the necessary data
    for report in data:
        if report.poop:
            poop_count += 1
            last_poop = report.created_at.strftime("%Y-%m-%d %H:%M:%S")
        if report.pee:
            pee_count += 1
            last_pee = report.created_at.strftime("%Y-%m-%d %H:%M:%S")
        sleep_time += report.sleep_time
        if report.eat:
            eat_count += 1
            eat_quality += report.eat_quality
            last_eat = report.created_at.strftime("%Y-%m-%d %H:%M:%S")
        if report.sleep_time:
            last_sleep = report.created_at.strftime("%Y-%m-%d %H:%M:%S")

    # Format the results string
    results = (f"In the last 24 hours, Ana has: \n"
               f"- Pooped {poop_count} times (Last at: {last_poop})\n"
               f"- Peed {pee_count} times (Last at: {last_pee})\n"
               f"- Slept for {sleep_time} hours (Last at: {last_sleep})\n"
               f"- Eaten {eat_count} times (Last at: {last_eat})\n"
               f"- She has eaten in both breasts {eat_quality/2} times.")
    return results
