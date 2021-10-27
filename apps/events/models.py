from django.db import models
from django.db.models import JSONField

from apps.core.models import AbstractBaseModel


class Event(models.Model):
    session_id = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, db_index=True)
    data = JSONField(default=dict)
    timestamp = models.DateTimeField(db_index=True)


class EventCustomFields(AbstractBaseModel):

    CHOICES = (
        ('text', 'Text'),
        ('file', 'File'),
        ('date', 'Date'),
        ('choice', 'Choice'),
    )
    field_name = models.CharField(max_length=255)
    is_required = models.BooleanField(default=True)
    display_name = models.CharField(max_length=255)
    field_type = models.CharField(choices=CHOICES, max_length=255)
    field_configuration = JSONField(default=dict)
    category = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('category', 'name')

