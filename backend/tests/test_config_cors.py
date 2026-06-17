from app.core.config import _parse_cors_origins


def test_parses_json_array():
    assert _parse_cors_origins('["https://app.x.com", "https://y.com"]') == [
        "https://app.x.com",
        "https://y.com",
    ]


def test_strips_trailing_slash_from_json_array():
    assert _parse_cors_origins('["https://app.x.com/"]') == ["https://app.x.com"]


def test_falls_back_to_comma_separated_list():
    assert _parse_cors_origins("https://app.x.com,https://y.com/") == [
        "https://app.x.com",
        "https://y.com",
    ]


def test_accepts_bare_single_origin():
    assert _parse_cors_origins("https://app.x.com") == ["https://app.x.com"]
