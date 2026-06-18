from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DBSession

from ..database import get_db
from ..deps import require_login
from ..media import delete_media, save_upload
from ..models import Comment, Like, Post, User
from ..utils import extract_hashtags, get_or_create_hashtags
from ..web import redirect_back, redirect_to

router = APIRouter()


@router.post("/posts")
async def create_post(
    request: Request,
    body: str = Form(...),
    media: UploadFile | None = File(None),
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    body = body.strip()
    media_path, media_kind = await save_upload(media)
    if not body and not media_path:
        if media_path:
            delete_media(media_path)
        raise HTTPException(status_code=400, detail="Il post non può essere vuoto.")

    post = Post(author_id=user.id, body=body, media_path=media_path, media_kind=media_kind)
    post.hashtags = get_or_create_hashtags(db, extract_hashtags(body))
    db.add(post)
    db.commit()
    db.refresh(post)
    return redirect_to(f"/post/{post.id}")


@router.post("/posts/{post_id}/like")
def toggle_like(
    post_id: int,
    request: Request,
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post non trovato.")

    existing = (
        db.query(Like).filter(Like.user_id == user.id, Like.post_id == post_id).one_or_none()
    )
    if existing:
        db.delete(existing)
        liked = False
    else:
        db.add(Like(user_id=user.id, post_id=post_id))
        liked = True
    db.commit()

    count = db.query(Like).filter(Like.post_id == post_id).count()
    # Se la richiesta arriva da fetch (JS) rispondiamo JSON, altrimenti redirect
    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse({"liked": liked, "count": count})
    return redirect_back(request)


@router.post("/posts/{post_id}/comment")
def add_comment(
    post_id: int,
    request: Request,
    body: str = Form(...),
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post non trovato.")
    body = body.strip()
    if not body:
        raise HTTPException(status_code=400, detail="Il commento non può essere vuoto.")
    db.add(Comment(post_id=post_id, author_id=user.id, body=body))
    db.commit()
    return redirect_back(request, default=f"/post/{post_id}")


@router.post("/posts/{post_id}/delete")
def delete_post(
    post_id: int,
    request: Request,
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post non trovato.")
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Non puoi eliminare questo post.")
    delete_media(post.media_path)
    db.delete(post)
    db.commit()
    return redirect_back(request, default="/")


@router.post("/comments/{comment_id}/delete")
def delete_comment(
    comment_id: int,
    request: Request,
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Commento non trovato.")
    if comment.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Non puoi eliminare questo commento.")
    db.delete(comment)
    db.commit()
    return redirect_back(request, default="/")
