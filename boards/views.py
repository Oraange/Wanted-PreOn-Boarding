import json

from django.http import JsonResponse
from django.views import View

from boards.models import Board

from core.auth import authentication

class BoardPostingView(View):
    @authentication
    def post(self, request):
        try:
            data = json.loads(request.body)

            title   = data["title"]
            content = data["content"]

            if title=="" or content=="":
                return JsonResponse({ "MESSAGE" : "PLEASE INPUT CONTENTS" }, status = 400)

            Board.objects.create(
                writer  = request.user,
                title   = title,
                content = content
            )

            return JsonResponse({ "MESSAGE" : "CREATED" }, status = 201)

        except KeyError:
            return JsonResponse({ "MESSAGE" : "KEY ERROR" }, status = 400)
        
        # except ValueError:
        #     return JsonResponse({ "MESSAGE" : "VALUE ERROR" }, status = 400)

class BoardListView(View):
    def get(self, request):
        LIMIT  = int(request.GET.get("limit", 4))
        OFFSET = int(request.GET.get("offset", 0)) * LIMIT

        boards = Board.objects.select_related('writer').order_by("-updated_at")[OFFSET : OFFSET + LIMIT]

        return JsonResponse({
            "RESULT" : [
                {
                    "id"           : board.id,
                    "writer"       : board.writer.nickname,
                    "title"        : board.title,
                    "content"      : board.content
                } for board in boards]
        }, status = 200)

class BoardView(View):
    def get(self, request, board_id):
        try:
            board = Board.objects.select_related('writer').get(id = board_id)
            
            return JsonResponse({
                "RESULT" : {
                    "created time" : board.created_at,
                    "updated time" : board.updated_at,
                    "id"     : board.id,
                    "writer" : board.writer.nickname,
                    "title"  : board.title,
                    "content" : board.content
                }
            }, status = 200)

        except Board.DoesNotExist:
            return JsonResponse({ "MESSAGE" : "BOARD DOES NOT EXIST" }, status = 400)

    @authentication
    def patch(self, request, board_id):
        try:
            data = json.loads(request.body)
            
            title   = data["title"]
            content = data["content"]

            board = Board.objects.get(id = board_id)

            if board.writer.id != request.user.id:
                return JsonResponse({ "MESSAGE" : "FORBIDDEN" }, status = 403)

            if title=="" or content=="":
                return JsonResponse({ "MESSAGE" : "PLEASE INPUT CONTENTS" }, status = 400)

            board.title   = title
            board.content = content
            board.save()

            return JsonResponse({ "MESSAGE" : "UPDATED" }, status = 201)

        except KeyError:
            return JsonResponse({ "MESSAGE" : "KEY ERROR" }, status = 400)

    @authentication
    def delete(self, request, board_id):
        try:
            board = Board.objects.get(id = board_id)

            if board.writer.id != request.user.id:
                return JsonResponse({ "MESSAGE" : "FORBIDDEN" }, status = 403)

            board.delete()

            return JsonResponse({ "MESSAGE" : "DELETED" }, status = 204)

        except Board.DoesNotExist:
            return JsonResponse({ "MESSAGE" : "BOARD DOES NOT EXIST"}, status = 400)

