from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from apps.core.serializer_fields import Base64FileField


class CustomFieldsValidation:

    def init(self, form_additional_fields, additional_fields):
        self.form_additional_fields = form_additional_fields
        self.additional_fields = additional_fields
        self._validate_form_data_keys()
        self.serializer_types = {
            'text': serializers.CharField,
            'choice': serializers.ChoiceField,
            'date': serializers.DateField,
            'file': Base64FileField
        }

    def validate_data(self, request_method=None):
        is_update = True if request_method and request_method.lower() == 'patch' else False
        self._generate_serializer(is_update)

    def _date_field(self, field):
        return self.serializer_types[field.field_type](
            format=field.field_configuration["date_format"],
            input_formats=[field.field_configuration["date_format"]],
            required=field.is_required
        )

    def _choice_field(self, field):
        return self.serializer_types[field.field_type](
            choices=field.field_configuration["choices"],
            required=field.is_required
        )

    def _file_field(self, field):
        return self.serializer_types[field.field_type](
            validators=[FileExtensionValidator(field.field_configuration["file_extensions"])],
            required=field.is_required
        )

    def _text_field(self, field):
        return self.serializer_types[field.field_type](
            required=field.is_required
        )

    def _generate_serializer(self, is_update=False):
        attributes = {}
        for field in self.form_additional_fields:
            if is_update:
                field.is_required = False
            attributes[field.field_name] = getattr(self, '_{}_field'.format(field.field_type))(field)

        serializer = type('CustomValidation', (serializers.Serializer, ), attributes)

        serializer = serializer(data=self.additional_fields)
        serializer.is_valid(raise_exception=True)

        self.validated_data = serializer.validated_data

    def _validate_form_data_keys(self):
        custom_fields_keys = self.form_additional_fields.values_list('field_name', flat=True)
        form_data_keys = self.additional_fields.keys()
        for key in form_data_keys:
            if key not in custom_fields_keys:
                raise serializers.ValidationError('Invalid key "{}" for custom field.'.format(key))


class EventCustomFieldsValidation:

    AVAILABLE_FORMATS = (
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%d/%m/%y',
        '%d-%m-%y',
        '%d/%m/%Y',
        '%d-%m-%Y',
    )

    # for this extensions we can also have a model for configure them.
    AVAILABLE_FILE_EXTENSIONS = [
        ".csv", ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx"
    ]

    def __init__(self, validated_data, **kwargs):
        self.validated_data = validated_data
        self.kwargs = kwargs
        self.field_configuration = validated_data.get("field_configuration", {})
        self.errors = {
            'field_configuration': {}
        }

    def validate(self):
        field_type = self.validated_data['field_type']
        if field_type == 'text':
            return

        if not self.field_configuration:
            self.errors["field_configuration"]["field_configuration"] = "Field configuration not set"

        if hasattr(self, '_check_{}'.format(field_type)):
            getattr(self, '_check_{}'.format(field_type))()

        return self.errors

    def _check_date(self):
        date_format = self.field_configuration.get("date_format")
        if not date_format:
            self.errors["field_configuration"]["date_format"] = 'Date format not set'
        if date_format not in self.AVAILABLE_FORMATS:
            self.errors["field_configuration"]["date_format"] = f'No valid date format found.'

    def _check_choice(self):
        choices = self.field_configuration.get("choices")
        if not choices:
            self.errors["field_configuration"]["choices"] = 'Choices not set'
        if not isinstance(choices, list):
            self.errors["field_configuration"]["choices"] = "Choices must be a list instance"

    def _check_file(self):
        file_extensions = self.field_configuration.get("file_extensions")
        if not file_extensions:
            self.errors["field_configuration"]["file_extensions"] = 'File extensions not set'
        if not isinstance(file_extensions, list):
            self.errors["field_configuration"]["file_extensions"] = "File extension must be a list of extensions like ['.pdf',...]"
        if file_extensions and not set(file_extensions).issubset(self.AVAILABLE_FILE_EXTENSIONS):
            self.errors["field_configuration"]["file_extensions"] = f"File extension can be " \
                                                                    f"{' '.join(str(f'{el},') for el in self.AVAILABLE_FILE_EXTENSIONS)}"
