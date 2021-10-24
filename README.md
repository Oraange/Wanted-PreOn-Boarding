# Wanted Pre-on Boarding Backend Course 지원 과제

---

# 구현 방법과 이유

## 🧩 User (사용자)

- model
  - nickname : 사용자의 아이디
  - password : 사용자의 패스워드

- view
  - **Sign Up**

    ```python
    if type(nickname) != str or type(password) != str:
        return JsonResponse({ "MESSAGE" : f"INPUT MUST BE STRING, INPUT TYPE IS {type(nickname)}" }, status = 400)
    ```
    잘못된 형식의 타입 요청이 들어올 경우 에러 반환

    ```python
    if IsUserExist(nickname):
        return JsonResponse({ "MESSAGE" : "DUPLICATED NICKNAME" }, status = 409)
    ```
    - `repo.py`파일에 `IsUserExist` 선언(유저가 이미 존재하는지 확인하는 로직 구현)
    - 입력한 nickname이 이미 존재할 경우 에러 반환

    ```python
    if not VerifyNickname(nickname):
        return JsonResponse({ "MESSAGE" : "NICKNAME ONLY CONTAIN 'alphabet' and 'number', ALSO LENGTH BETWEEN 3 ~ 15" }, status = 400)
            
    if not VerifyPassword(password):
        return JsonResponse({ "MESSAGE" : "PASSWORD MUST CONTAIN 'alphabet', 'number', 'special character', ALSO LENGTH BETWEEN 8 ~ 20" }, status = 400)
    ```
    - `validator.py`파일에 validation 체크하는 로직 구현
    - Validation 에러 (사용자에게 nickname과 password의 입력 요구사항 명시)

    ```py
    hashed_pw  = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    decoded_pw = hashed_pw.decode("utf-8")

    User.objects.create(
        nickname = nickname,
        password = decoded_pw
    )

    return JsonResponse({ "MESSAGE" : "CREATED" }, status = 201)
    ```
    입력된 패스워드 암호화 후 회원가입 완료

  - **Sign In**

    ```py
    if not IsUserExist(nickname):
        return JsonResponse({ "MESSAGE" : "LOGIN ERROR"}, status = 401)
    ```
    입력된 nickname이 존재하지 않으면 에러 반환

    ```py
        if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            return JsonResponse({ "MESSAGE" : "LOGIN ERROR"}, status = 401)
    ```
    입력된 password와 DB에 저장된 password를 비교해서 같지 않으면 에러 반환

    **유저가 로그인을 시도했을 때 nickname이 잘못 입력됐는지 password가 잘못 입력됐는지 알 수 없어야 해커에 의한 공격을 최소화할 수 있기 때문에 같은 에러 반환**

    ```py
    token = jwt.encode({"id" : user.id}, SECRET_KEY, algorithm = "HS256")

        return JsonResponse({ 
            "MESSAGE" : "SUCCESS",
            "TOKEN"   : token }, status = 200)
    ```
    jwt를 생성하여 유저에게 반환

---

## 🧩 Board (게시글)

- model
  - title : 게시글 제목 (Index) -> 추후 검색 기능이 추가될 경우 WHERE절이 자주 들어갈 수 있으므로 Index를 걸어주었습니다.
  - content : 게시글 내용

