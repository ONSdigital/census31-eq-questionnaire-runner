import pytest
from flask import Flask, current_app
from flask import session as cookie_session

from app.helpers.template_helpers import ContextHelper, get_survey_config
from app.questionnaire import QuestionnaireSchema
from app.routes.session import set_schema_context_in_cookie
from app.settings import ACCOUNT_SERVICE_BASE_URL, ACCOUNT_SERVICE_BASE_URL_CENSUS, ONS_URL, ONS_URL_CY, read_file
from app.survey_config import (
    CensusSurveyConfig,
    NICensusSurveyConfig,
    NRSCensusSurveyConfig,
    SurveyConfig,
)
from app.survey_config.survey_type import SurveyType
from tests.app.helpers.conftest import (
    expected_footer_census_theme,
    expected_footer_census_theme_no_cookie,
)
from tests.app.questionnaire.conftest import get_metadata

DEFAULT_URL = "http://localhost"


@pytest.mark.parametrize(
    "theme, survey_config, language, expected_footer",
    [
        (
            SurveyType.CENSUS,
            CensusSurveyConfig(),
            "en",
            expected_footer_census_theme("en"),
        ),
        (None, CensusSurveyConfig(), "en", expected_footer_census_theme_no_cookie()),
        (
            SurveyType.CENSUS,
            CensusSurveyConfig(language_code="cy"),
            "cy",
            expected_footer_census_theme("cy"),
        ),
    ],
)
def test_footer_context(app: Flask, theme, survey_config, language, expected_footer):
    with app.app_context():
        if theme:
            cookie_session["theme"] = theme
        config = survey_config

        result = ContextHelper(
            language=language,
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=config,
        ).context["footer"]

    assert result == expected_footer


@pytest.mark.parametrize(
    "theme, survey_title, survey_config, expected",
    (
        (
            SurveyType.CENSUS,
            None,
            CensusSurveyConfig(),
            ["ONS Surveys", None, None, read_file("./templates/assets/images/census-logo.svg"), None],
        ),
        (
            SurveyType.CENSUS,
            "Test",
            CensusSurveyConfig(),
            ["Test", None, None, read_file("./templates/assets/images/census-logo.svg"), None],
        ),
        (
            SurveyType.CENSUS,
            "Test",
            CensusSurveyConfig(language_code="cy"),
            ["Test", None, None, read_file("./templates/assets/images/census-logo-cy-small.svg"), None],
        ),
        (
            None,
            None,
            CensusSurveyConfig(),
            ["ONS Surveys", None, None, read_file("./templates/assets/images/census-logo.svg"), None],
        ),
        (
            None,
            None,
            SurveyConfig(),
            ["ONS Surveys", None, None, None, None],
        ),
        (
            None,
            None,
            NICensusSurveyConfig(),
            [
                "ONS Surveys",
                read_file("./templates/assets/images/nisra-logo.svg"),
                None,
                read_file("./templates/assets/images/census-logo.svg"),
                read_file("./templates/assets/images/nisra-footer-logo.svg"),
            ],
        ),
        (
            SurveyType.CENSUS_NISRA,
            "Test",
            NICensusSurveyConfig(),
            [
                "Test",
                read_file("./templates/assets/images/nisra-logo.svg"),
                None,
                read_file("./templates/assets/images/census-logo.svg"),
                read_file("./templates/assets/images/nisra-footer-logo.svg"),
            ],
        ),
        (
            SurveyType.CENSUS_NRS,
            "Test",
            NRSCensusSurveyConfig(),
            [
                "Test",
                read_file("./templates/assets/images/nrs-logo.svg"),
                None,
                read_file("./templates/assets/images/census-logo.svg"),
                read_file("./templates/assets/images/nrs-footer-logo.svg"),
            ],
        ),
    ),
)
def test_header_context(app: Flask, theme, survey_title, survey_config, expected):
    with app.app_context():
        for cookie_name, cookie_value in {
            "theme": theme,
            "title": survey_title,
        }.items():
            if cookie_value:
                cookie_session[cookie_name] = cookie_value

        context_helper = ContextHelper(
            language="en",
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        )

        result = [
            context_helper.context["survey_title"],
            context_helper.context["masthead_logo"],
            context_helper.context["masthead_logo_mobile"],
            context_helper.context["title_logo"],
            context_helper.context["footer_logo"],
        ]

    assert result == expected


