import base64
import zipfile
from io import BytesIO
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile

from apps.families.models import Family
from apps.activitylog.utils import log_activity
from .models import FamilyTreeExport
from .utils import generate_gedcom


class SaveVisualPDFView(View):
    def post(self, request, family_id):
        family = get_object_or_404(Family, id=family_id)

        pdf_data = request.POST.get("pdf")
        decoded = base64.b64decode(pdf_data.split(",")[1])

        export = FamilyTreeExport.objects.create(
            family=family,
            exported_by=request.user,
            export_type="pdf"
        )

        export.file.save(
            f"family_{family.id}_tree.pdf",
            ContentFile(decoded)
        )

        log_activity(
            family=family,
            user=request.user,
            action_type="export",
            target_type="family_tree",
            target_id=family.id,
            description="Exported visual family tree PDF"
        )

        return JsonResponse({"status": "saved"})

class ExportGEDCOMView(View):
    def get(self, request, family_id):
        family = get_object_or_404(Family, id=family_id)
        gedcom = generate_gedcom(family)

        export = FamilyTreeExport.objects.create(
            family=family,
            exported_by=request.user,
            export_type="gedcom"
        )

        export.file.save(
            f"family_{family.id}.ged",
            ContentFile(gedcom)
        )

        log_activity(
            family=family,
            user=request.user,
            action_type="export",
            target_type="gedcom",
            target_id=family.id,
            description="Exported GEDCOM file"
        )

        response = HttpResponse(gedcom, content_type="application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="family_{family.id}.ged"'
        return response


class ExportCombinedZIPView(View):
    def post(self, request, family_id):
        family = get_object_or_404(Family, id=family_id)

        pdf_data = request.POST.get("pdf")
        pdf_bytes = base64.b64decode(pdf_data.split(",")[1])
        gedcom_text = generate_gedcom(family)

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("family_tree.pdf", pdf_bytes)
            z.writestr("family_tree.ged", gedcom_text)

        export = FamilyTreeExport.objects.create(
            family=family,
            exported_by=request.user,
            export_type="zip"
        )

        export.file.save(
            f"family_{family.id}_export.zip",
            ContentFile(buffer.getvalue())
        )

        log_activity(
            family=family,
            user=request.user,
            action_type="export",
            target_type="zip",
            target_id=family.id,
            description="Exported PDF + GEDCOM ZIP"
        )

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/zip"
        )
        response["Content-Disposition"] = f'attachment; filename="family_{family.id}_export.zip"'
        return response

