from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.loginPage, name="login"),
    path("register/", views.registerPage, name="register"),
    path("logout/", views.logoutUser, name="logout"),
    path("", views.home, name="home"),
    path("room /<str:pk>/", views.room, name="room"),
    path("create-form/", views.createRoom, name="create-room"),
    path("update-form/<str:pk>", views.updateRoom, name="update-room"),
    path("delete-form/<str:pk>", views.deleteRoom, name="delete-room"),
]
