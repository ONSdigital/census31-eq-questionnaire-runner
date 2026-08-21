from datetime import datetime, timedelta, timezone

import pytest

from app.data_models import QuestionnaireStore
from app.questionnaire.questionnaire_schema import QuestionnaireSchema
from app.views.handlers.view_submitted_response import ViewSubmittedResponse, ViewSubmittedResponseNotEnabled
from tests.app.views.handlers.conftest import set_storage_data


def test_not_enabled(storage, language):
    set_storage_data(storage)
    questionnaire_store = QuestionnaireStore(storage)

    with pytest.raises(ViewSubmittedResponseNotEnabled):
        ViewSubmittedResponse(QuestionnaireSchema({}), questionnaire_store, language)


def test_has_expired_no_submitted_at_return_false(storage, language, app):
    with app.app_context():
        set_storage_data(storage)
        questionnaire_store = QuestionnaireStore(storage)
        schema = QuestionnaireSchema({"post_submission": {"view_response": True}})
        view_submitted_response = ViewSubmittedResponse(schema, questionnaire_store, language)
        assert view_submitted_response.has_expired is False


def test_has_expired_with_expired_submitted_at_return_true(storage, language, app):
    with app.app_context():
        submitted_at = datetime.now(timezone.utc) - timedelta(minutes=46)
        set_storage_data(storage, submitted_at=submitted_at)
        questionnaire_store = QuestionnaireStore(storage)
        schema = QuestionnaireSchema({"post_submission": {"view_response": True}})
        view_submitted_response = ViewSubmittedResponse(schema, questionnaire_store, language)

        assert view_submitted_response.has_expired is True


def test_has_expired_with_recent_submitted_at_return_false(storage, language, app):
    with app.app_context():
        submitted_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        set_storage_data(storage, submitted_at=submitted_at)
        questionnaire_store = QuestionnaireStore(storage)
        schema = QuestionnaireSchema({"post_submission": {"view_response": True}})
        view_submitted_response = ViewSubmittedResponse(schema, questionnaire_store, language)

        assert view_submitted_response.has_expired is False
