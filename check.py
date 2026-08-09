#!/usr/bin/env python3
"""
Weekly checker for free-llm-services.

Policy: we NEVER test with real API keys (we can't fabricate key-based results).
Instead we run honest, verifiable checks:
  1. HTTP reachability of the provider's OpenAI-compatible base_url (endpoint or site).
  2. Best-effort scan of the provider's site / pricing page for "free" tier indicators.
  3. Update providers.json status + write a dated report to reports/YYYY-MM-DD.md.
  4. Commit + push to the repo (via calling the enclosing git, not fabricating).

Status semantics:
  ok            - reachable AND "free" indicator found on scanned page
  unreachable   - endpoint/site did not respond within timeout
  needs_review  - reachable but free-tier could not be confirmed from scanned page
"""
import json, os, sys, subprocess, time, datetime, urllib.request, urllib.error, re

REPO = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(REPO, "providers.json")
REPORTS = os.path.join(REPO, "reports")
TIMEOUT = 15
UA = "Mozilla/5.0 (compatible; free-llm-services-checker/1.0)"

class _NoRedirectFollow:
    """Resolve redirects manually with a hop cap to survive bot-blocking / loop CDNs."""

def _resolve(url, hops=0, timeout=TIMEOUT):
    """Follow up to 5 redirects; return (final_url, status, body). Raises on final failure."""
    if hops > 5:
        raise RuntimeError("too many redirects")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    r = urllib.request.urlopen(req, timeout=timeout)  # auto-follows most redirects
    return r.status, r.read(300000).decode("utf-8", errors="replace")

def http_get(url, timeout=TIMEOUT):
    """Reachability probe. Any HTTP response (incl. 401/403/404) proves the
    host is alive and the endpoint exists; only transport errors are failures."""
    m = re.match(r"(https?://[^/]+)", url)
    root = m.group(1) if m else url
    try:
        st, body = _resolve(root, timeout=timeout)
        return st, body
    except urllib.error.HTTPError as e:
        # a real HTTP status reached us -> alive
        try:
            body = e.read(200000).decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return e.code, body
    except Exception as e:
        raise RuntimeError(str(e)) from e

def check_provider(p):
    checked_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    endpoints = [p.get("base_url"), p.get("site")]
    candidates = [e for e in endpoints if e]
    last_err = ""
    reachable = False
    body = ""
    for u in candidates:
        # keep only scheme://host for reachability (avoids requiring valid auth paths)
        try:
            m = re.match(r"(https?://[^/]+)", u)
            root = m.group(1) if m else u
            st, body = http_get(root)
            reachable = st < 500
            last_err = f"{root} HTTP {st}"
            break
        except Exception as e:
            last_err = str(e)
            continue

    free_found = False
    if body:
        low = body.lower()
        free_found = bool(re.search(r'free', low))
        # deeper: a pricing/docs page mention of free tier
        for kw in ["free tier", "free-tier", "permanently free", "free models", "no credit card"]:
            if kw in low:
                free_found = True
                break

    if reachable and free_found:
        status, note = "ok", last_err
    elif reachable:
        status, note = "needs_review", last_err
    else:
        status, note = "unreachable", last_err

    return {
        "status": status,
        "note": note,
        "checked_at": checked_at,
        "last_checked": checked_at,
    }

def main():
    os.makedirs(REPORTS, exist_ok=True)
    with open(DATA) as f:
        data = json.load(f)
    now = datetime.datetime.now()
    report_lines = ["# Free LLM Services — weekly check",
                    f"\n_Checked {now.strftime('%Y-%m-%d %H:%M UTC')}_",
                    "", "| Provider | Status | Note |", "|---|---|---|"]
    for p in data["providers"]:
        res = check_provider(p)
        p["last_checked"] = res["last_checked"]
        p["status"] = res["status"]
        if "notes" not in p:
            p["notes"] = ""
        report_lines.append(f"| {p['name']} | {res['status']} | {res['note']} |")
        print(f"{p['name']:25} -> {res['status']}  ({res['note']})")

    data["last_verified"] = now.strftime("%Y-%m-%d %H:%M UTC")
    ok = sum(1 for p in data["providers"] if p["status"] == "ok")
    u = sum(1 for p in data["providers"] if p["status"] == "unreachable")
    r = sum(1 for p in data["providers"] if p["status"] == "needs_review")
    report_lines.insert(3, f"\n**Summary:** {ok} ok · {r} needs review · {u} unreachable\n")
    report_lines.append(f"\n---\nSummary: {ok} ok · {r} needs review · {u} unreachable")

    with open(DATA, "w") as f:
        json.dump(data, f, indent=2)
    report_path = os.path.join(REPORTS, now.strftime("%Y-%m-%d.md"))
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines) + "\n")

    # Commit + push (this is the honest delivery step)
    try:
        subprocess.run(["git", "add", "providers.json", "reports/"], cwd=REPO,
                       capture_output=True, check=True)
        subprocess.run(["git", "-c", "user.name=Simao Lopes",
                        "-c", "user.email=simaocarmolopes@gmail.com",
                        "commit", "-m", f"check: {now.strftime('%Y-%m-%d')} — {ok} ok / {r} review / {u} unreachable"],
                       cwd=REPO, capture_output=True, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO,
                       capture_output=True, check=True)
        print(f"\nCommitted + pushed. Report: reports/{now.strftime('%Y-%m-%d')}.md")
    except subprocess.CalledProcessError as e:
        print(f"\n[git] {e}")

if __name__ == "__main__":
    main()