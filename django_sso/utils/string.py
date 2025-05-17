from urllib.parse import urlparse, urlunparse


def normalize_uri(uri: str) -> str:
    parsed = urlparse(uri.strip())
    normalized_path = parsed.path.rstrip("/")
    return urlunparse(parsed._replace(path=normalized_path))
