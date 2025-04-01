from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from accounts.forms import UserRegistrationForm
from accounts.models import CustomUser


def is_admin(user):
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    return render(request, 'manage_users.html')


@login_required()
def accounts_home(request):
    return render(request, 'home.html')


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm


# View for Register Page
def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")  # Adjust this to your actual register URL name

        # Proceed with user creation if passwords match
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully. You can now log in.")
        return redirect("login")  # Adjust this to your actual login URL name

    return render(request, "accounts/register.html")


# View for Login Page
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home after login
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')

    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

class CustomLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'  # Path relative to templates directory

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy('admin_dashboard')  # Redirect to admin dashboard
        else: # Route for the regular user, they can see latest posts(if authenticated)
            return reverse_lazy('latest_posts')  # Redirect to the posts feed
