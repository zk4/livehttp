
# -*- coding: utf-8 -*-

from livehttp import livehttp

def test_run_openssl_command() -> None:
    assert 1 == 1


def test_feed():
    assert 4 == livehttp.feed(2)
