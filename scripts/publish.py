#!/usr/bin/env python3
"""Zveřejňuje naplánované příspěvky na Instagram (@onlineitalsky).

Režimy (proměnná MODE):
  plan            – běžné denní spuštění: zveřejní příspěvek, jehož termín už nastal
  test            – jen ověří token, účet a dostupnost obrázku; nic nezveřejní
  publikovat-ted  – zveřejní další nezveřejněný příspěvek hned (bez ohledu na termín)
  nanecisto       – jako "plan", ale bez volání Instagramu (pro kontrolu rozpisu)
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("Europe/Prague")
GRAPH = "https://graph.facebook.com"
VERSION = os.environ.get("GRAPH_VERSION", "").strip()  # prázdné = výchozí verze aplikace
MODE = os.environ.get("MODE", "plan").strip() or "plan"
TOKEN = os.environ.get("IG_TOKEN", "").strip()
IG_USER_ID = os.environ.get("IG_USER_ID", "").strip()
IG_USERNAME = os.environ.get("IG_USERNAME", "onlineitalsky").strip()


def log(msg):
    print(msg, flush=True)


def fail(msg):
    print(f"::error::{msg}", flush=True)
    sys.exit(1)


def api(method, path, params=None):
    base = f"{GRAPH}/{VERSION}" if VERSION else GRAPH
    params = dict(params or {})
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params)
    if method == "GET":
        req = urllib.request.Request(f"{base}/{path}?{data}")
    else:
        req = urllib.request.Request(f"{base}/{path}", data=data.encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        fail(f"Instagram API {method} {path} → HTTP {e.code}: {body}")


def now():
    fake = os.environ.get("NOW")  # jen pro testování, např. "2026-11-17 18:10"
    return datetime.fromisoformat(fake).replace(tzinfo=TZ) if fake else datetime.now(TZ)


def when(p):
    return datetime.fromisoformat(p["datum"]).replace(tzinfo=TZ)


def image_url(p):
    base = os.environ.get("IMAGE_BASE_URL", "").strip()
    if not base:
        repo = os.environ.get("GITHUB_REPOSITORY", "")
        ref = os.environ.get("GITHUB_SHA", "main")
        base = f"https://raw.githubusercontent.com/{repo}/{ref}/feed/"
    return base.rstrip("/") + "/" + urllib.parse.quote(p["filename"])


def find_ig_user():
    if IG_USER_ID:
        return IG_USER_ID
    res = api("GET", "me/accounts", {"fields": "name,instagram_business_account{id,username}"})
    found = [a["instagram_business_account"] for a in res.get("data", []) if a.get("instagram_business_account")]
    for acc in found:
        log(f"Nalezen Instagram účet @{acc.get('username')} (ID {acc['id']})")
    match = [a for a in found if a.get("username", "").lower() == IG_USERNAME.lower()] or found
    if len(match) != 1:
        fail("Nepodařilo se jednoznačně najít Instagram účet. Zkontrolujte, že systémový uživatel má přiřazenou "
             "facebookovou stránku propojenou s @" + IG_USERNAME + ", případně nastavte proměnnou IG_USER_ID.")
    return match[0]["id"]


def check_image(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as r:
            ctype = r.headers.get("Content-Type", "")
            log(f"Obrázek je veřejně dostupný ({r.status}, {ctype}): {url}")
            return True
    except Exception as e:  # noqa: BLE001
        log(f"::warning::Obrázek není dostupný: {url} ({e})")
        return False


def already_on_instagram(ig, caption):
    """Pojistka proti dvojímu zveřejnění: porovná začátek popisku s posledními příspěvky."""
    res = api("GET", f"{ig}/media", {"fields": "caption,permalink,timestamp", "limit": 10})
    head = caption.strip()[:80]
    for m in res.get("data", []):
        if (m.get("caption") or "").strip()[:80] == head:
            return m
    return None


def publish(ig, p):
    url = image_url(p)
    dup = already_on_instagram(ig, p["caption"])
    if dup:
        log(f"Příspěvek #{p['id']} už na Instagramu je ({dup.get('permalink')}), jen ho zapíšu.")
        return {"media_id": dup.get("id"), "permalink": dup.get("permalink")}
    container = api("POST", f"{ig}/media", {
        "image_url": url,
        "caption": p["caption"],
        "alt_text": p.get("alt_text", ""),
    })["id"]
    for _ in range(30):
        status = api("GET", container, {"fields": "status_code"}).get("status_code")
        if status == "FINISHED":
            break
        if status in ("ERROR", "EXPIRED"):
            fail(f"Instagram odmítl obrázek {url} (stav {status}).")
        time.sleep(5)
    else:
        fail("Instagram nezpracoval obrázek do 150 s.")
    media_id = api("POST", f"{ig}/media_publish", {"creation_id": container})["id"]
    permalink = api("GET", media_id, {"fields": "permalink"}).get("permalink")
    return {"media_id": media_id, "permalink": permalink}


def main():
    posts = sorted(json.loads((ROOT / "prispevky.json").read_text("utf-8")), key=when)
    sent_path = ROOT / "odeslano.json"
    sent = json.loads(sent_path.read_text("utf-8") or "{}")
    t = now()
    pending = [p for p in posts if str(p["id"]) not in sent]
    log(f"Teď je {t:%d.%m.%Y %H:%M} (Praha). Zveřejněno {len(sent)}/{len(posts)}.")
    if not pending:
        log("Všechny příspěvky jsou zveřejněné.")
        return
    nxt = pending[0]
    log(f"Další na řadě: #{nxt['id']} {nxt['title_it']} – {when(nxt):%d.%m.%Y %H:%M}")

    if MODE == "test":
        if not TOKEN:
            fail("Chybí secret IG_TOKEN.")
        ig = find_ig_user()
        info = api("GET", ig, {"fields": "username,followers_count,media_count"})
        log(f"Spojení funguje: @{info.get('username')}, příspěvků {info.get('media_count')}, "
            f"sledujících {info.get('followers_count')}.")
        try:
            lim = api("GET", f"{ig}/content_publishing_limit", {"fields": "quota_usage,config"})
            log(f"Limit publikování: {lim}")
        except SystemExit:
            log("::warning::Limit publikování se nepodařilo načíst (nevadí).")
        if not check_image(image_url(nxt)):
            fail("Obrázek není veřejně dostupný – zkontrolujte, že je repozitář Public.")
        log("Test v pořádku. Nic nebylo zveřejněno.")
        return

    if MODE != "publikovat-ted":
        if when(nxt) > t:
            log("Zatím není čas, končím.")
            return
        today = t.date().isoformat()
        if any(v.get("cas", "").startswith(today) for v in sent.values()):
            log("Dnes už byl jeden příspěvek zveřejněn, zbytek počká na zítřek.")
            return
        late = (t - when(nxt)).total_seconds() / 3600
        if late > 24:
            log(f"::warning::Příspěvek #{nxt['id']} je zpožděný o {late / 24:.1f} dne – zveřejňuji teď.")

    if MODE == "nanecisto":
        log(f"[nanečisto] Zveřejnil bych #{nxt['id']} s obrázkem {image_url(nxt)}")
        return
    if not TOKEN:
        fail("Chybí secret IG_TOKEN.")
    ig = find_ig_user()
    res = publish(ig, nxt)
    sent[str(nxt["id"])] = {"cas": t.isoformat(timespec="minutes"), "titulek": nxt["title_it"], **res}
    sent_path.write_text(json.dumps(sent, ensure_ascii=False, indent=1) + "\n", "utf-8")
    log(f"Zveřejněno #{nxt['id']} {nxt['title_it']}: {res.get('permalink')}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"### Zveřejněno #{nxt['id']} {nxt['title_it']}\n{res.get('permalink')}\n")


if __name__ == "__main__":
    main()
