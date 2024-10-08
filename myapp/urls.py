from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("file-upload/", SummaryView.as_view(), name="file-upload"),
    path("summaries/", SummaryList.as_view(), name="summaries"),
    path("extract-data/", ExtractData.as_view(), name="extract-data"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)