@pytest.mark.parametrize(
    "survey_config, is_authenticated, theme, expected",
    [
        (
            SurveyConfig(),
            True,
            None,
            None,
        ),
        (
            CensusSurveyConfig(),
            False,
            "census",
            None,
        ),
        (
            CensusSurveyConfig(schema=QuestionnaireSchema({"survey_id": "999"})),
            True,
            "census",
            None,
        ),
        (CensusSurveyConfig(), False, None, None),
        (
            CensusSurveyConfig(schema=QuestionnaireSchema({"survey_id": "999"})),
            True,
            "census",
            None,
        ),
    ],
)
def test_service_links_context(app: Flask, mocker, survey_config, is_authenticated, theme, expected):
    with app.app_context():
        mocked_current_user = mocker.Mock()
        mocked_current_user.is_authenticated = is_authenticated
        mocker.patch("flask_login.utils._get_user", return_value=mocked_current_user)
        cookie_session["theme"] = theme

        if is_authenticated:
            mocker.patch(
                "app.helpers.template_helpers.get_metadata",
                return_value=get_metadata(
                    extra_metadata={"ru_ref": "12345678901A", "tx_id": "tx_id"},
                ),
            )

        result = ContextHelper(
            language="en",
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        ).context["service_links"]

    assert result == expected


def test_service_links_context_when_links_exist(app: Flask, mocker):
    with app.app_context():
        mocked_current_user = mocker.Mock()
        mocked_current_user.is_authenticated = True
        mocker.patch("flask_login.utils._get_user", return_value=mocked_current_user)
        cookie_session["theme"] = "default"

        survey_config = SurveyConfig()
        expected_items = [{"text": "Example", "url": "/example"}]
        mocker.patch.object(survey_config, "get_service_links", return_value=expected_items)

        result = ContextHelper(
            language="en",
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        ).context["service_links"]

    assert result == {
        "toggleServicesButton": {
            "text": "Menu",
            "ariaLabel": "Toggle services menu",
        },
        "itemsList": expected_items,
    }


@pytest.mark.parametrize(
    "survey_config, language, expected",
    [
        (
            SurveyConfig(),
            "en",
            f"{ACCOUNT_SERVICE_BASE_URL}/contact-us/",
        ),
        (
            CensusSurveyConfig(),
            "en",
            f"{ONS_URL}/aboutus/contactus/surveyenquiries/",
        ),
        (
            CensusSurveyConfig(language_code="cy"),
            "cy",
            f"{ONS_URL_CY}/aboutus/contactus/surveyenquiries/",
        ),
        (
            NICensusSurveyConfig(),
            "en",
            f"{ONS_URL}/aboutus/contactus/surveyenquiries/",
        ),
        (
            NRSCensusSurveyConfig(),
            "en",
            f"{ONS_URL}/aboutus/contactus/surveyenquiries/",
        ),
    ],
)
def test_contact_us_url_context(
    app: Flask,
    survey_config: SurveyConfig,
    language: str,
    expected: dict[str, str],
):
    with app.app_context():
        result = ContextHelper(
            language=language,
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        ).context["contact_us_url"]

    assert result == expected


@pytest.mark.parametrize(
    "survey_config, expected",
    [
        (SurveyConfig(), "Save and exit survey"),
    ],
)
def test_sign_out_button_text_context(app: Flask, survey_config: SurveyConfig, expected: dict[str, str]):
    with app.app_context():
        result = ContextHelper(
            language="en",
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        ).context["sign_out_button_text"]

    assert result == expected


