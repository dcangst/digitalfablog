import functools
# django
from django.http import JsonResponse


def ajax_login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        return JsonResponse('Unauthorized', status=401, safe=False)

    return wrapper
