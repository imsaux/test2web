from django.http import HttpResponse
from django.shortcuts import render_to_response
import time

def warning_page(request):
    return render_to_response('warning.html')

def stat_page(request):
    return render_to_response('stat.html')

