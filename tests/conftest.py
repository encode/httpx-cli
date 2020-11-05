import asyncio
import threading
import time

import pytest
from uvicorn.config import Config
from uvicorn.main import Server


async def app(scope, receive, send):
      """
      Sends the app.

      Args:
          scope: (str): write your description
          receive: (todo): write your description
          send: (todo): write your description
      """
    assert scope["type"] == "http"
    if scope["path"].startswith("/echo_body"):
        await echo_body(scope, receive, send)
    elif scope["path"].startswith("/json"):
        await hello_world_json(scope, receive, send)
    else:
        await hello_world(scope, receive, send)


async def hello_world(scope, receive, send):
      """
      Emit a world.

      Args:
          scope: (str): write your description
          receive: (todo): write your description
          send: (todo): write your description
      """
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"text/plain"]],
        }
    )
    await send({"type": "http.response.body", "body": b"Hello, world!"})


async def hello_world_json(scope, receive, send):
      """
      Displays the world json in the world.

      Args:
          scope: (str): write your description
          receive: (todo): write your description
          send: (todo): write your description
      """
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"application/json"]],
        }
    )
    await send({"type": "http.response.body", "body": b'{"Hello": "world!"}'})


async def echo_body(scope, receive, send):
      """
      Echo a message.

      Args:
          scope: (str): write your description
          receive: (str): write your description
          send: (todo): write your description
      """
    body = b""
    more_body = True

    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)

    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"text/plain"]],
        }
    )
    await send({"type": "http.response.body", "body": body})


class TestServer(Server):
    @property
    def url(self) -> str:
        """
        Str : url for the http request.

        Args:
            self: (todo): write your description
        """
        protocol = "https" if self.config.is_ssl else "http"
        return f"{protocol}://{self.config.host}:{self.config.port}/"

    def install_signal_handlers(self) -> None:
        """
        Installs the default signal handlers.

        Args:
            self: (todo): write your description
        """
        # Disable the default installation of handlers for signals such as SIGTERM,
        # because it can only be done in the main thread.
        pass

    async def serve(self, sockets=None):
          """
          Starts the event loop.

          Args:
              self: (todo): write your description
              sockets: (str): write your description
          """
        self.restart_requested = asyncio.Event()

        loop = asyncio.get_event_loop()
        tasks = {
            loop.create_task(super().serve(sockets=sockets)),
            loop.create_task(self.watch_restarts()),
        }
        await asyncio.wait(tasks)

    async def restart(self) -> None:  # pragma: nocover
          """
          Restart the connection.

          Args:
              self: (todo): write your description
          """
        # This coroutine may be called from a different thread than the one the
        # server is running on, and from an async environment that's not asyncio.
        # For this reason, we use an event to coordinate with the server
        # instead of calling shutdown()/startup() directly, and should not make
        # any asyncio-specific operations.
        self.started = False
        self.restart_requested.set()
        while not self.started:
            await asyncio.sleep(0.2)

    async def watch_restarts(self):  # pragma: nocover
          """
          Perform a new watch.

          Args:
              self: (todo): write your description
          """
        while True:
            if self.should_exit:
                return

            try:
                await asyncio.wait_for(self.restart_requested.wait(), timeout=0.1)
            except asyncio.TimeoutError:
                continue

            self.restart_requested.clear()
            await self.shutdown()
            await self.startup()


def serve_in_thread(server: Server):
    """
    Run a server thread.

    Args:
        server: (str): write your description
    """
    thread = threading.Thread(target=server.run)
    thread.start()
    try:
        while not server.started:
            time.sleep(1e-3)
        yield server
    finally:
        server.should_exit = True
        thread.join()


@pytest.fixture(scope="session")
def server():
    """
    A wsgi application.

    Args:
    """
    config = Config(app=app, lifespan="off", loop="asyncio")
    server = TestServer(config=config)
    yield from serve_in_thread(server)
