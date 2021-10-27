from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.events.filters import EventCustomFieldsFilter
from apps.events.models import EventCustomFields, Event
from apps.events.serializers import EventCustomFieldsSerializer, EventLogSerializer, EventSerializer


class EventCustomFieldsViewSet(ModelViewSet):
    queryset = EventCustomFields.objects.all().order_by('-modified')
    serializer_class = EventCustomFieldsSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_class = EventCustomFieldsFilter


class EventLogAPIView(APIView):
    serializer_class = EventLogSerializer

    @swagger_auto_schema(request_body=EventLogSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.event_log()
        return Response('Successfully created.', status.HTTP_200_OK)


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    http_method_names = ['get', 'delete']
    filter_class = EventCustomFieldsFilter
