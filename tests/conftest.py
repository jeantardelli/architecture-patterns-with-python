import shutil
import subprocess
import time
from pathlib import Path

import pytest
import redis
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from tenacity import retry, stop_after_delay

from allocation.adapters.orm import metadata, start_mappers
from allocation import config

pytest.register_assert_rewrite("tests.e2e.api_client")

@pytest.fixture
def in_memory_sqlite_db():
    engine = create_engine("sqlite:///:memory:",
                           echo=True,
                           connect_args={"check_same_thread": False})
    metadata.create_all(engine)

    return engine

@pytest.fixture
def sqlite_session_factory(in_memory_sqlite_db):
    yield sessionmaker(bind=in_memory_sqlite_db)

@pytest.fixture
def mappers():
    start_mappers()
    yield
    clear_mappers()

@retry(stop=stop_after_delay(15))
def wait_for_mysql_to_come_up(engine):
    return engine.connect()

@retry(stop=stop_after_delay(15))
def wait_for_webapp_to_come_up():
    url = config.get_api_url()
    return requests.get(url)

@retry(stop=stop_after_delay(30))
def wait_for_redis_to_come_up():
    r = redis.Redis(**config.get_redis_host_and_port())
    return r.ping()

@pytest.fixture(scope="session")
def mysql_db():
    engine = create_engine(config.get_mysql_uri())
    wait_for_mysql_to_come_up(engine)
    metadata.create_all(engine)

    return engine

@pytest.fixture
def mysql_session_factory(mysql_db):
    yield sessionmaker(bind=mysql_db)

@pytest.fixture
def mysql_session(mysql_session_factory):
    return mysql_session_factory()

@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/allocation/entrypoints/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()

@pytest.fixture
def restart_redis_pubsub():
    wait_for_redis_to_come_up()
    if not shutil.which("docker-compose"):
        print("skipping restart, assumes running in container")
        return
    subprocess.run(
        ["docker-compose", "restart", "-t", "0", "redis_pubsub"],
        check=True,
    )
