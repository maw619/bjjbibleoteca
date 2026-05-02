from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Category, Note, Video, NoteComment, NoteLike
import json
from django.utils import timezone
from django.db import connection
from django.db.models import Count
from django.db.utils import OperationalError, ProgrammingError


@login_required
def notes_list(request):
    table_names = connection.introspection.table_names()
    has_comments_table = "mainapp_notecomment" in table_names
    has_likes_table = "mainapp_notelike" in table_names

    notes_query = Note.objects.select_related(
        "user",
        "video",
        "video__section"
    )
    if has_comments_table:
        notes_query = notes_query.prefetch_related("comments__user")
    if has_likes_table:
        notes_query = notes_query.prefetch_related("likes__user")

    notes_query = notes_query.order_by("-updated_at")
    try:
        notes = list(notes_query)
    except (OperationalError, ProgrammingError):
        has_comments_table = False
        has_likes_table = "mainapp_notelike" in connection.introspection.table_names()
        fallback_query = Note.objects.select_related("user", "video", "video__section").order_by("-updated_at")
        if has_likes_table:
            fallback_query = fallback_query.prefetch_related("likes__user")
        notes = list(fallback_query)

    return render(request, "notes.html", {
        "notes": notes,
        "has_comments_table": has_comments_table,
        "has_likes_table": has_likes_table,
    })


@require_POST
@login_required
def add_note_comment(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        note_id = data.get("note_id")
        content = (data.get("content") or "").strip()

        if not note_id or not content:
            return JsonResponse({"error": "Missing note or comment content"}, status=400)

        note = Note.objects.get(id=note_id)
        comment = NoteComment.objects.create(
            note=note,
            user=request.user,
            content=content,
        )

        return JsonResponse({
            "status": "success",
            "comment": {
                "id": comment.id,
                "username": comment.user.username,
                "content": comment.content,
                "created_at": timezone.localtime(comment.created_at).strftime("%Y-%m-%d %H:%M"),
            },
        })

    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found"}, status=404)
    except (OperationalError, ProgrammingError):
        return JsonResponse({"error": "Comments table is missing. Run migrations first."}, status=503)
    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": "Server error"}, status=500)


@require_POST
@login_required
def delete_note_comment(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        comment_id = data.get("comment_id")

        if not comment_id:
            return JsonResponse({"error": "Missing comment id"}, status=400)

        comment = NoteComment.objects.get(id=comment_id, user=request.user)
        comment.delete()

        return JsonResponse({"status": "deleted"})
    except NoteComment.DoesNotExist:
        return JsonResponse({"error": "Not allowed"}, status=403)
    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": "Server error"}, status=500)


@require_POST
@login_required
def toggle_note_like(request):
    try:
        if "mainapp_notelike" not in connection.introspection.table_names():
            return JsonResponse({"error": "Likes table is missing. Run migrations first."}, status=503)

        data = json.loads(request.body.decode("utf-8"))
        note_id = data.get("note_id")
        if not note_id:
            return JsonResponse({"error": "Missing note id"}, status=400)

        note = Note.objects.get(id=note_id)
        like, created = NoteLike.objects.get_or_create(note=note, user=request.user)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        likes = NoteLike.objects.filter(note=note).select_related("user")
        return JsonResponse({
            "status": "success",
            "liked": liked,
            "count": likes.count(),
            "users": [like.user.username for like in likes],
        })
    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found"}, status=404)
    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({"error": "Server error"}, status=500)

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
    except (OperationalError, ProgrammingError):
        table_names = connection.introspection.table_names()
        if "mainapp_notecomment" in table_names:
            return JsonResponse({"error": "Server error"}, status=500)

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM mainapp_note WHERE id = %s AND user_id = %s",
                [note_id, request.user.id],
            )
            deleted_rows = cursor.rowcount

        if deleted_rows:
            return JsonResponse({"status": "deleted"})
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

    recent_notes = Note.objects.select_related("user", "video").order_by("-updated_at")[:12]

    table_names = connection.introspection.table_names()
    has_comments_table = "mainapp_notecomment" in table_names
    if has_comments_table:
        recent_notes = recent_notes.prefetch_related("comments__user")

    return render(request, 'videos.html', {
        'categories': categories,
        'noted_video_ids': noted_video_ids,
        'recent_notes': recent_notes,
        'has_comments_table': has_comments_table,
    })

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
