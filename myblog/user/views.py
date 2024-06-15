from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import json
from .models import UserProfile
import hashlib
from django.utils.decorators import method_decorator
from tools.login_decorator import login_check


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

        # check if the input is correct for creating user
        if password_1 != password_2:
            return JsonResponse({'code': 10100, 'error': 'passwords entered are not the same'})

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

