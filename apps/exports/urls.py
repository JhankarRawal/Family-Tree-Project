from django.urls import path
from .views import (
    ExportPDFView,
    ExportGEDCOMView,
    ExportZIPView,
)

app_name = "exports"

urlpatterns = [
    path("save-pdf/", ExportPDFView.as_view(), name="save_pdf"),
    path("gedcom/", ExportGEDCOMView.as_view(), name="gedcom"),
    path("zip/", ExportZIPView.as_view(), name="zip"),
]