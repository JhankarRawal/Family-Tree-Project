import zipfile
from io import BytesIO
from django.views import View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile

from apps.activitylog.utils import log_activity
from apps.families.models import Family
from apps.exports.utils import generate_family_tree_pdf, generate_gedcom
from .models import FamilyTreeExport

# --------------------------
# PDF Export
# --------------------------
class ExportPDFView(View):
    def get(self, request, family_id):
        family = get_object_or_404(Family, id=family_id)
        pdf_bytes = generate_family_tree_pdf(family)  # generate dynamically

        # Save to DB
        export = FamilyTreeExport.objects.create(
            family=family,
            exported_by=request.user,
            export_type="pdf"
        )
        export.file.save(f"family_{family.id}_tree.pdf", ContentFile(pdf_bytes))
        log_activity(
            family=family,
            user=request.user,
            action_type="export",
            target_type="family_tree",
            target_id=family.id,
            description="Exported family tree PDF"
        )

        # Return download
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="family_{family.id}_tree.pdf"'
        return response


class ExportGEDCOMView(View):
    def get(self, request, family_id):
        family = get_object_or_404(Family, id=family_id)
        gedcom_text = generate_gedcom(family)

        # Save to DB
        export = FamilyTreeExport.objects.create(
            family=family,
            exported_by=request.user,
            export_type="gedcom"
        )
        export.file.save(f"family_{family.id}.ged", ContentFile(gedcom_text))
        log_activity(
            family=family,
            user=request.user,
            action_type="export",
            target_type="gedcom",
            target_id=family.id,
            description="Exported GEDCOM file"
        )

        response = HttpResponse(gedcom_text, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="family_{family.id}.ged"'
        return response

# --------------------------
# ZIP Export (PDF + GEDCOM)
# --------------------------
class ExportZIPView(View):
    def get(self, request, family_id):
        family = get_object_or_404(Family, id=family_id)

        pdf_bytes = generate_family_tree_pdf(family)
        gedcom_text = generate_gedcom(family)

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w') as z:
            z.writestr(f"family_{family.id}_tree.pdf", pdf_bytes)
            z.writestr(f"family_{family.id}.ged", gedcom_text)
        buffer.seek(0)

        # Save to DB
        export = FamilyTreeExport.objects.create(
            family=family,
            exported_by=request.user,
            export_type="zip"
        )
        export.file.save(f"family_{family.id}_export.zip", ContentFile(buffer.getvalue()))
        log_activity(
            family=family,
            user=request.user,
            action_type="export",
            target_type="zip",
            target_id=family.id,
            description="Exported PDF + GEDCOM ZIP"
        )

        response = HttpResponse(buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="family_{family.id}_export.zip"'
        return response