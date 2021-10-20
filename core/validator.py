import re

def VerifyPassword(password):
    #소문자, 대문자, 숫자, 특수문자 무조건 1개씩 포함, 8 ~ 20자 사이
    regex_compiler = re.compile("^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,20}$")

    return regex_compiler.match(password)