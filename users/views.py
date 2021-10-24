import json, bcrypt, jwt

from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.views           import View
from django.http            import JsonResponse, response

from my_settings    import SECRET_KEY
from users.models   import User
from core.validator import VerifyNickname, VerifyPassword
from .repo          import IsUserExist
from .serializers   import UserSerializer

class SignUpView(APIView):

    serializer_class = UserSerializer
    @swagger_auto_schema(operation_description="회원가입", request_body = UserSerializer)
    def post(self, request, format = None):
        try:
            data = json.loads(request.body)

            nickname, password = data["nickname"], data["password"]

            if type(nickname) != str or type(password) != str:
                return JsonResponse({ "MESSAGE" : f"INPUT MUST BE STRING, INPUT TYPE IS {type(nickname)}" }, status = 400)
            
            if IsUserExist(nickname):
                return JsonResponse({ "MESSAGE" : "DUPLICATED NICKNAME" }, status = 409)

            if not VerifyNickname(nickname):
                return JsonResponse({ "MESSAGE" : "NICKNAME ONLY CONTAIN 'alphabet' and 'number', ALSO LENGTH BETWEEN 3 ~ 15" }, status = 400)
            
            if not VerifyPassword(password):
                return JsonResponse({ "MESSAGE" : "PASSWORD MUST CONTAIN 'alphabet', 'number', 'special character', ALSO LENGTH BETWEEN 8 ~ 20" }, status = 400)

            hashed_pw  = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            decoded_pw = hashed_pw.decode("utf-8")

            User.objects.create(
                nickname = nickname,
                password = decoded_pw
            )

            return JsonResponse({ "MESSAGE" : "CREATED" }, status = 201)

        except KeyError:
            return JsonResponse({ "MESSAGE" : "KEY ERROR" }, status = 400)

class SignInView(APIView):

    serializer_class = UserSerializer
    @swagger_auto_schema(operation_description="로그인", request_body = UserSerializer)
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            nickname, password = data["nickname"], data["password"]

            if not IsUserExist(nickname):
                return JsonResponse({ "MESSAGE" : "LOGIN ERROR"}, status = 401)

            user = User.objects.get(nickname = nickname)

            if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
                return JsonResponse({ "MESSAGE" : "LOGIN ERROR"}, status = 401)
            
            token = jwt.encode({"id" : user.id}, SECRET_KEY, algorithm = "HS256")

            return JsonResponse({ 
                "MESSAGE" : "SUCCESS",
                "TOKEN"   : token }, status = 200)

        except KeyError:
            return JsonResponse({ "MESSAGE" : "KEY ERROR" }, status = 400)