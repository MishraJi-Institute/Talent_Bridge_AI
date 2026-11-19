import re
import urllib.request

for path in ("/contact/", "/employer/", "/jobs/", "/login/", "/about/"):
    html = urllib.request.urlopen(f"http://127.0.0.1:8000{path}", timeout=15).read().decode(
        "utf-8", "replace"
    )
    bases = re.findall(r"<base[^>]*>", html, re.I)
    abouts = re.findall(r"""href=["']([^"']*about[^"']*)["']""", html, re.I)[:8]
    print(path, "bases=", bases, "about_hrefs=", abouts)
    print("  head=", html[html.lower().find("<head") : html.lower().find("<head") + 280].replace("\n", " "))
