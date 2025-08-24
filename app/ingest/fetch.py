import os, hashlib, httpx
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "itmo-program-assistant/1.0"}

ABIT_PAGES = {
    "AI": "https://abit.itmo.ru/program/master/ai",
    "AI Product": "https://abit.itmo.ru/program/master/ai_product",
}

def _cache_path(url: str, cache_dir: str) -> str:
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    return os.path.join(cache_dir, f"{h}")

def download(url: str, cache_dir: str = "datasets/raw") -> str:
    os.makedirs(cache_dir, exist_ok=True)
    path = _cache_path(url, cache_dir)
    if os.path.exists(path):
        return path

    # если PROXY задан в .env — пробросим в окружение для httpx
    proxy = os.environ.get("PROXY")
    if proxy:
        os.environ["HTTP_PROXY"] = proxy
        os.environ["HTTPS_PROXY"] = proxy

    # без параметра proxies=
    with httpx.Client(follow_redirects=True, headers=HEADERS, timeout=30.0) as client:
        r = client.get(url)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    return path


def extract_plan_link(html_bytes: bytes) -> str | None:
    soup = BeautifulSoup(html_bytes, "lxml")
    candidate = None
    for a in soup.find_all(["a", "button"]):
        text = (a.get_text() or "").strip().lower()
        if "скачать" in text and "учеб" in text:
            href = a.get("href")
            if href:
                candidate = href
                break
    if not candidate:
        for a in soup.find_all("a"):
            href = (a.get("href") or "").lower()
            if any(ext in href for ext in [".pdf", ".xlsx", ".xls"]):
                candidate = a.get("href")
                break
    if candidate and candidate.startswith("/"):
        candidate = "https://abit.itmo.ru" + candidate
    return candidate

def get_official_plan_link(program: str) -> str | None:
    url = ABIT_PAGES[program]
    html_path = download(url)
    with open(html_path, "rb") as f:
        html = f.read()
    return extract_plan_link(html)