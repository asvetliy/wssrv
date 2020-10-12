import logging
import asyncio
import uvloop
import os

from tornado import web, ioloop
from argparse import ArgumentParser
from wssrv.config import Config
from wssrv.core.use_cases.use_cases import UseCases
from wssrv.ws.routes import routes


def init_config() -> Config:
    parser = ArgumentParser(description='Service Notification')
    parser.add_argument(
        '-config',
        dest='filepath',
        required=False,
        help='config file path (default is ./config/main.[json])',
        metavar='./PATH/TO/FILE or $HOME/app/<FILE>.json',
        default=None
    )
    parsed_args = parser.parse_args()
    if parsed_args.filepath is not None:
        if not os.path.isfile(parsed_args.filepath):
            config_ = Config()
            log.warning(f'The file [{parsed_args.filepath}] does not exist!')
            return config_
        else:
            try:
                return Config(parsed_args.filepath)
            except Exception as e:
                log.exception(e, exc_info=False)
    return Config()


async def init_app(config_: Config) -> web.Application:
    repository = await config_.repo.make()
    use_cases = UseCases.make(repository)
    entrypoints = []

    for e in config_.entrypoints:
        t = e.start(use_cases)
        entrypoints.append({'type': e.type, 'threads': t})

    app_ = web.Application(routes)
    app_.config = config_
    app_.repository = repository
    app_.use_cases = use_cases
    app_.entrypoints = entrypoints
    app_.ws_clients = set()

    return app_

if __name__ == '__main__':
    log = logging.getLogger(__name__)
    uvloop.install()
    loop = asyncio.get_event_loop()
    config = init_config()
    app = loop.run_until_complete(init_app(config))
    app.listen(config.options['port'])
    try:
        ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        ioloop.IOLoop.current().stop()
