from app.utils.url_validator import is_safe_url


def test_valid_https():
    assert is_safe_url("https://boards.greenhouse.io/company/jobs/123") is True


def test_valid_http():
    assert is_safe_url("http://lever.co/postings/company") is True


def test_localhost_blocked():
    assert is_safe_url("http://localhost:8000/admin") is False


def test_loopback_blocked():
    assert is_safe_url("http://127.0.0.1/secret") is False


def test_metadata_blocked():
    assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False


def test_file_protocol_blocked():
    assert is_safe_url("file:///etc/passwd") is False


def test_empty_string():
    assert is_safe_url("") is False


def test_private_ip_blocked():
    assert is_safe_url("http://192.168.1.1/api") is False
