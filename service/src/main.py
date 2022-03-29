from aiohttp import web
from http_handler import HttpHander
from runner import Runner
from asyncio import create_task, CancelledError, Queue
from contextlib import suppress
import logging
import sys


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    # TODO: jogar para arquivo
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('selenium').setLevel(logging.ERROR)

    # TODO: confs de algum lugar
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    max_req = 5
    req_timeout = 30
    wait_timeout = 5
    server = 'http://192.168.0.13:4723/wd/hub'

    req_queue = Queue(maxsize=max_req)
    runner = Runner(req_queue, server, wait_timeout)
    http_hdlr = HttpHander(req_queue, req_timeout)

    app = web.Application()
    app.router.add_view(path='/getinfo', handler=http_hdlr.handle_info_request)

    async def run_other_task(_app):
        task = create_task(runner.run())
        yield
        task.cancel()
        with suppress(CancelledError):
            await task

    app.cleanup_ctx.append(run_other_task)
    web.run_app(app, host='0.0.0.0', port=port)
