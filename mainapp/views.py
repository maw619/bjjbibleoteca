from django.shortcuts import render
from .models import Category

def video_dropdown(request):
    categories = Category.objects.prefetch_related("sections__videos")
    for x in categories:
        print(x)
    return render(request, 'videos.html', {
        'categories': categories
    })