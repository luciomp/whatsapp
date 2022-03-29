from datetime import datetime
import logging
from uuid import uuid1
from asyncio import Queue


logger = logging.getLogger(__name__)


class RequestError(Exception):
    pass


class ResponseStatus:
    OK = 'OK'
    ERROR = 'ERROR'

    def is_valid_status(s):
        return s == ResponseStatus.OK or s == ResponseStatus.ERROR


class Response:
    def __init__(self,
                 status: ResponseStatus,
                 detail: str = "",
                 contact_title: str = "",
                 contact_subtitle: str = "",
                 contact_status: str = "",
                 contact_status_info: str = "",
                 contact_image: str = "") -> None:

        if not ResponseStatus.is_valid_status(status):
            raise RequestError("Invallid response status")

        self.dt = datetime.utcnow()
        self.status = status
        self.detail = detail
        self.contact_title = contact_title
        self.contact_subtitle = contact_subtitle
        self.contact_status = contact_status
        self.contact_status_info = contact_status_info
        self.contact_image = contact_image

    def toDict(self) -> dict:
        return {
            'status': self.status,
            'details': self.detail,
            'responsetime': self.dt.isoformat(),
            'contact_title': self.contact_title,
            'contact_subtitle': self.contact_subtitle,
            'contact_status': self.contact_status,
            'contact_image': self.contact_image
        }


class Request:
    def __init__(self,
                 target_identity: str) -> None:

        if not isinstance(target_identity, str) or \
                len(target_identity) < 6:
            raise RequestError()

        self.id = uuid1()
        self.target = target_identity
        self.dt = datetime.utcnow()
        self.resp = None
        self.resp_queue = Queue(maxsize=1)

    def answer(self, response: Response) -> None:
        if not isinstance(response, Response):
            raise RequestError(
                'Request must be answered with a valid Response')

        if not self.answered():
            self.resp = response

        if self.resp_queue.empty():
            self.resp_queue.put_nowait(response)

    def answered(self) -> bool:
        return self.resp is not None

    async def wait_response(self) -> Response:
        if not self.answered():
            self.resp = await self.resp_queue.get()

        return self.resp

    def toDict(self):
        return {
            'id': str(self.id),
            'requesttime': self.dt.isoformat()
        } | self.resp.toDict() if self.answered() else {}
