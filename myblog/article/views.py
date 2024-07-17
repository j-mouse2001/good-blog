import json

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from tools.login_decorator import login_check, get_user_by_request
from .models import Article
from user.models import UserProfile


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

    def make_articles(self, author, author_articles):
        article_list = []
        for article in author_articles:
            dic = {}
            dic['id'] = article.id
            dic['title'] = article.title
            dic['category'] = article.category
            dic['created_time'] = article.created_time.strftime("%Y-%m-%d% %H:%M:%S")
            dic['summary'] = article.summary
            dic['author'] = author.nickname

            article_list.append(dic)

        data = {'articles': article_list, 'nickname': author.nickname}
        res = {'code': 200, 'data': data}
        return res

    def get(self, request, author_id):

        # check if the author exist
        try:
            author = UserProfile.objects.get(username=author_id)
        except Exception as e:
            result = {'code': 10301, 'error': 'author does not exist'}
            return JsonResponse(result)

        visitor_username = get_user_by_request(request)

        # get the category if we have one
        category = request.GET.get('category')

        if category in ['tec', 'no-tec']:
            # the author is checking his articles
            if visitor_username == author_id:
                author_articles = Article.objects.filter(author_id=author_id, category=category)
            else:
                author_articles = Article.objects.filter(author_id=author_id, visibility='public', category=category)
        else:
            if visitor_username == author_id:
                author_articles = Article.objects.filter(author_id=author_id)
            else:
                author_articles = Article.objects.filter(author_id=author_id, visibility='public')

        res = self.make_articles(author, author_articles)

        return JsonResponse(res)

