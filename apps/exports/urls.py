from django.urls import path
from django.http import HttpResponse

def export_pdf_list(request): return HttpResponse("Export PDF list")

app_name = 'exports'

urlpatterns = [
    path('', export_pdf_list, name='export_pdf_list'),
]
