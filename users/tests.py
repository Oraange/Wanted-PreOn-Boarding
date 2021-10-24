import jwt, json, bcrypt

from django.test import TestCase, Client

from users.models  import User
from my_settings   import SECRET_KEY

class SignUpViewTest(TestCase):
    def setUp(self):
        User.objects.create(
            nickname = "orange",
            password = "pass1234!@"
        )

    def tearDown(self):
        User.objects.all().delete()

    def test_SignUpView_post_success(self):
        client  = Client()
        sign_up = {
            "nickname" : "star123",
            "password" : "pass1234!@"
        }
        response = client.post('/user/sign-up', json.dumps(sign_up), content_type = 'application/json')
        self.assertEqual(response.json(), { "MESSAGE" : "CREATED" })
        self.assertEqual(response.status_code, 201)

    def test_SignUpView_post_user_already_exists(self):
        client  = Client()
        sign_up = {
            "nickname" : "orange",
            "password" : "pppp123!!!"
        }
        response = client.post('/user/sign-up', json.dumps(sign_up), content_type = 'application/json')
        self.assertEqual(response.json(), { "MESSAGE" : "DUPLICATED NICKNAME" })
        self.assertEqual(response.status_code, 409)

    def test_SignUpView_post_nickname_validation_error(self):
        client = Client()
        sign_up = {
            "nickname" : "o",
            "password" : "abcd123!@"
        }
        response = client.post('/user/sign-up', json.dumps(sign_up), content_type = 'application/json')
        self.assertEqual(response.json(), { "MESSAGE" : "NICKNAME ONLY CONTAIN 'alphabet' and 'number', ALSO LENGTH BETWEEN 3 ~ 15" })
        self.assertEqual(response.status_code, 400)

    def test_SignUpView_post_password_validation_error(self):
        client = Client()
        sign_up = {
            "nickname" : "mynick",
            "password" : "abc!!!!@@@@"
        }
        response = client.post('/user/sign-up', json.dumps(sign_up), content_type = 'application/json')
        self.assertEqual(response.json(), { "MESSAGE" : "PASSWORD MUST CONTAIN 'alphabet', 'number', 'special character', ALSO LENGTH BETWEEN 8 ~ 20" })
        self.assertEqual(response.status_code, 400)

    def test_SignUpView_post_key_error(self):
        client  = Client()
        sign_up = {
            "username" : "orange",
            "password" : "pppp123!!!"
        }
        response = client.post('/user/sign-up', json.dumps(sign_up), content_type = 'application/json')
        self.assertEqual(response.json(), { "MESSAGE" : "KEY ERROR" })
        self.assertEqual(response.status_code, 400)

    def test_SignUpView_post_type_error(self):
        client  = Client()
        sign_up = {
            "nickname" : 123,
            "password" : "pppp123!!!"
        }
        response = client.post('/user/sign-up', json.dumps(sign_up), content_type = 'application/json')
        self.assertEqual(response.json(), { "MESSAGE" : f"INPUT MUST BE STRING, INPUT TYPE IS {type(sign_up['nickname'])}" })
        self.assertEqual(response.status_code, 400)

class SignInViewTest(TestCase):
    def setUp(self):
        password = "pass1234!@"
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        decoded_pw = hashed_pw.decode("utf-8")
        user = User.objects.create(
            nickname = "orange",
            password = decoded_pw
        )

        self.token = jwt.encode({ "id" : user.id }, SECRET_KEY, algorithm = "HS256")

    def tearDown(self):
        User.objects.all().delete()

    def test_SignInView_post_success(self):
        client = Client()
        sign_in = {
            "nickname" : "orange",
            "password" : "pass1234!@"
        }
        response = client.post('/user/sign-in', json.dumps(sign_in), content_type = 'application/json')
        self.assertEqual(response.json(), {
            "MESSAGE" : "SUCCESS",
            "TOKEN"   : self.token })
        self.assertEqual(response.status_code, 200)

    def test_SignInView_post_login_error_nickname(self):
        client = Client()
        sign_in = {
            "nickname" : "orange123",
            "password" : "pass1234!@"
        }
        response = client.post('/user/sign-in', json.dumps(sign_in), content_type = 'application/json')
        self.assertEqual(response.json(), { "MESSAGE" : "LOGIN ERROR" })
        self.assertEqual(response.status_code, 401)

    def test_SignInView_post_login_error_password(self):
        client = Client()
        sign_in = {
            "nickname" : "orange",
            "password" : "pass1234@@!"
        }
        response = client.post('/user/sign-in', json.dumps(sign_in), content_type = 'application/json')
        self.assertEqual(response.json(), { "MESSAGE" : "LOGIN ERROR" })
        self.assertEqual(response.status_code, 401)

    def test_SignInView_post_key_error(self):
        client = Client()
        sign_in = {
            "username" : "orange",
            "password" : "pass1234##!"
        }
        response = client.post('/user/sign-in', json.dumps(sign_in), content_type = 'application/json')
        self.assertEqual(response.json(), { "MESSAGE" : "KEY ERROR" })
        self.assertEqual(response.status_code, 400)