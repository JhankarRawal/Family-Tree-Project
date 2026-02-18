from django.urls import path
from .views import (
    SaveVisualPDFView,
    ExportGEDCOMView,
    ExportCombinedZIPView,
)

app_name = "exports"

urlpatterns = [
    path("<int:family_id>/save-pdf/", SaveVisualPDFView.as_view(), name="save_pdf"),
    path("<int:family_id>/gedcom/", ExportGEDCOMView.as_view(), name="gedcom"),
    path("<int:family_id>/zip/", ExportCombinedZIPView.as_view(), name="zip"),
]
