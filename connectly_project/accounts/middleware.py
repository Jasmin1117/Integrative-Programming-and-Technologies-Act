from django.http import JsonResponse


def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return JsonResponse({'error': 'Permission denied'}, status=403)

        return wrapper

    return decorator
