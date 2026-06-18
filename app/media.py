import os
import secrets

from fastapi import HTTPException, UploadFile, status

from .config import settings

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_EXTS = {".mp4", ".webm", ".mov", ".m4v"}
AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".oga", ".m4a", ".aac", ".flac"}


def _kind_for_ext(ext: str) -> str | None:
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in AUDIO_EXTS:
        return "audio"
    return None


async def save_upload(file: UploadFile | None) -> tuple[str | None, str | None]:
    """Salva un media caricato. Ritorna (path_relativo, kind) oppure (None, None).

    Valida estensione e dimensione. Solleva HTTPException se non valido.
    """
    if file is None or not file.filename:
        return None, None

    ext = os.path.splitext(file.filename)[1].lower()
    kind = _kind_for_ext(ext)
    if kind is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato file non supportato (immagine, video o audio).",
        )

    os.makedirs(settings.media_dir, exist_ok=True)
    name = f"{secrets.token_hex(16)}{ext}"
    dest = os.path.join(settings.media_dir, name)

    size = 0
    with open(dest, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_bytes:
                out.close()
                os.remove(dest)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File troppo grande (max {settings.max_upload_mb} MB).",
                )
            out.write(chunk)

    return name, kind


async def save_image(file: UploadFile | None) -> str | None:
    """Salva un'immagine (per gli avatar). Rifiuta i video. Ritorna il path o None."""
    if file is None or not file.filename:
        return None
    path, kind = await save_upload(file)
    if kind != "image":
        delete_media(path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'immagine del profilo deve essere un'immagine (jpg, png, gif, webp).",
        )
    return path


def delete_media(media_path: str | None) -> None:
    if not media_path:
        return
    full = os.path.join(settings.media_dir, media_path)
    try:
        os.remove(full)
    except OSError:
        pass
