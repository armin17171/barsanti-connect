from fastapi import Request
from fastapi.responses import RedirectResponse

# Codice 303: forza il browser a fare GET dopo un POST (pattern Post/Redirect/Get)
SEE_OTHER = 303


def redirect_back(request: Request, next_url: str | None = None, default: str = "/") -> RedirectResponse:
    """Torna alla pagina indicata dal campo 'next', altrimenti al Referer, altrimenti al default."""
    target = next_url or request.headers.get("referer") or default
    return RedirectResponse(url=target, status_code=SEE_OTHER)


def redirect_to(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=SEE_OTHER)
