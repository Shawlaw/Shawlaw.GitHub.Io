"""Validate a built Pages artifact and its existing Markdown article routes."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from homepage import HOME, ROOT, SEED, SITE, read_json, read_projects, require


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.hrefs = []
        self.sources = []
        self.nav = []
        self.in_nav = False

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag == "nav":
            self.in_nav = True
        if tag == "a" and "href" in fields:
            self.hrefs.append(fields["href"])
            if self.in_nav:
                self.nav.append(fields["href"])
        if tag == "img" and "src" in fields:
            self.sources.append(fields["src"])
        if "id" in fields:
            require(fields["id"] not in self.ids, f"重复锚点：{fields['id']}")
            self.ids.add(fields["id"])

    def handle_endtag(self, tag):
        if tag == "nav":
            self.in_nav = False


def check(site, state, homepage_only):
    document = Document()
    document.feed((site / "index.html").read_text(encoding="utf-8"))
    require(document.nav == ["#projects", "#activity", "#articles", "#about"], "站内导航不符合预期")
    for link in document.hrefs:
        if link.startswith("#"):
            require(link[1:] in document.ids, f"首页锚点不存在：{link}")
    for project in read_projects()["projects"]:
        record = state["projects"].get(project["id"], {})
        for entry in ([record["latest"]] if record.get("latest") else []) + record.get("tools", []):
            require(entry["url"] in document.hrefs, f"缺少项目链接：{entry['url']}")
    for article in read_json(HOME / "articles.json"):
        url = article["url"]
        require(url in document.hrefs and url.startswith(SITE + "/"), f"缺少历史入口：{url}")
        if not homepage_only:
            relative = unquote(urlsplit(url).path).lstrip("/")
            options = [site / relative, site / (relative + ".html"), site / relative / "index.html"]
            require(any(p.is_file() for p in options), f"未生成文章：{url}")
    for src in document.sources:
        if src.startswith("./"):
            require((site / src).is_file(), f"截图文件不存在：{src}")
    if not homepage_only:
        for original in ROOT.glob("google*.html"):
            require((site / original.name).is_file(), f"验证文件缺失：{original.name}")
        for private in (site / "homepage", site / "tools", site / "_homepage-cache", site / "_homepage-media"):
            require(not private.exists(), f"站点包含构建文件：{private}")
    print("首页导航、项目版本、截图和旧文章入口检查通过。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--status", type=Path, default=SEED)
    parser.add_argument("--homepage-only", action="store_true")
    args = parser.parse_args()
    try:
        check(args.site, read_json(args.status), args.homepage_only)
    except (ValueError, OSError, KeyError) as error:
        raise SystemExit(str(error)) from error
