from app.sources.remoteok import _parse_date, _plain_text
from app.core.expansions import matches_role_text


def test_remoteok_description_becomes_plain_text():
    assert _plain_text("<b>.NET &amp; Docker</b>") == ".NET & Docker"


def test_remoteok_date_is_timezone_aware():
    parsed = _parse_date("2026-08-05T19:01:14+00:00")
    assert parsed is not None
    assert parsed.tzinfo is not None


def test_backend_role_matches_generic_english_software_title():
    assert matches_role_text("Independent Software Developer", ["Desenvolvedor Backend"])


def test_full_stack_role_matches_hyphenated_title():
    assert matches_role_text("Full-Stack Rails Engineer", ["Desenvolvedor Full Stack"])