@pytest.mark.parametrize(
    "survey_config, cookie_present, expected",
    [
        (SurveyConfig(), True, f"{ACCOUNT_SERVICE_BASE_URL}/cookies/"),
        (
            CensusSurveyConfig(),
            True,
            f"{ACCOUNT_SERVICE_BASE_URL_CENSUS}/en/cookies/",
        ),
        (
            CensusSurveyConfig(language_code="cy"),
            True,
            f"{ACCOUNT_SERVICE_BASE_URL_CENSUS}/cy/cookies/",
        ),
        (
            NICensusSurveyConfig(),
            True,
            f"{ACCOUNT_SERVICE_BASE_URL_CENSUS}/en/cookies/",
        ),
        (
            NRSCensusSurveyConfig(),
            True,
            f"{ACCOUNT_SERVICE_BASE_URL_CENSUS}/en/cookies/",
        ),
        (SurveyConfig(), False, None),
    ],
)
def test_cookie_settings_url_context(app: Flask, survey_config: SurveyConfig, cookie_present: bool, expected: str):
    with app.app_context():
        if cookie_present:
            cookie_session["theme"] = "dummy_value"
        context_helper = ContextHelper(
            language="en",
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        )
        result = context_helper.context.get("cookie_settings_url")

    assert result == expected


@pytest.mark.parametrize(
    "survey_config, language, address",
    [
        (SurveyConfig(), "en", ACCOUNT_SERVICE_BASE_URL),
        (
            CensusSurveyConfig(),
            "en",
            ACCOUNT_SERVICE_BASE_URL_CENSUS,
        ),
        (
            CensusSurveyConfig(),
            "cy",
            ACCOUNT_SERVICE_BASE_URL_CENSUS,
        ),
        (
            NICensusSurveyConfig(),
            "en",
            ACCOUNT_SERVICE_BASE_URL_CENSUS,
        ),
        (
            NRSCensusSurveyConfig(),
            "en",
            ACCOUNT_SERVICE_BASE_URL_CENSUS,
        ),
    ],
)
def test_cookie_domain_context(app: Flask, survey_config: SurveyConfig, language: str, address: str):
    with app.app_context():
        cookie_session["theme"] = "dummy_value"
        context_helper = ContextHelper(
            language=language,
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        )

        expected = address.replace("https://", "")
        result = context_helper.context.get("cookie_domain")

    assert result == expected


@pytest.mark.parametrize(
    "survey_config",
    [
        SurveyConfig(),
        CensusSurveyConfig(),
        NICensusSurveyConfig(),
        NRSCensusSurveyConfig(),
    ],
)
def test_cookie_domain_context_cookie_not_provided(app: Flask, survey_config: SurveyConfig):
    with app.app_context():
        context_helper = ContextHelper(
            language="en",
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        )

    assert "cookie_domain" not in context_helper.context


@pytest.mark.parametrize(
    "survey_config, expected",
    [
        (SurveyConfig(), None),
        (CensusSurveyConfig(), None),
    ],
)
def test_account_service_my_account_url_context(
    app: Flask, survey_config: SurveyConfig, expected: str, get_context_helper
):
    result = get_context_helper(app, survey_config).context["account_service_my_account_url"]

    assert result == expected


@pytest.mark.parametrize(
    "survey_config, expected",
    [
        (SurveyConfig(), None),
        (
            CensusSurveyConfig(),
            None,
        ),
    ],
)
def test_account_service_my_todo_url_context(
    app: Flask, survey_config: SurveyConfig, expected: str, get_context_helper
):
    result = get_context_helper(app, survey_config).context["account_service_todo_url"]
    assert result == expected


