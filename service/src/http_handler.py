from aiohttp.web import BaseRequest, json_response, Response as HTTPResponse
from aiohttp.web import HTTPServiceUnavailable, HTTPGatewayTimeout
from aiohttp.web import HTTPBadRequest, HTTPInternalServerError
from request import RequestError, Request, Response, ResponseStatus
from asyncio import Queue, QueueFull, wait_for, TimeoutError
from urllib.parse import parse_qs
import logging


logger = logging.getLogger(__name__)


class HttpHander:
    def __init__(self,
                 request_queue: Queue,
                 request_timeout: float) -> None:
        self.req_queue = request_queue
        self.req_timeout = request_timeout

    async def handle_request(self, request: Request) -> HTTPResponse:
        try:
            logger.info(f'Defined id {request.id} to received request')

            self.req_queue.put_nowait(request)
            await wait_for(
                    request.wait_response(), timeout=self.req_timeout)

            logger.info(f'Request id {request.id} answered')
            return json_response(request.toDict())

        except QueueFull:
            logger.warn(
                f'Request id {request.id} rejected due to server overload')
            request.answer(Response(ResponseStatus.ERROR, 'Server overloaded'))
            return HTTPServiceUnavailable()

        except TimeoutError:
            logger.warn(f'Request id {request.id} timed out')
            request.answer(Response(ResponseStatus.ERROR, 'Timeout'))
            return HTTPGatewayTimeout()

        except RequestError as error:
            logger.error(
                f'Request error handling request id {request.id}: {error}')
            request.answer(Response(ResponseStatus.ERROR,
                                    f'Internal Server error: {error}'))
            return HTTPInternalServerError()

    async def handle_info_request(self, request: BaseRequest) -> HTTPResponse:
        try:
            params = parse_qs(request.query_string)
            if 'target' not in params or\
                    len(params) > 1 or \
                    not isinstance(params['target'], list) or \
                    len(params['target']) != 1:
                return HTTPBadRequest()

            return await self.handle_request(Request(params['target'][0]))

        except RequestError as error:
            logger.error(f'Request error handling http request: {error}')
            return HTTPBadRequest()

        except Exception as error:
            logger.error(f'Error handling http request: {error}')
            return HTTPInternalServerError()
