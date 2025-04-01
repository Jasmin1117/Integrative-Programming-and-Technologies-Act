from django.shortcuts import render


def home(request):
    # use the root theme
    return render(request, 'home.html')
