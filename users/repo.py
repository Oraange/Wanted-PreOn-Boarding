from users.models import User

def IsUserExist(nickname):
    return User.objects.filter(nickname = nickname).exists()
