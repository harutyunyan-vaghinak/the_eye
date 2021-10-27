from django.conf.urls import url

from apps.core.routers import DefaultRouter
from apps.events.views import EventViewSet, EventLogAPIView, EventCustomFieldsViewSet

router = DefaultRouter()

urlpatterns = [
    url(r'log-event/', EventLogAPIView.as_view()),
]

router.register(r'events/custom-fields', EventCustomFieldsViewSet)
router.register(r'events', EventViewSet)

