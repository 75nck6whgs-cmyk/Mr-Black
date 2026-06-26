"""Analyzes a business website and returns an oldness score + issues list."""
import re
import requests
from bs4 import BeautifulSoup


def check_website(url: str, timeout: int = 10, user_agent: str = "Mozilla/5.0") -> dict:
    if not url:
        return {"has_website": False, "is_outdated": True, "oldness_score": 100, "issues": ["No website"]}

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result = {"has_website": True, "url": url, "is_outdated": False, "oldness_score": 0, "issues": []}

    try:
        resp = requests.get(
            url, timeout=timeout,
            headers={"User-Agent": user_agent},
            allow_redirects=True,
        )
        html = resp.text
        soup = BeautifulSoup(html, "lxml")
        html_lower = html.lower()

        def add(score, issue):
            result["oldness_score"] += score
            result["issues"].append(issue)

        # No HTTPS
        if not resp.url.startswith("https://"):
            add(20, "No HTTPS")

        # Not mobile-responsive
        if not soup.find("meta", {"name": re.compile(r"viewport", re.I)}):
            add(30, "Not mobile-responsive")

        # Old copyright year
        footer = soup.find("footer") or soup
        year_match = re.search(r"(?:©|copyright)\s*(\d{4})", footer.get_text(), re.I)
        if year_match and int(year_match.group(1)) <= 2019:
            add(25, f"Copyright year: {year_match.group(1)}")

        # Adobe Flash
        if ".swf" in html_lower or "shockwave-flash" in html_lower:
            add(40, "Uses Adobe Flash")

        # Old jQuery
        m = re.search(r"jquery[.-](\d+\.\d+)", html_lower)
        if m and float(m.group(1)) < 2.0:
            add(15, f"Old jQuery {m.group(1)}")

        # Old WordPress
        wp = soup.find("meta", {"name": "generator", "content": re.compile(r"WordPress", re.I)})
        if wp:
            v = re.search(r"(\d+\.\d+)", wp.get("content", ""))
            if v and float(v.group(1)) < 5.0:
                add(20, f"Old WordPress {v.group(1)}")

        # Table-based layout
        layout_tables = [t for t in soup.find_all("table") if not t.find("thead") and len(t.find_all("td")) > 4]
        if len(layout_tables) > 3:
            add(20, "Table-based layout")

        # Framesets
        if soup.find("frameset") or soup.find("frame"):
            add(50, "Uses HTML frames")

        # Missing meta description
        if not soup.find("meta", {"name": "description"}):
            add(5, "Missing meta description")

        result["oldness_score"] = min(result["oldness_score"], 100)
        result["is_outdated"] = result["oldness_score"] >= 55

    except requests.exceptions.ConnectionError:
        result["issues"].append("Connection error — site may be down")
    except requests.exceptions.Timeout:
        result["oldness_score"] += 10
        result["issues"].append("Very slow response")
    except Exception as e:
        result["issues"].append(f"Check error: {str(e)[:60]}")

    return result
