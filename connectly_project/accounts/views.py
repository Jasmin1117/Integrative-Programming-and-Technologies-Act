from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from accounts.models import CustomUser
from posts.models import Post, Comment, Like


def is_admin(user):
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with statistics and overview"""
    # Get statistics
    total_users = CustomUser.objects.count()
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    total_likes = Like.objects.count()
    
    # Get recent activities
    recent_activities = []
    
    # Recent posts
    recent_posts = Post.objects.select_related('created_by').order_by('-created_at')[:5]
    for post in recent_posts:
        recent_activities.append({
            'icon': '📝',
            'description': f'New post "{post.title or post.content[:30]}" by {post.created_by.username}',
            'time': post.created_at.strftime('%b %d, %Y at %I:%M %p')
        })
    
    # Recent comments
    recent_comments = Comment.objects.select_related('user', 'post').order_by('-created_at')[:5]
    for comment in recent_comments:
        recent_activities.append({
            'icon': '💬',
            'description': f'New comment by {comment.user.username} on post "{comment.post.title or comment.post.content[:30]}"',
            'time': comment.created_at.strftime('%b %d, %Y at %I:%M %p')
        })
    
    # Recent user registrations
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    for user in recent_users:
        recent_activities.append({
            'icon': '👤',
            'description': f'New user {user.username} joined',
            'time': user.date_joined.strftime('%b %d, %Y at %I:%M %p')
        })
    
    # Sort activities by time (most recent first)
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:10]  # Limit to 10 most recent
    
    context = {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_likes': total_likes,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """Manage users with search, filtering, and pagination"""
    users = CustomUser.objects.annotate(
        post_count=Count('posts')
    ).order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(role__icontains=search_query)
        )
    
    # Role filter
    role_filter = request.GET.get('role_filter', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Status filter
    status_filter = request.GET.get('status_filter', '')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 20)  # 20 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'total_users': users.count(),
    }
    
    return render(request, 'accounts/manage_users.html', context)


@login_required
@user_passes_test(is_admin)
def admin_posts(request):
    """Manage posts with search, filtering, and pagination"""
    posts = Post.objects.select_related('created_by').prefetch_related('likes', 'comments').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(created_by__username__icontains=search_query)
        )
    
    # Type filter
    type_filter = request.GET.get('type_filter', '')
    if type_filter:
        posts = posts.filter(post_type=type_filter)
    
    # Privacy filter
    privacy_filter = request.GET.get('privacy_filter', '')
    if privacy_filter:
        posts = posts.filter(privacy=privacy_filter)
    
    # Pagination
    paginator = Paginator(posts, 15)  # 15 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'total_posts': posts.count(),
    }
    
    return render(request, 'accounts/admin_posts.html', context)


@login_required
@user_passes_test(is_admin)
def admin_comments(request):
    """Manage comments with search, filtering, and pagination"""
    comments = Comment.objects.select_related('user', 'post').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        comments = comments.filter(
            Q(text__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(post__title__icontains=search_query) |
            Q(post__content__icontains=search_query)
        )
    
    # Post filter
    post_filter = request.GET.get('post_filter', '')
    if post_filter:
        comments = comments.filter(post_id=post_filter)
    
    # User filter
    user_filter = request.GET.get('user_filter', '')
    if user_filter:
        comments = comments.filter(user_id=user_filter)
    
    # Pagination
    paginator = Paginator(comments, 20)  # 20 comments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available posts and users for filters
    available_posts = Post.objects.values('id', 'title', 'content')[:100]  # Limit to 100 for performance
    available_users = CustomUser.objects.values('id', 'username')[:100]  # Limit to 100 for performance
    
    context = {
        'comments': page_obj,
        'total_comments': comments.count(),
        'available_posts': available_posts,
        'available_users': available_users,
    }
    
    return render(request, 'accounts/admin_comments.html', context)


@login_required()
@user_passes_test(is_admin)
def accounts_home(request):
    return render(request, 'home.html')


# API Views for AJAX operations
@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def get_user_api(request, user_id):
    """Get user data for editing"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def update_user_api(request, user_id):
    """Update user data"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        data = json.loads(request.body)
        
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        
        user.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def deactivate_user_api(request, user_id):
    """Deactivate a user"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        if user != request.user:  # Prevent admin from deactivating themselves
            user.is_active = False
            user.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Cannot deactivate yourself'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def activate_user_api(request, user_id):
    """Activate a user"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        user.is_active = True
        user.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def delete_user_api(request, user_id):
    """Delete a user"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        if user != request.user:  # Prevent admin from deleting themselves
            user.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Cannot delete yourself'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# View for Register Page
def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully. You can now log in.")
        return redirect("login")

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
                if user.is_superuser:
                    return redirect('admin_dashboard')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')

    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})
