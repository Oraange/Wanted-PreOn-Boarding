from django.db import models

from core.models import TimeStamp

class User(TimeStamp):
    nickname = models.CharField(max_length = 32, unique = True)
    password = models.CharField(max_length = 32)

    class Meta:
        db_table = "users"