import random

from django.db import models

def default_motto():
    mottos = ['Dream big, work hard, stay focused.', 'Live, laugh, love.', 'Kindness is always fashionable.']
    return random.choice(mottos)


# Create your models here.
class UserProfile(models.Model):
    username = models.CharField(max_length=11, verbose_name='username', primary_key=True)
    nickname = models.CharField(max_length=30, verbose_name='nickname')
    password = models.CharField(max_length=32)
    email = models.EmailField()
    phone = models.CharField(max_length=11)
    avatar = models.ImageField(upload_to='avatar', null=True)
    motto = models.CharField(max_length=50, verbose_name='personal motto', default=default_motto)
    info = models.CharField(max_length=500, default='')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_user_profile'
