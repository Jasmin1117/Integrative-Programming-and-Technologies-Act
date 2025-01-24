from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Post
from django.http import JsonResponse, HttpResponseNotAllowed

# Retrieve All Users (GET)
def get_users(request):
    try:
        users = list(User.objects.values('id', 'username', 'email', 'created_at'))
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Create a User (POST)
@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            # Parse JSON request body
            data = json.loads(request.body)
            
            # Validate required fields
            if 'username' not in data or 'email' not in data:
                return JsonResponse({'error': 'Username and email are required'}, status=400)
            
            # Create a new user
            user = User.objects.create(username=data['username'], email=data['email'])
            return JsonResponse({'id': user.id, 'message': 'User created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # Return a 405 Method Not Allowed response for non-POST requests
    return HttpResponseNotAllowed(['POST'])


# Retrieve All Posts (GET)
def get_posts(request):
    try:
        posts = list(Post.objects.values('id', 'content', 'author', 'created_at'))
        return JsonResponse(posts, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Create a Post (POST)
@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            author = User.objects.get(id=data['author'])
            post = Post.objects.create(content=data['content'], author=author)
            return JsonResponse({'id': post.id, 'message': 'Post created successfully'}, status=201)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Author not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