@pytest.mark.parametrize(
    "survey_config, expected",
    [
        (SurveyConfig(), None),
        (
            CensusSurveyConfig(),
            f"{ACCOUNT_SERVICE_BASE_URL_CENSUS}/en/start/",
        ),
        (
            NICensusSurveyConfig(),
            f"{ACCOUNT_SERVICE_BASE_URL_CENSUS}/en/start/",
        ),
        (
            NRSCensusSurveyConfig(),
            f"{ACCOUNT_SERVICE_BASE_URL_CENSUS}/en/start/",
        ),
    ],
)
def test_account_service_log_out_url_context(
    app: Flask, survey_config: SurveyConfig, expected: str, get_context_helper
):
    result = get_context_helper(app, survey_config).context["account_service_log_out_url"]
    assert result == expected


@pytest.mark.parametrize(
    "theme, language, expected",
    [
        (SurveyType.DEFAULT, "en", CensusSurveyConfig),
        (SurveyType.DEFAULT, "cy", CensusSurveyConfig),
        (SurveyType.CENSUS, "en", CensusSurveyConfig),
        (SurveyType.CENSUS, "cy", CensusSurveyConfig),
        (SurveyType.CENSUS_NISRA, "en", NICensusSurveyConfig),
        (SurveyType.CENSUS_NRS, "en", NRSCensusSurveyConfig),
        (None, None, CensusSurveyConfig),
    ],
)
def test_get_survey_config(app: Flask, theme: SurveyType, language: str, expected: SurveyConfig):
    with app.app_context():
        result = get_survey_config(theme=theme, language=language)
    assert isinstance(result, expected)


@pytest.mark.parametrize(
    "survey_config_type, base_url",
    [
        (CensusSurveyConfig, ACCOUNT_SERVICE_BASE_URL_CENSUS),
        (SurveyConfig, DEFAULT_URL),
    ],
)
def test_survey_config_base_url_provided_used_in_links(
    app: Flask, survey_config_type: type[SurveyConfig], base_url: str
):
    with app.app_context():
        result = survey_config_type(base_url=base_url)

    assert result.base_url == base_url

    urls_to_check = [
        result.account_service_my_account_url,
        result.account_service_log_out_url,
        result.account_service_todo_url,
        result.cookie_settings_url,
        result.contact_us_url,
        result.privacy_and_data_protection_url,
    ]

    if survey_config_type == CensusSurveyConfig:
        urls_to_check.remove(result.contact_us_url)

    for url in urls_to_check:
        if url:
            assert base_url in url


def test_survey_config_base_url_duplicate_todo(app: Flask):
    base_url = f"{DEFAULT_URL}/surveys/todo"
    with app.app_context():
        result = CensusSurveyConfig(base_url=base_url)

    assert result.base_url == base_url

    assert result.account_service_log_out_url == f"{base_url}/en/start/"
    assert result.account_service_my_account_url is None
    assert result.account_service_todo_url is None
    assert result.contact_us_url == f"{ONS_URL}/aboutus/contactus/surveyenquiries/"
    assert result.cookie_settings_url == f"{base_url}/en/cookies/"
    assert result.privacy_and_data_protection_url == f"{base_url}/en/privacy-and-data-protection/"


def test_get_survey_config_base_url_not_provided(app: Flask):
    with app.app_context():
        result = get_survey_config()

    assert result.base_url == ACCOUNT_SERVICE_BASE_URL


def test_context_set_from_app_config(app):
    with app.app_context():
        current_app.config["CDN_URL"] = "test-cdn-url"
        current_app.config["CDN_ASSETS_PATH"] = "/test-assets-path"
        current_app.config["ADDRESS_LOOKUP_API_URL"] = "test-address-lookup-api-url"
        current_app.config["EQ_GOOGLE_TAG_ID"] = "test-google-tag-manager-id"
        survey_config = SurveyConfig()

        context = ContextHelper(
            language="en",
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        ).context

    assert context["cdn_url"] == "test-cdn-url/test-assets-path"
    assert context["address_lookup_api_url"] == "test-address-lookup-api-url"
    assert context["google_tag_id"] == "test-google-tag-manager-id"


