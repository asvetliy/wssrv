import logging
import uuid

from tornado import websocket

log = logging.getLogger(__name__)


class WebSocketHandler(websocket.WebSocketHandler):
    listeners = set()

    def __init__(self, app, request):
        self.id = uuid.uuid4()
        super(WebSocketHandler, self).__init__(app, request)

    def check_origin(self, origin):
        return True

    @classmethod
    async def send_all(cls, message):
        log.debug({'action': 'send_all', 'message': message})
        for l in cls.listeners:
            l.write_message(message)

    def open(self, *args, **kwargs):
        log.debug(f'Listener({self.id}) connected...')
        self.listeners.add(self)
        log.info(f'Listeners count: {len(self.listeners)}')

    def on_close(self):
        log.debug(f'Listener({self.id}) disconnected...')
        self.listeners.remove(self)
        log.info(f'Listeners count: {len(self.listeners)}')

    def on_message(self, message):
        log.debug({'action': 'on_message', 'message': message})

    def on_ping(self, data: bytes) -> None:
        self.write_message('pong')
