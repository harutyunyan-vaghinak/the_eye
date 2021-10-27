import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.core.mixins import CustomFieldsValidation
from apps.events.models import EventCustomFields, Event
from apps.events.tests.base_64_string import base_64_simple_string

def get_payloads_event_custom_fields():
    text_payload = {
        "field_name": "text_field",
        "is_required": False,
        "display_name": "string",
        "field_type": "text",
        "field_configuration": {},
        "category": "text",
        "name": "string"
    }
    date_payload = {
        "field_name": "date_field",
        "is_required": False,
        "display_name": "string",
        "field_type": "date",
        "field_configuration": {
            "date_format": '%Y-%m-%d'
        },
        "category": "date",
        "name": "string"
    }
    choices_payload = {
        "field_name": "choice_field",
        "is_required": False,
        "display_name": "string",
        "field_type": "choice",
        "field_configuration": {
            "choices": [
                "choice_1", "choice_2", "choice_3"
            ]
        },
        "category": "choice",
        "name": "string"
    }
    file_payload = {
        "field_name": "file_field",
        "is_required": False,
        "display_name": "string",
        "field_type": "file",
        "field_configuration": {
            "file_extensions": [
                "pdf", "doc", "docx"
            ]
        },
        "category": "file",
        "name": "string"
    }
    return [text_payload, date_payload, choices_payload, file_payload]

class EventTestCase(TestCase):
    def test_event(self):
        payload = {
            "session_id": "string",
            "name": "string",
            "category": "string",
            "data": {},
            "timestamp": "2021-10-27T07:19:19.261Z"
        }
        event = Event.objects.create(**payload)
        url = reverse('event-detail', kwargs={'pk': event.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EventCustomFieldsTestCase(TestCase):

    def test_custom_fields_text(self):
        payloads = get_payloads_event_custom_fields()
        for payload in payloads:
            field = EventCustomFields.objects.create(**payload)
            url = reverse('eventcustomfields-detail', kwargs={'pk': field.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class EventLogTestCase(TestCase):
    def test_event_log(self):
        custom_fields_payloads = get_payloads_event_custom_fields()
        payloads_with_data_validation = self.__get_event_log_payload()
        categories = set()
        names = set()
        for payload in custom_fields_payloads:
            categories.add(payload['category'])
            names.add(payload['name'])
            field = EventCustomFields.objects.create(**payload)
            url = reverse('eventcustomfields-detail', kwargs={'pk': field.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        fields = EventCustomFields.objects.filter(
            category__in=categories,
            name__in=names
        )
        validated_fields = CustomFieldsValidation()
        for payload in payloads_with_data_validation:
            validated_fields.init(fields, payload['data'])
            validated_fields.validate_data()
            self.assertRaises(ValidationError)

    def __get_event_log_payload(self):
        payloads_with_data_validation = [
            {
                "session_id": "string",
                "name": "text_field",
                "category": "text",
                "data": {},
                "timestamp": "2021-10-27T07:19:19.261Z"
            },
            {
                "session_id": "string",
                "name": "date_field",
                "category": "date",
                "data": {
                    "date_field": datetime.datetime.now().strftime('%Y-%m-%d')
                },
                "timestamp": "2021-10-27T07:19:19.261Z"
            },
            {
                "session_id": "string",
                "name": "choice_field",
                "category": "choice",
                "data": {
                    "choice_field": "choice_2"
                },
                "timestamp": "2021-10-27T07:19:19.261Z"
            },
            {
                "session_id": "string",
                "name": "file_field",
                "category": "file",
                'data': {"file_field": base_64_simple_string()},
                "timestamp": "2021-10-27T07:19:19.261Z"
            }
        ]
        return payloads_with_data_validation
