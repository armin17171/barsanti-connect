import os
import re
from datetime import datetime, timezone
from html import escape

from fastapi import Request
from fastapi.templating import Jinja2Templates
from markupsafe import Markup

_BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(_BASE_DIR, "templates"))

_TAG_RE = re.compile(r"#(\w{1,80})", re.UNICODE)
_MENTION_RE = re.compile(r"@([A-Za-z0-9_.]{3,32})")


def linkify(text: str) -> Markup:
    """Rende cliccabili #hashtag e @menzioni. Esegue prima l'escape dell'HTML."""
    safe = escape(text or "")
    safe = _TAG_RE.sub(r'<a class="tag" href="/hashtag/\1">#\1</a>', safe)
    safe = _MENTION_RE.sub(r'<a class="mention" href="/u/\1">@\1</a>', safe)
    safe = safe.replace("\n", "<br>")
    return Markup(safe)


def humantime(dt: datetime) -> str:
    """Tempo relativo in italiano (es. '3 min fa')."""
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - dt
    secs = int(delta.total_seconds())
    if secs < 60:
        return "ora"
    if secs < 3600:
        return f"{secs // 60} min fa"
    if secs < 86400:
        return f"{secs // 3600} h fa"
    if secs < 604800:
        return f"{secs // 86400} g fa"
    return dt.strftime("%d/%m/%Y")


def datefmt(dt: datetime, fmt: str = "%d/%m/%Y %H:%M") -> str:
    if dt is None:
        return ""
    return dt.strftime(fmt)


templates.env.filters["linkify"] = linkify
templates.env.filters["humantime"] = humantime
templates.env.filters["datefmt"] = datefmt


def render(template_name: str, request: Request, *, user=None, status_code: int = 200, **context):
    """Renderizza un template con il contesto comune (request, utente loggato)."""
    ctx = {"current_user": user}
    ctx.update(context)
    response = templates.TemplateResponse(request, template_name, ctx)
    response.status_code = status_code
    return response
