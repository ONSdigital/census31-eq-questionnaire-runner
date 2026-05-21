from datetime import datetime, timedelta, timezone

import pytest
import fakeredis
from dateutil.tz import tzutc
from pytest import fixture

from app.data_models.app_models import EQSession
from app.setup import create_app
from app.storage.redis import Redis

NOW = datetime.now(tz=tzutc()).replace(microsecond=0)


@fixture
def app():
    setting_overrides = {"LOGIN_DISABLED": True}
    the_app = create_app(setting_overrides=setting_overrides)

    return the_app


@fixture
def fake_eq_session():
    eq_session = EQSession(
        eq_session_id="sessionid",
        user_id="someuser",
        session_data="somedata",
        expires_at=NOW + timedelta(minutes=1),
    )

    return eq_session


@pytest.fixture(name="redis_client")
def mock_redis_client():
    return fakeredis.FakeStrictRedis()


@pytest.fixture
def redis(redis_client):
    return Redis(redis_client)


@pytest.fixture
def eq_session():
    return EQSession(
        eq_session_id="sessionid",
        user_id="someuser",
        session_data="somedata",
        expires_at=datetime.now(tz=timezone.utc).replace(microsecond=0)
        + timedelta(minutes=1),
    )
