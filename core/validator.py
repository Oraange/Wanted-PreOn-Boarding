import re

def VerifyPassword(password):
    #알파벳, 숫자, 특수문자 무조건 1개씩 포함, 8 ~ 20자 사이
    regex_compiler = re.compile("^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,20}$")

    return regex_compiler.match(password)

def VerifyNickname(nickname):
    #알파벳, 숫자만 가능, 3 ~ 15자 사이
    regex_compiler = re.compile("^([0-9a-z]+){3,15}$")

    return regex_compiler.match(nickname)