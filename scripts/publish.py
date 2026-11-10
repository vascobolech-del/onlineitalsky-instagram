#!/usr/bin/env python3
"""Zveřejňuje naplánované příspěvky na Instagram (@onlineitalsky) a stejný příspěvek i na facebookovou stránku.

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
GRAPH = os.environ.get("GRAPH_URL", "https://graph.facebook.com")
VERSION = os.environ.get("GRAPH_VERSION", "").strip()  # prázdné = výchozí verze aplikace
MODE = os.environ.get("MODE", "plan").strip() or "plan"
TOKEN = os.environ.get("IG_TOKEN", "").strip()
IG_USER_ID = os.environ.get("IG_USER_ID", "").strip()
IG_USERNAME = os.environ.get("IG_USERNAME", "onlineitalsky").strip()
FB_ENABLED = os.environ.get("FACEBOOK", "1").strip() not in ("0", "ne", "false", "")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "").strip()
FB_MAX_ATTEMPTS = 3


def log(msg):
    print(msg, flush=True)


def fail(msg):
    print(f"::error::{msg}", flush=True)
    sys.exit(1)


def api(method, path, params=None, fatal=True, token=None):
    base = f"{GRAPH}/{VERSION}" if VERSION else GRAPH
    params = dict(params or {})
    params["access_token"] = token or TOKEN
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
        if not fatal:
            log(f"(info) {method} {path} → HTTP {e.code}: {body[:300]}")
            return {}
        fail(f"Meta API {method} {path} → HTTP {e.code}: {body}")


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
    """Najde ID Instagram účtu. Zkouší token přes facebookovou stránku i přímo přiřazené účty."""
    if IG_USER_ID:
        return IG_USER_ID
    found = []
    res = api("GET", "me/accounts", {"fields": "name,instagram_business_account{id,username}"}, fatal=False)
    found += [a["instagram_business_account"] for a in res.get("data", []) if a.get("instagram_business_account")]
    if not found:
        for path in ("me/assigned_instagram_accounts", "me/instagram_accounts"):
            res = api("GET", path, {"fields": "id,username"}, fatal=False)
            found += [a for a in res.get("data", []) if a.get("id")]
            if found:
                break
    for acc in found:
        log(f"Nalezen Instagram účet @{acc.get('username')} (ID {acc['id']})")
    match = [a for a in found if (a.get("username") or "").lower() == IG_USERNAME.lower()] or found
    if len(match) != 1:
        fail("Nepodařilo se automaticky najít Instagram účet. V repozitáři nastavte Settings → Secrets and variables → "
             "Actions → Variables → New repository variable: IG_USER_ID = ID účtu @" + IG_USERNAME +
             " (najdete ho v Meta Business → Nastavení → Účty → Instagramové účty).")
    return match[0]["id"]


def find_page():
    """Vrátí (id, název, token stránky) facebookové stránky, nebo None."""
    if FB_PAGE_ID:
        res = api("GET", FB_PAGE_ID, {"fields": "name,access_token"}, fatal=False)
        return (FB_PAGE_ID, res.get("name"), res.get("access_token")) if res.get("access_token") else None
    res = api("GET", "me/accounts", {"fields": "name,access_token"}, fatal=False)
    pages = [a for a in res.get("data", []) if a.get("access_token")]
    match = [a for a in pages if "ital" in (a.get("name") or "").lower()] or pages
    if len(match) != 1:
        if pages:
            log("Nalezené stránky: " + ", ".join(f"{a.get('name')} ({a['id']})" for a in pages))
        return None
    return match[0]["id"], match[0].get("name"), match[0]["access_token"]


def publish_facebook(page, p):
    page_id, _name, page_token = page
    head = p["caption"].strip()[:80]
    res = api("GET", f"{page_id}/posts", {"fields": "message,permalink_url", "limit": 10}, token=page_token)
    for m in res.get("data", []):
        if (m.get("message") or "").strip()[:80] == head:
            log(f"Příspěvek #{p['id']} už na Facebooku je, jen ho zapíšu.")
            return {"fb_post_id": m["id"], "fb_permalink": m.get("permalink_url")}
    out = api("POST", f"{page_id}/photos", {"url": image_url(p), "message": p["caption"], "published": "true"},
              token=page_token)
    post_id = out.get("post_id") or out.get("id")
    link = api("GET", post_id, {"fields": "permalink_url"}, fatal=False, token=page_token).get("permalink_url")
    return {"fb_post_id": post_id, "fb_permalink": link}


def try_facebook(sent, posts_by_id, key):
    """Zkusí poslat příspěvek na Facebook; výsledek nebo chybu zapíše do záznamu. Vrací True při úspěchu."""
    rec = sent[key]
    rec["fb_pokusy"] = rec.get("fb_pokusy", 0) + 1
    try:
        page = find_page()
        if not page:
            fail("Nenašel jsem facebookovou stránku – přidělte ji systémovému uživateli (Obsah) a vygenerujte token "
                 "s oprávněním pages_manage_posts, případně nastavte proměnnou FB_PAGE_ID.")
        rec.update(publish_facebook(page, posts_by_id[int(key)]))
        rec.pop("fb_chyba", None)
        log(f"Facebook: zveřejněno {rec.get('fb_permalink')}")
        return True
    except SystemExit:
        rec["fb_chyba"] = "zveřejnění na Facebook selhalo, viz log běhu"
        return False


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
    posts_by_id = {p["id"]: p for p in posts}
    t = now()

    def save():
        sent_path.write_text(json.dumps(sent, ensure_ascii=False, indent=1) + "\n", "utf-8")

    # Dořešit Facebook u posledního příspěvku, pokud se tam minule nepovedl.
    if FB_ENABLED and TOKEN and MODE in ("plan", "publikovat-ted") and sent:
        last = max(sent, key=lambda k: sent[k].get("cas", ""))
        rec = sent[last]
        if not rec.get("fb_post_id") and rec.get("fb_pokusy", 0) < FB_MAX_ATTEMPTS:
            log(f"Zkouším znovu Facebook u příspěvku #{last}.")
            if not try_facebook(sent, posts_by_id, last):
                save()
                fail(f"Facebook u příspěvku #{last} se ani napodruhé nepovedl "
                     f"(pokus {rec['fb_pokusy']}/{FB_MAX_ATTEMPTS}).")
            save()
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
        if FB_ENABLED:
            page = find_page()
            if not page:
                fail("Instagram je v pořádku, ale nenašel jsem facebookovou stránku. Přidělte ji systémovému uživateli "
                     "(Obsah) a vygenerujte token s oprávněním pages_manage_posts. Pokud Facebook nechcete, "
                     "nastavte proměnnou FACEBOOK = 0.")
            log(f"Facebook stránka: {page[1]} (ID {page[0]}) – přístup funguje.")
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
    key = str(nxt["id"])
    sent[key] = {"cas": t.isoformat(timespec="minutes"), "titulek": nxt["title_it"], **res}
    save()
    log(f"Instagram: zveřejněno #{nxt['id']} {nxt['title_it']}: {res.get('permalink')}")
    fb_ok = True
    if FB_ENABLED:
        fb_ok = try_facebook(sent, posts_by_id, key)
        save()
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"### Zveřejněno #{nxt['id']} {nxt['title_it']}\nInstagram: {res.get('permalink')}\n")
            if FB_ENABLED:
                f.write(f"Facebook: {sent[key].get('fb_permalink') or 'nepovedlo se, zkusím znovu při dalším běhu'}\n")
    if not fb_ok:
        fail("Instagram je zveřejněný, ale Facebook se nepovedl. Při dalším běhu to zkusím znovu.")


if __name__ == "__main__":
    main()
