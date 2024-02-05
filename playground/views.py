from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Room, Topic, Messages
from .forms import RoomForm


def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist")
            return redirect("login")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username or password does")

    # Prefill the form with the logged-in user's information if available
    if request.user.is_authenticated:
        username = request.user.username
        context = {"username": username}
    else:
        context = {"page": page}
    return render(request, "playground/login_register.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


def registerPage(request):
    page = "register"
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Error occured during registration")

    context = {"form": form}
    return render(request, "playground/login_register.html", context)


def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)
        | Q(name__icontains=q)
        | Q(description__icontains=q),
    )
    room_count = rooms.count()
    topics = Topic.objects.all()
    room_messages = Messages.objects.filter(Q(room__name__icontains=q))
    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
    }
    return render(request, "playground/home.html", context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = Messages.objects.filter(room=room)
    participants = room.participants.all()
    if request.method == "POST":
        message = Messages.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get("body"),
        )
        room.participants.add(request.user)

        return redirect("room", pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }
    return render(request, "playground/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    room_messages = user.messages_set.all()
    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics,
    }
    return render(request, "playground/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")

    context = {
        "form": form,
        "topics": topics,
    }
    return render(request, "playground/room_form.html", context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("Your are not allowed to edit this room")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")
    context = {
        "form": form,
        "topics": topics,
    }
    return render(request, "playground/room_form.html", context)


@login_required(login_url="login")
def deleteRoom(request, pk):

    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("Your are not allowed to delete this room")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "playground/delete.html", {"obj": room})


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Messages.objects.get(id=pk)

    # Check if the current user is the owner of the message
    if request.user != message.user:
        return HttpResponse("You are not allowed to delete this message")

    if request.method == "POST":
        message.delete()
        return redirect("home")

    return render(request, "playground/delete.html", {"obj": message})
