from django.http import HttpResponse
from django.shortcuts import render_to_response
import time

def main_page(request):
    return render_to_response('index.html')

def data_handle(request):
    return render_to_response('data.html')