- view
  - **Create**

    ```py
    if title=="" or content=="":
        return JsonResponse({ "MESSAGE" : "PLEASE INPUT CONTENTS" }, status = 400)
    ```
    제목 및 내용을 빈 칸으로 두면 에러 반환

    ```py
    Board.objects.create(
        writer  = request.user,
        title   = title,
        content = content
    )

    return JsonResponse({ "MESSAGE" : "CREATED" }, status = 201)
    ```
    authorization 데코레이터를 이용하여 payload에서 user의 id값을 가져온 후 해당 유저 객체를 ForeignKey로 연결하여 게시글 생성

  - **Read**
    - 전체 조회(pagination 적용)
        ```py
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
        ```
        - pagination을 구현하기 위해 OFFSET(page number) 및 LIMIT(페이지당 출력할 게시글 수) 선언
        - OFFSET과 LIMIT은 query parameter로 받아옵니다.
        - TimeStamp 모델을 생성하여 User 및 Board객체에 각각 상속하였습니다.
        - 최근에 생성된(혹은 수정된) 게시글이 가장 위에 보이게 하기 위해서 `updated_at`의 역순으로 정렬
        - 정렬된 게시글을 OFFSET과 LIMIT을 이용하여 pagination 구현

    - 상세 조회
        ```py
        def get(self, request, board_id):
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
        ```
        board_id를 path parameter로 받아서 해당 게시글 조회

        ```py
        except Board.DoesNotExist:
            return JsonResponse({ "MESSAGE" : "BOARD DOES NOT EXIST" }, status = 400)
        ```
        만약 해당 id의 게시글이 없다면 에러 반환

  - **Update**

    ```py
    board = Board.objects.get(id = board_id)

    if board.writer.id != request.user.id:
        return JsonResponse({ "MESSAGE" : "FORBIDDEN" }, status = 403)
    ```
    - 마찬가지로 path parameter로 게시글 id를 받아옵니다.
    - 만약 해당 게시글의 작성자가 토큰의 user id와 다르면 수정할 권한이 없으므로 에러 반환

    ```py
    if title=="" or content=="":
        return JsonResponse({ "MESSAGE" : "PLEASE INPUT CONTENTS" }, status = 400)
    ```
    내용이 둘 중 하나라도 없으면 에러 반환

    ```py
    board.title   = title
    board.content = content
    board.save()

    return JsonResponse({ "MESSAGE" : "UPDATED" }, status = 201)
    ```
    수정 내용을 적용하고 수정 완료

    ```py
    except Board.DoesNotExist:
        return JsonResponse({ "MESSAGE" : "BOARD DOES NOT EXIST"}, status = 400)
    ```
    수정할 게시글이 존재하지 않는다면 에러 반환

  - **Delete**

    ```py
    board = Board.objects.get(id = board_id)

    if board.writer.id != request.user.id:
        return JsonResponse({ "MESSAGE" : "FORBIDDEN" }, status = 403)
    ```
    수정과 마찬가지로 권한 없으면 에러 반환

    ```py
    board.delete()

    return HttpResponse(status = 204)
    ```
    게시글 삭제 완료

    ```py
    except Board.DoesNotExist:
        return JsonResponse({ "MESSAGE" : "BOARD DOES NOT EXIST"}, status = 400)
    ```
    삭제할 게시글이 존재하지 않는다면 에러 반환

---

# 실행 방법 (Endpoint 호출 방법)

## 🧩 User (사용자)

- **/user/sign-up (유저 회원가입)**
    - Method : POST
    - parameter : request_body

    param_name(json key값) | type | option
    -----|------|---
    nickname | varchar(32) | null = False / unique = True
    password | varchar(32) | null = False

- **/user/sign-in (유저 로그인)**
    - Method : POST
    - parameter : request_body

    param_name(json key값) | type | option
    -----|------|---------
    nickname | varchar(32) | null = False / unique = True
    password | varchar(32) | null = False

## 🧩 Board (게시글)

- **/boards?offset=0&limit=4 (게시글 전체 조회)**
    - Method : GET
    - parameter : query_parameter

    param_name | type | option
    -----------|------|-------
    offset | unsigned int | 입력은 옵션
    limit | unsigned int | 입력은 옵션

- **/boards/1 (게시글 상세 조회)**
    - Method : GET
    - parameter : path_parameter
    param | type
    ------|-----
    /<int> | int

- **/boards/write (게시글 작성)**
    - Method : POST
    - parameter : request_body

    param_name(json key값) | type | option
    -----------|------|-------
    title | varchar | blank = False
    content | text | blank = False

- **/boards/1 (게시글 수정)**
    - Method : PATCH
    - parameter : path_parameter

    param | type
    ------|-----
    /<int> | int

- **/boards/1 (게시글 삭제)**
    - Method : DELETE
    - parameter : path_parameter
    
    param | type
    ------|-----
    /<int> | int

---

# API 명세

