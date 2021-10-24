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

# 실행 방법 (Endpoint 호출 방법) 및 API 명세

## 🧩 User (사용자)

- **/user/sign-up (유저 회원가입)**
    - <img width="1255" alt="스크린샷 2021-10-24 오후 5 52 31" src="https://user-images.githubusercontent.com/42742076/138587745-fb1e4842-52a1-4a16-86c9-6466c8cd5cb5.png">
    - Method : POST
    - parameter : request_body

    param_name(json key값) | type | option
    -----|------|---
    nickname | varchar(32) | null = False / unique = True
    password | varchar(32) | null = False
    
    - 실행 예제
    - <img width="1238" alt="스크린샷 2021-10-24 오후 6 17 51" src="https://user-images.githubusercontent.com/42742076/138587925-709f4a1f-7504-4f0e-8af6-a3d02e04dcbf.png">

- **/user/sign-in (유저 로그인)**
    - <img width="1247" alt="스크린샷 2021-10-24 오후 6 33 10" src="https://user-images.githubusercontent.com/42742076/138588438-371a214c-f1b5-471e-9bbf-1119654963eb.png">
    - Method : POST
    - parameter : request_body

    param_name(json key값) | type | option
    -----|------|---------
    nickname | varchar(32) | null = False / unique = True
    password | varchar(32) | null = False
    
    - 실행 예제
    - <img width="1239" alt="스크린샷 2021-10-24 오후 6 19 47" src="https://user-images.githubusercontent.com/42742076/138587983-80109444-0da5-4c4d-9470-897e525c8a3d.png">

## 🧩 Board (게시글)

- **/boards?offset=0&limit=4 (게시글 전체 조회)**
    - <img width="1243" alt="스크린샷 2021-10-24 오후 6 22 11" src="https://user-images.githubusercontent.com/42742076/138588073-902e9ece-ac45-4a13-a20e-9ed91dc5e777.png">
    - Method : GET
    - parameter : query_parameter

    param_name | type | option
    -----------|------|-------
    offset | unsigned int | 입력은 옵션
    limit | unsigned int | 입력은 옵션
    
    - 실행 예제
    - <img width="1240" alt="스크린샷 2021-10-24 오후 6 22 53" src="https://user-images.githubusercontent.com/42742076/138588091-e38d710c-0a25-4853-b491-6be66e7eed6e.png">


- **/boards/1 (게시글 상세 조회)**
    - <img width="1242" alt="스크린샷 2021-10-24 오후 6 23 35" src="https://user-images.githubusercontent.com/42742076/138588113-845282a2-4f7e-4e9c-940e-c7a9ef0a21be.png">
    - Method : GET
    - parameter : path_parameter

    param | type
    ------|-----
    /1 | int
    
    - 실행 예제
    - <img width="1239" alt="스크린샷 2021-10-24 오후 6 24 22" src="https://user-images.githubusercontent.com/42742076/138588138-d9b28509-2bc1-4f0d-a1c1-20c9e974bbb4.png">


- **/boards/write (게시글 작성)**
    - <img width="1137" alt="스크린샷 2021-10-24 오후 6 25 39" src="https://user-images.githubusercontent.com/42742076/138588169-2ba5113f-cb56-4eec-9cfb-e64af0815192.png">
    - Method : POST
    - parameter : request_body

    param_name(json key값) | type | option
    -----------|------|-------
    title | varchar | blank = False
    content | text | blank = False
    
    - 실행 예제
    - <img width="1240" alt="스크린샷 2021-10-24 오후 6 26 10" src="https://user-images.githubusercontent.com/42742076/138588179-e22e946a-a97c-41fd-ad2b-fb5f384a181e.png">

- **/boards/1 (게시글 수정)**
    - <img width="1067" alt="스크린샷 2021-10-24 오후 6 27 33" src="https://user-images.githubusercontent.com/42742076/138588237-3fa5c0c4-933f-41c8-9cdf-823a9eaf6dcb.png">
    - Method : PATCH
    - parameter : path_parameter

    param | type
    ------|-----
    /1 | int
    
    - 실행 예제
    - <img width="1241" alt="스크린샷 2021-10-24 오후 6 28 37" src="https://user-images.githubusercontent.com/42742076/138588255-958d865c-f276-4694-a81d-7ead4d753ca8.png">

- **/boards/1 (게시글 삭제)**
    - <img width="1238" alt="스크린샷 2021-10-24 오후 6 30 29" src="https://user-images.githubusercontent.com/42742076/138588306-41b4df4c-9640-4d72-a9d1-26356f972343.png">
    - Method : DELETE
    - parameter : path_parameter

    param | type
    ------|-----
    /1 | int
    
    - 실행 예제
    - <img width="1241" alt="스크린샷 2021-10-24 오후 6 31 03" src="https://user-images.githubusercontent.com/42742076/138588336-f63592db-9ecf-4fb0-86d6-cc376540ec14.png">


