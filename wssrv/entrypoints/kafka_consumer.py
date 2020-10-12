import json
import logging

from asyncio import CancelledError, sleep
from aiokafka import AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context
from wssrv.core.helpers import get_from_path
from wssrv.core.shared.event_object import EventObject
from wssrv.constants import LogTypes

log = logging.getLogger(__name__)


def _unpack_event(entrypoint, event) -> (EventObject, None):
    name_path = entrypoint.options['consumer']['events']['events_params']['name_path']
    events_array = entrypoint.options['consumer']['events']['events_array']
    event_name = get_from_path(event, name_path)
    if event_name is None or event_name not in events_array:
        return None
    return EventObject.make(event, event_name, events_array[event_name])


async def kafka_consumer(entrypoint, loop, use_cases):
    while True:
        try:
            context = create_ssl_context(
                cafile=entrypoint.options['consumer']['ssl']['ca'],
                certfile=entrypoint.options['consumer']['ssl']['cert'],
                keyfile=entrypoint.options['consumer']['ssl']['key'],
                password=entrypoint.options['consumer']['ssl']['password'],
            )
            consumer = AIOKafkaConsumer(
                bootstrap_servers=entrypoint.options['brokers'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id=entrypoint.options['consumer']['group_id'],
                loop=loop,
                security_protocol='SASL_SSL',
                ssl_context=context,
                sasl_mechanism=entrypoint.options['consumer']['sasl']['mechanism'],
                sasl_plain_username=entrypoint.options['consumer']['sasl']['username'],
                sasl_plain_password=entrypoint.options['consumer']['sasl']['password'],
            )
            consumer.subscribe(entrypoint.options['consumer']['topics'])
            await consumer.start()
            try:
                async for msg in consumer:
                    event_obj = _unpack_event(entrypoint, msg.value)
                    if event_obj is not None:
                        request_object = event_obj.make_request_object()
                        if not request_object:
                            if request_object is None:
                                continue
                            log.info({
                                'type': LogTypes.TYPE_EVENT,
                                'event_object': event_obj.to_dict(),
                                'request_object': request_object.errors,
                            }, {'event_name': 'wssrv.kafka_consumer.event.invalid'})
                            continue
                        await use_cases.execute(request_object)
            finally:
                await consumer.stop()
                await sleep(1)
        except CancelledError:
            log.info('Kafka consuming task is canceled...')
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            log.exception(e, exc_info=False)
            await sleep(1)
