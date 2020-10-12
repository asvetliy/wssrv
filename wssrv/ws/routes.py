from wssrv.ws.handler import WebSocketHandler

routes = [
    (r'/ws', WebSocketHandler),
]
