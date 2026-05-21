from app.services.shortener import base62_encode


def test_base62_encoding() -> None:
    assert base62_encode(0) == "0"
    assert base62_encode(61) == "Z"
    assert base62_encode(62) == "10"
