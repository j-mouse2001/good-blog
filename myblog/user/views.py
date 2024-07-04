import random

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import json
import random
from .models import UserProfile
import hashlib
from django.utils.decorators import method_decorator
from tools.login_decorator import login_check
from django.core.cache import cache
from tools.sms import YunTongXin
from django.conf import settings


# Create your views here.
class UserViews(View):
    def get(self, request, username=None):
        if username:
            try:
                user = UserProfile.objects.get(username=username)
                result = {'code': 200, 'username': username, 'data': {
                    'info': user.info,
                    'nickname': user.nickname,
                    'sign': user.motto,
                    'avatar': str(user.avatar)
                }}
                return JsonResponse(result)
            except Exception as e:
                result = {'code': 10102, 'error': 'The user does not exist'}
                return JsonResponse(result)

    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)

        username = json_obj['username']
        email = json_obj['email']
        password_1 = json_obj['password_1']
        password_2 = json_obj['password_2']
        phone = json_obj['phone']
        sms_num = json_obj['sms_num']

        # check if the input is correct for creating user
        if password_1 != password_2:
            return JsonResponse({'code': 10100, 'error': 'passwords entered are not the same'})

        # check if the verification code is correct
        correct_code = cache.get(f'sms_{phone}')
        if not correct_code or correct_code != sms_num:
            return JsonResponse({'code': 10200, 'error': 'verification code is wrong'})

        # check if the username is available
        existed_users = UserProfile.objects.filter(username=username)
        if existed_users:
            return JsonResponse({'code': 10101, 'error': 'username is already taken'})

        pw = hashlib.md5()
        pw.update(password_2.encode())

        # add the created user to db
        UserProfile.objects.create(
            username=username,
            nickname=username,
            password=pw.hexdigest(),
            email=email,
            phone=phone
        )

        result = {'code': 200, 'username': username, 'data': {}}
        return JsonResponse(result)

    # put method for UserViews
    @method_decorator(login_check)
    def put(self, request, username=None):
        # get the json string from client and loads to json
        json_str = request.body
        json_obj = json.loads(json_str)

        # get the user from logged-in token
        user = request.my_user

        # replace the field of user object
        user.nickname = json_obj['nickname']
        user.motto = json_obj['sign']
        user.info = json_obj['info']
        user.save()
        return JsonResponse({'code': 200})


@login_check
def users_avatar(request, username):

    # get the user
    if request.method != 'POST':
        result = {'code': 10103, 'error': 'please use a POST request'}
        return JsonResponse(result)

    user = request.my_user

    # get the new avatar from request and save it to user
    new_avatar = request.FILES['avatar']
    user.avatar = new_avatar
    user.save()

    return JsonResponse({'code': 200})


def send_sms(phone, code):
    obj = YunTongXin(
        settings.ACCOUNT_SID,
        settings.ACCOUNT_TOKEN,
        settings.APP_ID,
        settings.TEMPLATE_ID
    )
    res = obj.run(phone, code)
    return res


def sms_view(request):
    if request.method != 'POST':
        result = {'code': 10108, 'error': 'please use a POST request'}
        return JsonResponse(result)

    # get the phone number from post data
    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj['phone']

    # generate a random 4 digit code
    code = str(random.randint(1000, 9999))

    # create phone code pair and save them in redis
    cache_key = f'sms_{phone}'

    # check if there is a code sent to this number and is not expired
    possible_code = cache.get(cache_key)
    if possible_code:
        return JsonResponse({'code': 10201, 'error': 'The code has already sent to this number'})

    # save the number and corresponding code to cache
    cache_val = code
    cache.set(cache_key, cache_val, timeout=300)

    # send the sms
    sms_res = json.loads(send_sms(phone, code))
    if sms_res['statusCode'] != '000000':
        return JsonResponse({'code': 10109, 'error': 'sms message send failed'})

    return JsonResponse({'code': 200})
