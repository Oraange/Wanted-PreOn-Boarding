import json

from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from django.http  import JsonResponse, HttpResponse
from django.views import View

from boards.models import Board
from core.auth     import authentication
from .serializers  import BoardSerializer

class BoardPostingView(APIView):
    """
    # 게시글 작성
    """
    serializer_class = BoardSerializer
    parameter_token = openapi.Parameter (
                                        "Authorization", 
                                        openapi.IN_HEADER, 
                                        description = "access_token", 
                                        type        = openapi.
                                        TYPE_STRING
    )
    @swagger_auto_schema(
        request_body = BoardSerializer,
        manual_parameters = [parameter_token]
    )
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

class BoardListView(APIView):
    """
    # 게시글 전체 조회
    """

    def get(self, request):
        LIMIT  = int(request.GET.get("limit", 4))
        OFFSET = int(request.GET.get("offset", 0)) * LIMIT

        boards = Board.objects.select_related('writer').order_by("-updated_at")[OFFSET : OFFSET + LIMIT]

        return JsonResponse({
            "RESULT" : [
                {
                    "updated time" : board.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "id"           : board.id,
                    "writer"       : board.writer.nickname,
                    "title"        : board.title,
                } for board in boards]
        }, status = 200)

class BoardView(APIView):
    """
    # 게시글 상세 조회
    """

    def get(self, request, board_id):
        try:
            board = Board.objects.select_related('writer').get(id = board_id)
            
            return JsonResponse({
                "RESULT" : {
                    "content"      : board.content,
                    "id"           : board.id,
                    "title"        : board.title,
                    "updated time" : board.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "writer"       : board.writer.nickname,
                }
            }, status = 200)

        except Board.DoesNotExist:
            return JsonResponse({ "MESSAGE" : "BOARD DOES NOT EXIST" }, status = 400)

    """
    # 게시글 수정
    """
    serializer_class = BoardSerializer
    parameter_token = openapi.Parameter (
                                        "Authorization", 
                                        openapi.IN_HEADER, 
                                        description = "access_token", 
                                        type        = openapi.TYPE_STRING
    )
    @swagger_auto_schema(
        request_body = BoardSerializer,
        manual_parameters = [parameter_token]
    )
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

    """
    # 게시글 삭제
    """
    serializer_class = BoardSerializer
    parameter_token = openapi.Parameter (
                                        "Authorization", 
                                        openapi.IN_HEADER, 
                                        description = "access_token", 
                                        type        = openapi.
                                        TYPE_STRING
    )
    @swagger_auto_schema(
        manual_parameters = [parameter_token]
    )
    @authentication
    def delete(self, request, board_id):
        try:
            board = Board.objects.get(id = board_id)

            if board.writer.id != request.user.id:
                return JsonResponse({ "MESSAGE" : "FORBIDDEN" }, status = 403)

            board.delete()

            return HttpResponse(status = 204)

        except Board.DoesNotExist:
            return JsonResponse({ "MESSAGE" : "BOARD DOES NOT EXIST"}, status = 400)

