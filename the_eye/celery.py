from __future__ import absolute_import, unicode_literals
import os

import kombu
from celery import Celery, bootsteps

# set the default Django settings module for the 'celery' program.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'the_eye.settings')

app = Celery('the_eye')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
default_auto_field = 'django.db.models.AutoField'


# setting publisher
with app.pool.acquire(block=True) as conn:
    exchange = kombu.Exchange(
        name='exchange',
        type='direct',
        durable=True,
        channel=conn,
    )
    exchange.declare()

    queue = kombu.Queue(
        name='log_queue',
        exchange=exchange,
        routing_key='publish_key',
        channel=conn,
        message_ttl=600,
        queue_arguments={
            'x-queue-type': 'classic'
        },
        durable=True
    )
    queue.declare()


# setting consumer
class EyeConsumerStep(bootsteps.ConsumerStep):
    def get_consumers(self, channel):
        return [kombu.Consumer(channel,
                               queues=[queue],
                               callbacks=[self.handle_message],
                               accept=['json', 'pickle', 'msgpack'])]

    def handle_message(self, body, message):
        from apps.events.models import Event
        Event.objects.create(**body)
        message.ack()


app.steps['consumer'].add(EyeConsumerStep)
