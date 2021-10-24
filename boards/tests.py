from django.http import request, response
import jwt, json
from datetime import datetime

from django.test import TestCase, Client

from boards.models import Board
from users.models  import User
from my_settings   import SECRET_KEY

class BoardCreateTest(TestCase):
    def setUp(self):
        user = User.objects.create(
            nickname = "orange",
            password = "pass1234!@"
        )

        self.token = jwt.encode({ "id" : user.id }, SECRET_KEY, algorithm = "HS256")

    def tearDown(self):
        User.objects.all().delete()
        Board.objects.all().delete()

    def test_BoardPostingView_post_success(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token }
        board_data = {
            "title"   : "게시판 등록",
            "content" : "내용을 입력해 주세요."
        }
        response = client.post('/boards/write', json.dumps(board_data), content_type = "application/json", **header)
        self.assertEqual(response.json(), { "MESSAGE" : "CREATED" })
        self.assertEqual(response.status_code, 201)
        
    def test_BoardPostingView_post_empty_input_title(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token }
        board_data = {
            "title"   : "",
            "content" : "내용을 입력해 주세요."
        }
        response = client.post('/boards/write', json.dumps(board_data), content_type = "application/json", **header)
        self.assertEqual(response.json(), { "MESSAGE" : "PLEASE INPUT CONTENTS" })
        self.assertEqual(response.status_code, 400)

    def test_BoardPostingView_post_empty_input_content(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token }
        board_data = {
            "title"   : "게시판 등록",
            "content" : ""
        }
        response = client.post('/boards/write', json.dumps(board_data), content_type = "application/json", **header)
        self.assertEqual(response.json(), { "MESSAGE" : "PLEASE INPUT CONTENTS" })
        self.assertEqual(response.status_code, 400)

    def test_BoardPostingView_post_key_error(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token }
        board_data = {
            "titel"   : "게시판 등록",
            "content" : "내용을 입력해 주세요."
        }
        response = client.post('/boards/write', json.dumps(board_data), content_type = "application/json", **header)
        self.assertEqual(response.json(), { "MESSAGE" : "KEY ERROR" })
        self.assertEqual(response.status_code, 400)

class BoardReadTest(TestCase):
    def setUp(self):
        user = User.objects.create(
            nickname = "orange",
            password = "pass1234!@"
        )

        Board.objects.bulk_create(
            [
                Board(
                    writer  = user,
                    title   = f"{i}번째 게시글",
                    content = "내용을 입력해 주세요."
                ) for i in range(1, 21)
            ]
        )

    def tearDown(self):
        User.objects.all().delete()
        Board.objects.all().delete()

    def test_BoardListView_get_success(self):
        client   = Client()
        response = client.get('/boards?offset=0&limit=4')

        time_list = [t.updated_at for t in Board.objects.all()][:4]

        self.maxDiff = None
        self.assertEqual(response.json(), {
            "RESULT" : [
                {
                    "id"           : i,
                    "title"        : f"{i}번째 게시글",
                    "updated time" : update_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "writer"       : "orange",
                } for i, update_time in zip(range(20, 16, -1), time_list)
            ]
        })
        self.assertEqual(response.status_code, 200)

    def test_BoardView_get_success(self):
        client   = Client()
        response = client.get('/boards/1')

        updated_time = Board.objects.get(id = 1).updated_at
        self.assertEqual(response.json(), {
            "RESULT" : {
                "id"           : 1,
                "title"        : "1번째 게시글",
                "content"      : "내용을 입력해 주세요.",
                "writer"       : "orange",
                "updated time" : updated_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
        self.assertEqual(response.status_code, 200)

    def test_BoardView_get_board_does_not_exist(self):
        client   = Client()
        response = client.get('/boards/100')

        self.assertEqual(response.json(), {
            "MESSAGE" : "BOARD DOES NOT EXIST"
        })
        self.assertEqual(response.status_code, 400)

class BoardUpdateAndDeleteTest(TestCase):
    def setUp(self):
        user_1 = User.objects.create(
            nickname = "orange",
            password = "pass1234!@"
        )

        user_2 = User.objects.create(
            nickname = "strawberry",
            password = "star1234!@"
        )

        Board.objects.create(
            writer  = user_1,
            title   = "1번째 게시글",
            content = "내용을 입력해 주세요."
        )

        self.token1 = jwt.encode({ "id" : user_1.id }, SECRET_KEY, algorithm = "HS256")
        self.token2 = jwt.encode({ "id" : user_2.id }, SECRET_KEY, algorithm = "HS256")
        
    def tearDown(self) -> None:
        User.objects.all().delete()
        Board.objects.all().delete()

    def test_BoardView_patch_success(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token1 }
        board_data = {
            "title"   : "수정된 1번째 게시글",
            "content" : "수정된 내용을 입력해 주세요."
        }
        response = client.patch('/boards/1', json.dumps(board_data), content_type = "application/josn", **header)
        self.assertEqual(response.json(), {
            "MESSAGE" : "UPDATED"
        })
        self.assertEqual(response.status_code, 201)

    def test_BoardView_patch_forbidden(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token2 }
        board_data = {
            "title"   : "수정된 1번째 게시글",
            "content" : "수정된 내용을 입력해 주세요."
        }
        response = client.patch('/boards/1', json.dumps(board_data), content_type = "application/josn", **header)
        self.assertEqual(response.json(), {
            "MESSAGE" : "FORBIDDEN"
        })
        self.assertEqual(response.status_code, 403)

    def test_BoardView_patch_input_error_title(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token1 }
        board_data = {
            "title"   : "",
            "content" : "수정된 내용을 입력해 주세요."
        }
        response = client.patch('/boards/1', json.dumps(board_data), content_type = "application/josn", **header)
        self.assertEqual(response.json(), {
            "MESSAGE" : "PLEASE INPUT CONTENTS"
        })
        self.assertEqual(response.status_code, 400)

    def test_BoardView_patch_input_error_content(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token1 }
        board_data = {
            "title"   : "수정된 1번째 게시글",
            "content" : ""
        }
        response = client.patch('/boards/1', json.dumps(board_data), content_type = "application/josn", **header)
        self.assertEqual(response.json(), {
            "MESSAGE" : "PLEASE INPUT CONTENTS"
        })
        self.assertEqual(response.status_code, 400)

    def test_BoardView_patch_key_error(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token1 }
        board_data = {
            "titel"   : "수정된 1번째 게시글",
            "content" : ""
        }
        response = client.patch('/boards/1', json.dumps(board_data), content_type = "application/josn", **header)
        self.assertEqual(response.json(), {
            "MESSAGE" : "KEY ERROR"
        })
        self.assertEqual(response.status_code, 400)

    def test_BoardView_delete_success(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token1 }
        
        response = client.delete('/boards/1', **header)
        self.assertEqual(response.status_code, 204)

    def test_BoardView_delete_forbidden(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token2 }

        response = client.delete('/boards/1', **header)
        self.assertEqual(response.json(), {
            "MESSAGE" : "FORBIDDEN"
        })
        self.assertEqual(response.status_code, 403)

    def test_BoardView_delete_board_does_not_exist(self):
        client     = Client()
        header     = { "HTTP_Authorization" : self.token1 }

        response = client.delete('/boards/100', **header)
        self.assertEqual(response.json(), {
            "MESSAGE" : "BOARD DOES NOT EXIST"
        })
        self.assertEqual(response.status_code, 400)