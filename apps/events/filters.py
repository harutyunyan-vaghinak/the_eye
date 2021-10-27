from django_filters import FilterSet, filters

from apps.events.models import Event, EventCustomFields


class EventFilter(FilterSet):
    start_date = filters.DateFilter(field_name='timestamp__date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='timestamp__date', lookup_expr='lte')

    class Meta:
        model = Event
        fields = {
            'id': ['exact'],
            'session_id': ['exact'],
            'category': ['exact'],
            'name': ['exact']
        }


class EventCustomFieldsFilter(FilterSet):

    class Meta:
        model = EventCustomFields
        fields = {
            'id': ['exact'],
            'category': ['exact'],
            'name': ['exact']
        }
