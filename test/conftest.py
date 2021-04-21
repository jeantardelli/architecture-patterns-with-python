# pylint: disable=redefined-outer-name
import time
import pytest
import requests
import config

from requests.exceptions import ConnectionError
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, clear_mappers
from orm import metadata, start_mappers

@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)

    return engine

@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()

def wait_for_mysql_to_come_up(engine):
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("MySQL never came up")

def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")

@pytest.fixture(scope="session")
def mysql_db():
    engine = create_engine(config.get_mysql_uri())
    wait_for_mysql_to_come_up(engine)
    metadata.create_all(engine)

    return engine

@pytest.fixture
def mysql_session(mysql_db):
    start_mappers()
    yield sessionmaker(bind=mysql_db)()
    clear_mappers()

@pytest.fixture
def add_stock(mysql_session):
    batches_added = set()
    skus_added = set()

    def _add_stock(lines):
        for ref, sku, qty, eta in lines:
            mysql_session.execute(
                "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
                " VALUES (:ref, :sku, :qty, :eta)",
                dict(ref=ref, sku=sku, qty=qty, eta=eta),)
            [[batch_id]] = mysql_session.execute(
                "SELECT id FROM batches WHERE reference=:ref AND sku=:sku",
                dict(ref=ref, sku=sku),)
            batches_added.add(batch_id)
            skus_added.add(sku)
        mysql_session.commit()

    yield _add_stock

    for batch_id in batches_added:
        mysql_session.execute(
            "DELETE FROM allocations WHERE batch_id=@batch_id",
            dict(batch_id=batch_id),)
        mysql_session.execute(
            "DELETE FROM batches WHERE id=@batch_id", dict(batch_id=batch_id),)

    for sku in skus_added:
        mysql_session.execute(
            "DELETE FROM order_lines WHERE sku=@sku", dict(sku=sku),)
        mysql_session.commit()

@pytest.fixture
def restart_api():
    (Path(__file__).parent / "flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
