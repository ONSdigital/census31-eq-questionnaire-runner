from flask import Blueprint, Response, jsonify, request
from werkzeug.exceptions import BadRequest

from app.questionnaire.questionnaire_schema import DEFAULT_LANGUAGE_CODE
from app.utilities.schema import LANGUAGE_CODES, get_schema_list, load_schema_from_name

schema_blueprint = Blueprint("schema", __name__)


def _get_language_code() -> str:
    language_code = request.args.get("language_code", DEFAULT_LANGUAGE_CODE)

    if language_code not in LANGUAGE_CODES:
        error_message = "language_code must be either 'en' or 'cy'"
        raise BadRequest(error_message)

    return language_code


@schema_blueprint.route("/schemas/<schema_name>", methods=["GET"])
def get_schema_json_from_name(schema_name: str) -> Response | tuple[str, int]:
    try:
        schema = load_schema_from_name(schema_name, language_code=_get_language_code())
        return jsonify(schema.json)
    except FileNotFoundError:
        return "Schema Not Found", 404


@schema_blueprint.route("/schemas", methods=["GET"])
def list_schemas() -> Response:
    return jsonify(get_schema_list(_get_language_code()))
