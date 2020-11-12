from wssrv.ws.handler import WebSocketHandler

routes = [
    (r'/quotes', WebSocketHandler),
]
