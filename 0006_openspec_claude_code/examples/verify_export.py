#!/usr/bin/env python3
"""Verify the module 0006 CSV contract against a disposable seeded aggregator."""

import argparse
import csv
from io import StringIO
import json
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def read(base, path, method="GET"):
    with urlopen(Request(base + path, method=method), timeout=5) as response:
        return response.headers, response.read().decode("utf-8")


def verify(base):
    _, json_text = read(base, "/favoritos")
    favorites = json.loads(json_text)
    assert len(favorites) == 1, favorites
    expected = favorites[0]
    assert expected["titulo"].startswith("="), expected

    headers, text = read(base, "/favoritos/export.csv")
    assert headers.get_content_type() == "text/csv", headers
    assert headers.get_content_charset() == "utf-8", headers
    assert headers.get_content_disposition() == "attachment", headers
    assert headers.get_filename() == "favoritos.csv", headers
    columns, *rows = csv.reader(StringIO(text))
    assert columns == ["titulo", "link", "fonte"], columns
    assert rows == [["'" + expected["titulo"], expected["link"], expected["fonte"]]], rows
    _, json_after_export = read(base, "/favoritos")
    assert json.loads(json_after_export) == favorites, json_after_export

    path = f'/artigos/{expected["id"]}/favoritar'
    read(base, path, "DELETE")
    try:
        _, empty = read(base, "/favoritos/export.csv")
        assert list(csv.reader(StringIO(empty))) == [columns], empty
    finally:
        read(base, path, "POST")
    _, json_after_restore = read(base, "/favoritos")
    assert json.loads(json_after_restore) == favorites, json_after_restore
    print("CSV attachment, quoting, filtered rows, header-only export, and existing JSON verified.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:19806")
    args = parser.parse_args()
    base = args.url.rstrip("/")
    url = urlsplit(base)
    if url.scheme != "http" or url.hostname != "127.0.0.1" or url.username or url.path or url.query or url.fragment:
        parser.error("Use the loopback HTTP address of the disposable lab.")
    verify(base)
