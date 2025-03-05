from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def admin_dashboard(request):
    if not request.user.is_admin():
        return redirect('/')  # Redirect non-admins to homepage
    return render(request, 'admin_dashboard.html')
