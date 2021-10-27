from rest_framework import serializers

from apps.core.mixins import CustomFieldsValidation, EventCustomFieldsValidation
from apps.events import tasks

from apps.events.models import Event, EventCustomFields


class EventLogSerializer(serializers.HyperlinkedModelSerializer):

    def event_log(self):
        self._validate_payload()
        self.__log_data(payload=self.context['request'].data)

    def _validate_payload(self):
        fields = EventCustomFields.objects.filter(
            category=self.validated_data['category'],
            name=self.validated_data['name']
        )
        if not fields:
            return

        validated_fields = CustomFieldsValidation()
        validated_fields.init(fields, self.validated_data['data'])
        validated_fields.validate_data()

    def __log_data(self, payload):
        tasks.publish_message(str(payload))

    class Meta:
        model = Event
        fields = '__all__'


class EventCustomFieldsSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        self._validate_custom_fields()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._validate_custom_fields()
        return super().update(instance, validated_data)

    def _validate_custom_fields(self):
        field_validation = EventCustomFieldsValidation(validated_data=self.validated_data)
        errors = field_validation.validate()
        if field_validation.errors["field_configuration"]:
            raise serializers.ValidationError(errors)

    class Meta:
        model = EventCustomFields
        fields = '__all__'


class EventSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = '__all__'
