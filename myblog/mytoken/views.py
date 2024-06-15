import jwt
from django.shortcuts import render
from django.http import JsonResponse
import json
from user.models import UserProfile
import hashlib
from django.conf import settings
import time


def make_tokens(username, expire=3600*24):
    key = settings.JWT_TOKEN_KEY
    time_now = time.time()
    payload_dict = {'username': username, 'exp': time_now + expire}
    return jwt.encode(payload_dict, key, algorithm='HS256')


# for login page token, error code from 10200-10299
def tokens(request):
    if request.method != 'POST':
        result = {'code': 10200, 'error': 'Please use POST request'}
        return JsonResponse(result)

    # check the username and password
    json_str = request.body
    json_obj = json.loads(json_str)

    username = json_obj['username']
    password = json_obj['password']

    # check if the user exists, if so, obtain the matching password, if not, return error
    existed_users = UserProfile.objects.filter(username=username)
    if not existed_users:
        return JsonResponse({'code': 10201, 'error': 'username or password is not correct'})
    else:
        user_password = existed_users[0].password
        pw = hashlib.md5()
        pw.update(password.encode())

        if user_password == pw.hexdigest():
            # if ok, return login successfully
            token = make_tokens(username)
            result = {'code': 200, 'username': username, 'data': {'token': token}}
            return JsonResponse(result)
        else:
            result = {'code': 10202, 'error': 'username or password is not correct'}
            return JsonResponse(result)