from uuid import uuid4 as U4

from django.db import models

from core.models import TimeStamp

class Board(TimeStamp):
    board_number = models.UUIDField(primary_key = True, default = U4, editable = False)
    writer       = models.ForeignKey('users.User', on_delete = models.CASCADE)
    title        = models.CharField(db_index = True, max_length = 128)
    content      = models.TextField()

    class Meta:
        db_table = "boards"