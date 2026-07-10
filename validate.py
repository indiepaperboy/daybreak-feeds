#!/usr/bin/env python3
"""Weekly health check for the Daybreak (rss.) feed catalogue.

Classifies each feed live / blocked / dead, tracks consecutive dead runs, prunes
feeds dead for 3+ runs (unless "protected"), and keeps "blocked" (403/429) feeds
flagged but never auto-removed. Run by .github/workflows/validate.yml.
"""
import json, ssl, os, datetime, urllib.request, urllib.error, concurrent.futures as cf

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.4 Safari/605.1.15")
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
PRUNE_AFTER = 3
TODAY = datetime.date.today().isoformat()

def check(url):
    for _ in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15, context=CTX) as r:
                low = r.read(200_000).decode("utf-8", "ignore").lower()
            return "live" if ("<rss" in low or "<feed" in low or "<rdf" in low) else "dead"
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                return "blocked"
        except Exception:
            pass
    return "dead"

cat = json.load(open("catalogue.json"))
feeds = [f for s in cat["sections"] for f in s["feeds"]]
with cf.ThreadPoolExecutor(max_workers=24) as ex:
    for f, st in zip(feeds, ex.map(lambda f: check(f["url"]), feeds)):
        f["_st"] = st

live = blocked = watch = pruned = 0
notes = []
for s in cat["sections"]:
    kept = []
    for f in s["feeds"]:
        st = f.pop("_st")
        if st == "live":
            live += 1; f["strikes"] = 0; f["lastAlive"] = TODAY; f.pop("blocked", None); kept.append(f)
        elif st == "blocked":
            blocked += 1; f["blocked"] = True; kept.append(f)          # a locked door isn't a corpse
        else:
            f["strikes"] = f.get("strikes", 0) + 1
            if f.get("protected"):
                notes.append(f"PROTECTED FEED DOWN — {f['title']} ({f['url']}), strike {f['strikes']}"); kept.append(f)
            elif f["strikes"] >= PRUNE_AFTER:
                pruned += 1; notes.append(f"pruned — {f['title']} ({f['url']}), dead {f['strikes']} runs")
            else:
                watch += 1; notes.append(f"strike {f['strikes']}/{PRUNE_AFTER} — {f['title']} ({f['url']})"); kept.append(f)
    s["feeds"] = kept

cat["generatedAt"] = TODAY
json.dump(cat, open("catalogue.json", "w"), indent=1, ensure_ascii=False)

total = sum(len(s["feeds"]) for s in cat["sections"])
report = [f"# Feed health — {TODAY}", "",
          f"- live: **{live}**", f"- blocked (kept, flagged): **{blocked}**",
          f"- on strike-watch: **{watch}**", f"- pruned this run: **{pruned}**",
          f"- total in catalogue: **{total}**"]
if notes:
    report += ["", "## Notes", *[f"- {n}" for n in notes]]
out = "\n".join(report)
print(out)
if os.environ.get("GITHUB_STEP_SUMMARY"):
    open(os.environ["GITHUB_STEP_SUMMARY"], "a").write(out + "\n")
