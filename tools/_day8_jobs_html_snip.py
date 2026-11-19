import re
import urllib.request

html = urllib.request.urlopen("http://127.0.0.1:8000/jobs/", timeout=15).read().decode("utf-8", "replace")
for m in re.finditer(r"<form\b[^>]*>", html, re.I):
    print("FORM", m.group(0)[:240])
print("pages_slash_count", html.count("/pages/"))
idx = html.find('"/pages/"')
if idx < 0:
    idx = html.find("'/pages/'")
print("bare_pages_idx", idx)
if idx >= 0:
    print(repr(html[max(0, idx - 100) : idx + 40]))
# also search without quotes
for pat in ['href="/pages/"', "href='/pages/'", 'href="/pages"', "href='/pages'"]:
    print(pat, html.count(pat))
