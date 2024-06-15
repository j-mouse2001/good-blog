from django.http import JsonResponse
import jwt
from django.conf import settings
from user.models import UserProfile

def login_check(func):

    def wrapper(request, *args, **kwargs):
        # get the token
        token = request.META.get('HTTP_AUTHORIZATION')
        # if the token does not exist, error 403
        if token == 'null':
            return JsonResponse({'code': 403, 'error': 'please log in first'})
        # error message: please log in

        # from the token to extract the logged-in user
        try:
            res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms=['HS256'])
        except Exception as e:
            print(f'jwt error is {e}')
            return JsonResponse({'code': 403, 'error': 'please log in'})

        username = res['username']
        user = UserProfile.objects.get(username=username)
        request.my_user = user
        return func(request, *args, **kwargs)

    return wrapper

