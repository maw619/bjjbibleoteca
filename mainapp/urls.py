from django.urls import path
from .views import register_view, login_view, logout_view, video_dropdown, save_note, get_note, notes_list, delete_note

urlpatterns = [
    path("", video_dropdown, name="home"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("save-note/", save_note, name="save_note"),
    path("get-note/<int:video_id>/", get_note, name="get_note"),
    path("notes/", notes_list, name="notes"),
    path("delete-note/", delete_note, name="delete_note"),
]