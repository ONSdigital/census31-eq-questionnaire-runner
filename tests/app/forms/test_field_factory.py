import pytest

from app.data_models.data_stores import DataStores
from app.forms import error_messages
from app.forms.field_handlers import get_field_handler
from app.questionnaire import QuestionnaireSchema
from app.questionnaire.rules.rule_evaluator import RuleEvaluator
from app.questionnaire.value_source_resolver import ValueSourceResolver


def test_invalid_field_type_raises_on_invalid():
    schema = QuestionnaireSchema(
        {
            "questionnaire_flow": {
                "type": "Linear",
                "options": {"summary": {"collapsible": False}},
            }
        }
    )

    metadata = {}

    value_source_resolver = ValueSourceResolver(
        data_stores=DataStores(metadata=metadata, response_metadata={}),
        schema=schema,
        location=None,
        list_item_id=None,
        escape_answer_values=False,
    )

    rule_evaluator = RuleEvaluator(
        data_stores=DataStores(),
        schema=schema,
        location=None,
    )

    # Given
    invalid_field_type = "Football"
    # When / Then
    with pytest.raises(KeyError):
        get_field_handler(
            answer_schema={"type": invalid_field_type},
            value_source_resolver=value_source_resolver,
            rule_evaluator=rule_evaluator,
            error_messages=error_messages,
        )
