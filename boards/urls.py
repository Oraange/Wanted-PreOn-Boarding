from django.urls import path

from boards.views import BoardListView, BoardPostingView, BoardView

urlpatterns = [
    path("/write", BoardPostingView.as_view()),
    path("", BoardListView.as_view()),
    path("/<int:board_id>", BoardView.as_view())
]