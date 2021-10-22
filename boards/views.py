import json
from django.http.response import JsonResponse

from django.views import View
from boards.models import Board

from core.auth import authentication

class BoardView(View):
    @authentication
    def post(self, request):
        try:
            data = json.loads(request.body)

            title   = data["title"]
            content = data["content"]

            Board.objects.create(
                writer  = request.user,
                title   = title,
                content = content
            )

            return JsonResponse({ "MESSAGE" : "CREATED" }, status = 201)

        except KeyError:
            return JsonResponse({ "MESSAGE" : "KEY ERROR" }, status = 400)
        
        except ValueError:
            return JsonResponse({ "MESSAGE" : "VALUE ERROR" }, status = 400)

    # def get(self, request):
    #     try:
    #         OFFSET = int(request.GET.get("offset", 0))
    #         LIMIT  = int(request.GET.get("limit", 0))

