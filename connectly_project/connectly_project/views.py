from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from accounts.views import is_admin


@login_required
@user_passes_test(is_admin)
def home(request):
    return render(request, 'home.html')
