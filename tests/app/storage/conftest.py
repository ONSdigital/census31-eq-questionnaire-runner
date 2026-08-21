import contextlib
from datetime import datetime, timedelta, timezone

import fakeredis
import pytest

from app.data_models.app_models import EQSession, QuestionnaireState
from app.storage.encrypted_questionnaire_storage import EncryptedQuestionnaireStorage
from app.storage.redis import Redis


@pytest.fixture
def mock_client(mocker):
    client = mocker.Mock()
    client.transaction.return_value = contextlib.suppress()
    return client


@pytest.fixture
def encrypted_storage():
    return EncryptedQuestionnaireStorage("user_id", "user_ik", "pepper")


@pytest.fixture(name="redis_client")
def mock_redis_client():
    return fakeredis.FakeStrictRedis()


@pytest.fixture
def redis(redis_client):
    return Redis(redis_client)


@pytest.fixture
def questionnaire_state():
    return QuestionnaireState("someuser", "data", "ce_sid", 1)


@pytest.fixture
def eq_session():
    return EQSession(
        eq_session_id="sessionid",
        user_id="someuser",
        session_data="somedata",
        expires_at=datetime.now(tz=timezone.utc).replace(microsecond=0) + timedelta(minutes=1),
    )
