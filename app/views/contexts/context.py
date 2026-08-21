from abc import ABC

from app.data_models.data_stores import DataStores
from app.questionnaire.placeholder_renderer import PlaceholderRenderer
from app.questionnaire.questionnaire_schema import QuestionnaireSchema
from app.questionnaire.router import Router


class Context(ABC):
    def __init__(
        self,
        language: str,
        schema: QuestionnaireSchema,
        data_stores: DataStores,
    ) -> None:
        self._language = language
        self._schema = schema
        self._data_stores = data_stores

        self._router = Router(schema=self._schema, data_stores=self._data_stores)

        self._placeholder_renderer = PlaceholderRenderer(
            data_stores=data_stores,
            language=self._language,
            schema=self._schema,
        )
