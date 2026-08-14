from pytest import fixture

from app.helpers.template_helpers import ContextHelper
from app.settings import ACCOUNT_SERVICE_BASE_URL, ACCOUNT_SERVICE_BASE_URL_CENSUS, ONS_URL, ONS_URL_CY


@fixture
def get_context_helper():
    def _context_helper(app, survey_config, is_post_submission=False, include_csrf_token=True):
        with app.test_client():
            return ContextHelper(
                language="en",
                is_post_submission=is_post_submission,
                include_csrf_token=include_csrf_token,
                survey_config=survey_config,
            )

    return _context_helper


def footer_context():
    return {
        "lang": "en",
        "crest": True,
        "newTabWarning": "The following links open in a new tab",
        "copyrightDeclaration": {
            "copyright": "Crown copyright and database rights 2020 OS 100019153.",
            "text": "Use of address data is subject to the terms and conditions.",
        },
    }


def expected_footer_census_theme(language_code: str):
    ons_url = ONS_URL_CY if language_code == "cy" else ONS_URL
    upstream_url = f"{ACCOUNT_SERVICE_BASE_URL_CENSUS}/{language_code}"
    census_footer_context = {
        "lang": language_code,
        "crest": True,
        "newTabWarning": "The following links open in a new tab",
        "copyrightDeclaration": {
            "copyright": "Crown copyright and database rights 2020 OS 100019153.",
            "text": "Use of address data is subject to the terms and conditions.",
        },
    }
    census = {
        "rows": [
            {
                "itemsList": [
                    {
                        "text": "What we do",
                        "url": f"{ons_url}/aboutus/whatwedo/",
                        "target": "_blank",
                    },
                    {
                        "text": "Contact us",
                        "url": f"{ons_url}/aboutus/contactus/surveyenquiries/",
                        "target": "_blank",
                    },
                    {
                        "text": "Accessibility",
                        "url": f"{ons_url}/help/accessibility/",
                        "target": "_blank",
                    },
                ]
            }
        ],
        "legal": [
            {
                "itemsList": [
                    {
                        "text": "Cookies",
                        "url": f"{upstream_url}/cookies/",
                        "target": "_blank",
                    },
                    {
                        "text": "Privacy and data protection",
                        "url": f"{upstream_url}/privacy-and-data-protection/",
                        "target": "_blank",
                    },
                ]
            }
        ],
    }
    return census_footer_context | census


def expected_footer_census_theme_no_cookie():
    census = {
        "rows": [
            {
                "itemsList": [
                    {
                        "text": "What we do",
                        "url": "https://www.ons.gov.uk/aboutus/whatwedo/",
                        "target": "_blank",
                    },
                    {
                        "text": "Accessibility",
                        "url": "https://www.ons.gov.uk/help/accessibility/",
                        "target": "_blank",
                    },
                ]
            }
        ],
    }
    return {**footer_context(), **census}