@pytest.mark.parametrize(
    "theme, language, expected",
    [
        (SurveyType.DEFAULT, "en", None),
        (SurveyType.CENSUS, "en", None),
        (SurveyType.CENSUS, "cy", None),
        (SurveyType.CENSUS_NISRA, "en", None),
        (SurveyType.CENSUS_NRS, "en", None),
    ],
)
def test_correct_theme_in_context(app: Flask, theme: SurveyType, language: str, expected: str):
    with app.app_context():
        survey_config = get_survey_config(theme=theme, language=language)
        result = ContextHelper(
            language="en",
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        ).context["theme"]
    assert result == expected


@pytest.mark.parametrize(
    "theme, language, expected",
    [
        (SurveyType.DEFAULT, "en", "ONS Surveys"),
        (SurveyType.CENSUS, "en", "ONS Surveys"),
        (SurveyType.CENSUS, "cy", "ONS Surveys"),
        (SurveyType.CENSUS_NISRA, "en", "ONS Surveys"),
        (SurveyType.CENSUS_NRS, "en", "ONS Surveys"),
    ],
)
def test_use_default_survey_title_in_context_when_no_cookie(
    app: Flask, theme: SurveyType, language: str, expected: str
):
    with app.app_context():
        survey_config = get_survey_config(theme=theme, language=language)
        result = ContextHelper(
            language="en",
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        ).context["survey_title"]
    assert result == expected


@pytest.mark.parametrize(
    "theme, language, schema, expected",
    [
        (
            SurveyType.DEFAULT,
            "en",
            QuestionnaireSchema({"survey_id": "999"}),
            {"survey_id": "999"},
        ),
        (
            SurveyType.DEFAULT,
            "en",
            QuestionnaireSchema({"survey_id": "999", "form_type": "test"}),
            {"form_type": "test", "survey_id": "999"},
        ),
        (
            SurveyType.CENSUS,
            "en",
            QuestionnaireSchema({"survey_id": "999", "form_type": "test", "title": "test_title"}),
            {"form_type": "test", "survey_id": "999", "title": "test_title"},
        ),
        (
            SurveyType.CENSUS,
            "cy",
            QuestionnaireSchema({"survey_id": "999", "form_type": "test", "title": "test_title"}),
            {"form_type": "test", "survey_id": "999", "title": "test_title"},
        ),
        (
            SurveyType.CENSUS_NISRA,
            "en",
            QuestionnaireSchema({"survey_id": "999", "form_type": "test", "title": "test_title"}),
            {"form_type": "test", "survey_id": "999", "title": "test_title"},
        ),
        (
            SurveyType.CENSUS_NRS,
            "en",
            QuestionnaireSchema({"survey_id": "999"}),
            {"survey_id": "999"},
        ),
    ],
)
def test_correct_data_layer_in_context(
    app: Flask,
    theme: SurveyType,
    language: str,
    schema: QuestionnaireSchema,
    expected: str,
):
    with app.app_context():
        set_schema_context_in_cookie(schema)
        survey_config = get_survey_config(theme=theme, language=language, schema=schema)

        result = ContextHelper(
            language="en",
            is_post_submission=False,
            include_csrf_token=True,
            survey_config=survey_config,
        ).context["data_layer"]
    assert result == expected


@pytest.mark.parametrize(
    "include_csrf_token",
    [
        False,
        True,
    ],
)
def test_include_csrf_token(app: Flask, include_csrf_token: bool):
    with app.app_context():
        survey_config = SurveyConfig()

        result = ContextHelper(
            language="en",
            is_post_submission=False,
            include_csrf_token=include_csrf_token,
            survey_config=survey_config,
        ).context["include_csrf_token"]

    assert result == include_csrf_token


def test_get_survey_config_language_retrieved_from_cookie(app: Flask):
    with app.app_context():
        cookie_session["language_code"] = "cy"
        cookie_session["theme"] = SurveyType.CENSUS
        result = get_survey_config()

    assert result.account_service_log_out_url == f"{ACCOUNT_SERVICE_BASE_URL}/cy/start/"
