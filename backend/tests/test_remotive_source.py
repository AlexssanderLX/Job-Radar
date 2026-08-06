from app.sources.remotive import _parse_date, _plain_text


def test_remotive_description_becomes_plain_text():
    assert _plain_text("<p>Python &amp; Docker</p>") == "Python & Docker"


def test_remotive_date_is_timezone_aware():
    parsed = _parse_date("2026-08-01T12:30:00")
    assert parsed is not None
    assert parsed.tzinfo is not None
