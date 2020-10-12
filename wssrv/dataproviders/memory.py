import logging
import asyncio
import json

from wssrv.core.repository import Repository
from wssrv.ws.handler import WebSocketHandler

log = logging.getLogger(__name__)


class Memory(Repository):
    def __init__(self, options_):
        self.options = options_
        self.queue = asyncio.Queue()
        self.publishers = []
        if 'publisher' in self.options:
            self._start_publishers()

    def _start_publishers(self):
        publisher_options = self.options['publisher'].get('options', None)
        loop = asyncio.get_event_loop()
        for i in range(0, publisher_options['threads']):
            task = loop.create_task(self._ws_publisher())
            self.publishers.append(task)

    async def _ws_publisher(self):
        while True:
            try:
                await WebSocketHandler.send_all(await self.get())
            except asyncio.CancelledError:
                log.info('Publisher task is canceled...')
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                log.exception(e, exc_info=False)
                await asyncio.sleep(1)

    @classmethod
    async def make(cls, options_):
        return cls(options_)

    async def add(self, request_object):
        try:
            await self.queue.put(json.dumps(request_object.data))
        except Exception as e:
            log.exception(e, exc_info=False)

    async def get(self):
        return await self.queue.get()
