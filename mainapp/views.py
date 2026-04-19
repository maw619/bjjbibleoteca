from django.shortcuts import render
from .models import Category
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Note, Video
import json
from django.utils import timezone  # <--- Import at the top


@login_required
def notes_list(request):
    notes = Note.objects.select_related(
        "user",
        "video",
        "video__section"
    ).order_by("-updated_at")

    return render(request, "notes.html", {
        "notes": notes
    })

@login_required
def save_note(request):
    if request.method == "POST":
        
        data = json.loads(request.body)

        video_id = data.get("video_id")
        content = data.get("content")
        timestamp = data.get("timestamp") or 0

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return JsonResponse({"error": "Video not found"}, status=404)

        note = Note.objects.create(
            user=request.user,
            video=video,
            content=content,
            timestamp=float(timestamp)
        )

        return JsonResponse({"status": "success", "note_id": note.id})
    
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Note

@require_POST
@login_required
def delete_note(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        note_id = data.get("note_id")

        print("Deleting note:", note_id)  # 🔥 DEBUG

        note = Note.objects.get(id=note_id, user=request.user)
        note.delete()

        return JsonResponse({"status": "deleted"})

    except Note.DoesNotExist:
        return JsonResponse({"error": "Not allowed"}, status=403)

    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": "Server error"}, status=500)

@login_required
def get_note(request, video_id):
    notes = Note.objects.filter(
        user=request.user,
        video_id=video_id
    ).order_by("-updated_at")

    serialized_notes = [
        {
            "id": note.id,
            "content": note.content,
            "timestamp": note.timestamp or 0,
        }
        for note in notes
    ]

    content = "\n\n".join(
        [f"[{int(note['timestamp']//60)}:{int(note['timestamp']%60):02d}] {note['content']}" for note in serialized_notes]
    )

    return JsonResponse({
        "content": content,
        "notes": serialized_notes,
    })

@login_required
def video_dropdown(request):
    categories = Category.objects.prefetch_related("sections__videos")
    noted_video_ids = set(
        Note.objects.filter(user=request.user).values_list("video_id", flat=True)
    )
 
    return render(request, 'videos.html', {
        'categories': categories,
        'noted_video_ids': noted_video_ids,
    })

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
