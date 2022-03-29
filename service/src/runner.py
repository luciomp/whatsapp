from typing import Any
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
# from appium import webdriver
from appium.webdriver import Remote
from appium.webdriver.common.appiumby import AppiumBy
import selenium.common.exceptions as selexcpt
from base64 import b64decode, b64encode
from PIL import Image
from io import BytesIO
from request import Response, ResponseStatus
from asyncio import get_running_loop, Queue
from request import Request
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
# from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class AppiumConnection():
    def __init__(self, server: str) -> None:
        self.server = server
        self.driver = None

    def __enter__(self):
        self.driver = Remote(self.server, {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'deviceName': 'Android Emulator'
        })
        return self.driver

    def __exit__(self, type, value, traceback):
        with suppress(Exception):
            if self.driver:
                self.driver.quit()


class Runner:
    def __init__(self,
                 queue: Queue,
                 server: str,
                 wait_timeout) -> None:
        self.req_queue = queue
        self.server = server
        self.wait_timeout = wait_timeout
        self.pool = ThreadPoolExecutor()
        self.driver = None

    def wait_for_presence(self, loc) -> Any:
        try:
            return WebDriverWait(self.driver, self.wait_timeout)\
                    .until(
                        expected_conditions.presence_of_element_located(loc))
        except selexcpt.TimeoutException:
            logger.debug('TimeoutException')
            return None
        except Exception as error:
            logger.debug(f'wait_for_presence::Exception: {error}')
            return None

    def get_full_image(self) -> str:
        ret = ""
        try:
            e = self.wait_for_presence(
                (AppiumBy.ID, 'com.whatsapp:id/picture_animation'))
            if not e:
                raise Exception('Picture Animation not found')

            logger.debug('Taking a screenshot')
            ib = b64decode(self.driver.get_screenshot_as_base64())

            logger.debug('Cropping the screenshot')
            r = Image.open(BytesIO(ib)).crop((
                e.location['x'],
                e.location['y'],
                e.location['x'] + e.size['width'],
                e.location['y'] + e.size['height']))

            logger.debug('Decoding to b64')
            buffer = BytesIO()
            r.save(buffer, format="png")
            ret = b64encode(buffer.getvalue()).decode()

        except Exception as error:
            logger.error(f'Exception getting image: {error}')

        finally:
            return ret

    def get_text(self, id: str) -> str:
        e = self.wait_for_presence((AppiumBy.ID, id))
        return e.text if e else ""

    def click(self, id: str) -> None:
        e = self.wait_for_presence((AppiumBy.ID, id))
        if e:
            e.click()

    def execute(self, req: Request) -> None:
        with AppiumConnection(self.server) as driver:
            self.driver = driver
            self.execute_conn(req)

    def execute_conn(self, req: Request) -> None:
        number: str = req.target

        ci: dict = {
            'contact_title': '',
            'contact_subtitle': '',
            'contact_status': '',
            'contact_status_info': '',
            'contact_image': ''
        }

        logger.debug('Opening new chat')
        self.driver.execute_script(
            'mobile: shell', {
                'command': 'am',
                'args': 'start -a android.intent.action.VIEW '
                        f'-d "https://api.whatsapp.com/send?phone={number}"'}
        )

        logger.debug('Looking for contact name')
        self.click('com.whatsapp:id/conversation_contact_name')

        logger.debug('Looking for contact title')
        ci['contact_title'] = self.get_text('com.whatsapp:id/contact_title')

        logger.debug('Looking for contact subtitle')
        ci['contact_subtitle'] = \
            self.get_text('com.whatsapp:id/contact_subtitle')

        logger.debug('Looking for contact status')
        ci['contact_status'] = self.get_text('com.whatsapp:id/status')

        print('Looking for contact status info')
        ci['contact_status_info'] = \
            self.get_text('com.whatsapp:id/status_info')

        logger.debug('Looking for contact image')
        self.click('com.whatsapp:id/profile_picture_image')
        ci['contact_image'] = self.get_full_image()
        # logger.debug('Navigating to up steps')
        # bt = self.wait_for_presence(
        #     (AppiumBy.ACCESSIBILITY_ID, 'Navigate up'))
        # if bt:
        #     bt.click()

        d = 'Ok with any info' if any(ci.values()) else \
            'Target is not sharing any info'
        req.answer(Response(ResponseStatus.OK, d, *ci.values()))

    async def run(self):
        while True:
            logger.debug('waiting for request')
            req: Request = await self.req_queue.get()
            if not req.answered():
                logger.debug('New request, found, executing...')
                try:
                    loop = get_running_loop()
                    await loop.run_in_executor(self.pool, self.execute, req)
                except Exception as error:
                    req.answer(Response(ResponseStatus.ERROR,
                               'Unable to connect to device'))
                    logger.error(f'Exception executing request: {error}')
