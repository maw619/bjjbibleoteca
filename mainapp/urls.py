from django.urls import path
from .views import register_view, login_view, logout_view, video_dropdown

urlpatterns = [
    path("", video_dropdown, name="home"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]