import json, bcrypt

from django.views import View
from django.http  import JsonResponse

from models         import User
from core.validator import VerifyPassword

class SignUpView(View):
    def post(self, request):
        data = json.loads(request.body)

        nickname, password = data["nickname"], data["password"]
        
        if User.objects.filter(nickname = nickname).exists():
            return JsonResponse({ "MESSAGE" : "DUPLICATED NICKNAME" }, status = 409)

        if not VerifyPassword(password):
            return JsonResponse({ "MESSAGE" : "VALIDATION ERROR" }, status = 400)

        hashed_pw  = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        decoded_pw = hashed_pw.decode("utf-8")

        User.objects.create(
            nickname = nickname,
            password = decoded_pw
        )

        return JsonResponse({ "MESSAGE" : "CREATED" }, status = 201)