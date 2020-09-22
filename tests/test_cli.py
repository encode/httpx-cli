import os

import pytest
from click.testing import CliRunner

import httpx
from httpx_cli import cli


def splitlines(output):
    return [line.strip() for line in output.splitlines()]


def remove_date_header(lines):
    return [line for line in lines if not line.startswith("date:")]


def test_get(server):
    runner = CliRunner()
    result = runner.invoke(cli, [server.url])
    assert result.exit_code == 0
    assert remove_date_header(splitlines(result.output)) == [
        "HTTP/1.1 200 OK",
        "server: uvicorn",
        "content-type: text/plain",
        "transfer-encoding: chunked",
        "",
        "Hello, world!",
    ]


def test_json(server):
    url = str(httpx.URL(server.url).copy_with(path="/json"))
    runner = CliRunner()
    result = runner.invoke(cli, [url])
    assert result.exit_code == 0
    assert remove_date_header(splitlines(result.output)) == [
        "HTTP/1.1 200 OK",
        "server: uvicorn",
        "content-type: application/json",
        "transfer-encoding: chunked",
        "",
        "{",
        '"Hello": "world!"',
        "}",
    ]


def test_post(server):
    url = str(httpx.URL(server.url).copy_with(path="/echo_body"))
    runner = CliRunner()
    result = runner.invoke(cli, [url, "-m", "POST", "-j", '{"hello": "world"}'])
    assert result.exit_code == 0
    assert remove_date_header(splitlines(result.output)) == [
        "HTTP/1.1 200 OK",
        "server: uvicorn",
        "content-type: text/plain",
        "transfer-encoding: chunked",
        "",
        '{"hello": "world"}',
    ]


def test_verbose(server):
    url = httpx.URL(server.url)
    runner = CliRunner()
    result = runner.invoke(cli, [server.url, "-v"])
    assert result.exit_code == 0
    assert remove_date_header(splitlines(result.output)) == [
        "GET / HTTP/1.1",
        f"host: {url.netloc}",
        "accept: */*",
        "accept-encoding: gzip, deflate, br",
        "connection: keep-alive",
        f"user-agent: python-httpx/{httpx.__version__}",
        "",
        "HTTP/1.1 200 OK",
        "server: uvicorn",
        "content-type: text/plain",
        "transfer-encoding: chunked",
        "",
        "Hello, world!",
    ]


def test_auth(server):
    url = httpx.URL(server.url)
    runner = CliRunner()
    result = runner.invoke(cli, [server.url, "-v", "-a", "username", "password"])
    assert result.exit_code == 0
    assert remove_date_header(splitlines(result.output)) == [
        "GET / HTTP/1.1",
        f"host: {url.netloc}",
        "accept: */*",
        "accept-encoding: gzip, deflate, br",
        "connection: keep-alive",
        f"user-agent: python-httpx/{httpx.__version__}",
        "authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=",
        "",
        "HTTP/1.1 200 OK",
        "server: uvicorn",
        "content-type: text/plain",
        "transfer-encoding: chunked",
        "",
        "Hello, world!",
    ]


def test_download(server):
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(cli, [server.url, "--download"])
        assert os.path.exists("index.txt")
        with open("index.txt", "r") as input_file:
            assert input_file.read() == "Hello, world!"

        runner.invoke(cli, [server.url, "--download"])
        assert os.path.exists("index.txt")
        with open("index-1.txt", "r") as input_file:
            assert input_file.read() == "Hello, world!"


def test_errors(server):
    runner = CliRunner()
    result = runner.invoke(cli, [server.url, "-h", "host", " "])
    assert result.exit_code == 1
    assert splitlines(result.output) == [
        "LocalProtocolError: Illegal header value b' '",
    ]
