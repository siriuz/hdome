from django.shortcuts import render, get_object_or_404
from news.models import *

def bulletin(request):
    context = {'articles' : Article.objects.all() }
    return render(request, 'news/bulletin.html', context )

# Create your views here.
