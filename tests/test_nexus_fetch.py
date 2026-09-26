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
