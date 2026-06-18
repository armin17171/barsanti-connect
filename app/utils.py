import re

from sqlalchemy.orm import Session as DBSession

from .models import Hashtag

# #parola: lettere/numeri/underscore (incluso unicode), 1-80 caratteri
_HASHTAG_RE = re.compile(r"#(\w{1,80})", re.UNICODE)


def extract_hashtags(text: str) -> list[str]:
    """Estrae i tag (senza '#', minuscoli, senza duplicati) da un testo."""
    seen: list[str] = []
    for match in _HASHTAG_RE.findall(text or ""):
        tag = match.lower()
        if tag not in seen:
            seen.append(tag)
    return seen


def get_or_create_hashtags(db: DBSession, tags: list[str]) -> list[Hashtag]:
    """Recupera gli hashtag esistenti o li crea, ritornando gli oggetti ORM."""
    result: list[Hashtag] = []
    for tag in tags:
        obj = db.query(Hashtag).filter(Hashtag.tag == tag).one_or_none()
        if obj is None:
            obj = Hashtag(tag=tag)
            db.add(obj)
            db.flush()
        result.append(obj)
    return result
