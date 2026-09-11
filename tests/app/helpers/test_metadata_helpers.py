from app.helpers.metadata_helpers import get_ru_ref_without_check_letter


def test_get_ru_ref_without_check_letter():
    assert get_ru_ref_without_check_letter("12345678901A") == "12345678901"
