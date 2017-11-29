from django.http import HttpResponse
from django.shortcuts import render_to_response
import time

def first_page(request):
    return HttpResponse("hello, my first page!")

def current_time(request):
    return HttpResponse("Current time is: "+time.strftime('%Y-%m-%d %H:%M:%S'))

def test(request):
    return HttpResponse("<html><body><p style='color:yellow'>hi</p></body></html>")

def test1(request):
    return render_to_response('test.html')

def test2(request):
    return render_to_response('index.html')

def default(request):
    return render_to_response()