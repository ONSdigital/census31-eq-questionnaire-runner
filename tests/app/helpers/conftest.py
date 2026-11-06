from pytest import fixture

from app.helpers.template_helpers import ContextHelper
from app.settings import ACCOUNT_SERVICE_BASE_URL, CENSUS_ASSETS_BASE_URL, ONS_URL, ONS_URL_CY


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
            "copyright": "Crown copyright and database rights 2027 OS 100019153.",
            "text": "Use of address data is subject to the terms and conditions.",
        },
    }


def expected_footer_census_theme(
    language_code: str,
    *,
    help_url: str | None = None,
    contact_us_url: str | None = None,
    feedback_url: str | None = None,
    footer_logo: str | None = None,
    footer_logo_alt_text: str | None = None,
    privacy_and_data_protection_url: str | None = None,
):
    ons_url = ONS_URL_CY if language_code == "cy" else ONS_URL
    upstream_url = f"{ACCOUNT_SERVICE_BASE_URL}/{language_code}"
    footer_links = [
        {
            "text": "Contact us",
            "url": contact_us_url or f"{ons_url}/census/aboutcensus/census2031/2027test/contactus/",
            "target": "_blank",
        }
    ]

    if help_url:
        footer_links.insert(
            0,
            {
                "text": "Help",
                "url": help_url,
                "target": "_blank",
            },
        )

    if feedback_url:
        footer_links.insert(
            0,
            {
                "text": "Feedback",
                "url": feedback_url,
                "target": "_blank",
            },
        )

    census_footer_context = {
        "lang": language_code,
        "crest": True,
        "newTabWarning": "The following links open in a new tab",
        "copyrightDeclaration": {
            "copyright": "Crown copyright and database rights 2027 OS 100019153.",
            "text": "Use of address data is subject to the terms and conditions.",
        },
    }

    if footer_logo and footer_logo_alt_text:
        census_footer_context["footerLogo"] = {
            "logos": {
                "logo1": {
                    "logoImage": (
                        f'<img src="{CENSUS_ASSETS_BASE_URL}/images/{footer_logo}" '
                        f'alt="{footer_logo_alt_text}" title="{footer_logo_alt_text}">'
                    ),
                },
            },
        }
    census = {
        "rows": [{"itemsList": footer_links}],
        "legal": [
            {
                "itemsList": [
                    {
                        "text": "Cookies",
                        "url": f"{upstream_url}/cookies/",
                        "target": "_blank",
                    },
                    {
                        "text": "Accessibility statement",
                        "url": f"{ons_url}/help/accessibility/",
                        "target": "_blank",
                    },
                    {
                        "text": "Privacy and data protection",
                        "url": privacy_and_data_protection_url
                        or (
                            f"{ons_url}/prawf-cyfrifiad/preifatrwydd/"
                            if language_code == "cy"
                            else f"{ons_url}/census-test/privacy/"
                        ),
                        "target": "_blank",
                    },
                ]
            }
        ],
    }
    return census_footer_context | census


def expected_footer_census_theme_no_cookie():
    return footer_context()
