from django.http import HttpResponse
from django.shortcuts import render
# def home(request):
#     return HttpResponse("<h1>Homepage works!</h1>")

def home(request):
    return render(request,'Home/home.html')

def features(request):
    return render(request,'Home/features.html')
def about(request):
    return render(request,'Home/about.html')

def contact(request):
    return render(request,'Home/contact.html')
def HowItWorks(request):
    return render(request,'Home/How it works.html')

def privacy(request):
    return render(request,'Home/privacy.html')
def technology(request):
    tech_list = [
        ('Django (Backend)', 95),
        ('PostgreSQL (Database)', 90),
        ('D3.js (Visualization)', 88),
        ('ReportLab (PDF Export)', 85),
        ('Django Auth (Security)', 92),
        ('PG Full-Text Search', 87),
        ]
    return render(request, 'Home/technology.html', {'tech_list': tech_list})
def blogs(request):
    return render(request,'Home/blogs.html')
