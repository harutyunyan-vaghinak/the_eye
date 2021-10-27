from __future__ import absolute_import, unicode_literals

import json

from celery import shared_task
from the_eye.celery import app


@shared_task
def publish_message(message):
    message = json.loads(message.replace("\'", "\""))
    with app.producer_pool.acquire(block=True) as producer:
        producer.publish(
            message,
            exchange='exchange',
            routing_key='publish_key',
        )
