"""nexus_fetch: CDN download URIs from the Nexus API can contain spaces in the file name."""

import nexus_fetch


def test_quote_uri_encodes_spaces_in_path_and_keeps_query():
    uri = ("https://cf-files.nexusmods.com/cdn/1704/150715/"
           "Skyshards - CS Light Addon-150715-1-0-0-1748776434.zip?expires=1&md5=Ab_c-D&user_id=1")
    out = nexus_fetch.quote_uri(uri)
    assert " " not in out
    assert "/Skyshards%20-%20CS%20Light%20Addon-150715-1-0-0-1748776434.zip" in out
    assert out.endswith("?expires=1&md5=Ab_c-D&user_id=1")


def test_quote_uri_leaves_already_safe_uri_unchanged():
    uri = "https://cf-files.nexusmods.com/cdn/1704/1/Plain-1-0.7z?expires=1&md5=x"
    assert nexus_fetch.quote_uri(uri) == uri


def test_quote_uri_does_not_double_encode():
    uri = "https://cf-files.nexusmods.com/cdn/1704/1/A%20B.7z?expires=1"
    assert nexus_fetch.quote_uri(uri) == uri


def test_quote_uri_encodes_brackets_and_non_ascii():
    uri = "https://cf-files.nexusmods.com/cdn/1704/1/[SSE] Café Pack.7z?e=1"
    out = nexus_fetch.quote_uri(uri)
    assert "%5BSSE%5D%20Caf%C3%A9%20Pack.7z" in out


def test_quote_uri_hash_and_question_mark_in_name_keep_signed_query():
    base = "https://cf-files.nexusmods.com/cdn/1704/1/"
    q = "?expires=1&md5=x&user_id=42"
    out = nexus_fetch.quote_uri(base + "Bug #123 Fix.zip" + q)
    assert out == base + "Bug%20%23123%20Fix.zip" + q
    out = nexus_fetch.quote_uri(base + "Really? Yes.zip" + q)
    assert out == base + "Really%3F%20Yes.zip" + q


def test_quote_uri_encodes_lone_percent_but_keeps_valid_escapes():
    base = "https://cf-files.nexusmods.com/cdn/1704/1/"
    assert nexus_fetch.quote_uri(base + "100% Craftable.zip?expires=1") == base + "100%25%20Craftable.zip?expires=1"
    assert nexus_fetch.quote_uri(base + "A%2FB.zip?expires=1") == base + "A%2FB.zip?expires=1"


def test_cdn_403_raises_cdn_error_not_http_error(monkeypatch, tmp_path):
    import urllib.error
    import pytest

    def fake_urlopen(req, timeout=0):
        raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", None, None)

    monkeypatch.setattr(nexus_fetch.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(nexus_fetch.CdnHTTPError) as exc:
        nexus_fetch.download_file("https://cf-files.nexusmods.com/cdn/x.zip?expires=1", tmp_path / "x.part")
    assert exc.value.args[0] == 403
    assert not isinstance(exc.value, urllib.error.HTTPError)


def test_quote_uri_without_signed_query():
    assert nexus_fetch.quote_uri("https://h.example/a b.zip") == "https://h.example/a%20b.zip"
