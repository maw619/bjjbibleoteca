from django.urls import path
from .views import register_view, login_view, logout_view, video_dropdown, save_note, get_note, notes_list, delete_note, add_note_comment, delete_note_comment, toggle_note_like, toggle_video_like, get_video_like

urlpatterns = [
    path("", video_dropdown, name="home"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("save-note/", save_note, name="save_note"),
    path("get-note/<int:video_id>/", get_note, name="get_note"),
    path("notes/", notes_list, name="notes"),
    path("add-note-comment/", add_note_comment, name="add_note_comment"),
    path("delete-note-comment/", delete_note_comment, name="delete_note_comment"),
    path("delete-note/", delete_note, name="delete_note"),
    path("toggle-note-like/", toggle_note_like, name="toggle_note_like"),
    path("toggle-video-like/", toggle_video_like, name="toggle_video_like"),
    path("get-video-like/<int:video_id>/", get_video_like, name="get_video_like"),
]
