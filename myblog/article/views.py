import json

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from tools.login_decorator import login_check
from .models import Article


# Create your views here.
class ArticleView(View):

    @method_decorator(login_check)
    def post(self, request, author_id):
        # obtain the author model from login_in info
        author = request.my_user

        # get data from the post request
        json_str = request.body
        json_obj = json.loads(json_str)

        content = json_obj['content']
        summary = json_obj['content_text'][:30]
        visibility = json_obj['limit']
        title = json_obj['title']
        category = json_obj['category']

        # check the visibility and category are acceptable
        if (category not in ['tec', 'no-tec']) or (visibility not in ['private', 'public']):
            return JsonResponse({'code': 10300, 'error': 'the input for visibility or category is not acceptable'})

        Article.objects.create(
            title=title, visibility=visibility,
            category=category, summary=summary,
            author=author, content=content
        )

        return JsonResponse({'code': 200})
