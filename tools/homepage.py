"""Build the homepage or edit its project catalog. Python 3.10+."""
import argparse
import base64
from datetime import date
from html import escape
import json
from hashlib import sha256
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "homepage"
CONFIG = HOME / "projects.json"
SEED = HOME / "status.seed.json"
SITE = "https://shawlaw.github.io"
GROUPS = ("portal", "featured", "tools")
IDENTIFIER = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
REPO = re.compile(r"Shawlaw/[A-Za-z0-9_.-]+")
ASSET = re.compile(r"[A-Za-z0-9_.-]+\.(?:webp|png|jpe?g)", re.I)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def asset_path(name):
    require(isinstance(name, str) and ASSET.fullmatch(name), f"无效的素材文件名：{name}")
    path = HOME / "assets" / name
    require(path.is_file(), f"素材不存在：{path}")
    return path


def read_projects():
    return validate_catalog(read_json(CONFIG))


def validate_catalog(catalog):
    require(catalog["schema"] == 1, "不支持的项目清单版本")
    ids, repos = set(), set()
    for p in catalog["projects"]:
        ident, repo = p["id"], p["repo"]
        require(IDENTIFIER.fullmatch(ident) and ident not in ids, f"无效或重复 ID：{ident}")
        require(REPO.fullmatch(repo) and repo.lower() not in repos, f"无效或重复仓库：{repo}")
        require(p["group"] in GROUPS, f"无效分组：{p['group']}")
        for field in ("name", "description", "category"):
            require(isinstance(p[field], str) and p[field].strip(), f"{ident} 缺少 {field}")
        if p["group"] == "portal":
            target = urlsplit(p["homepage"])
            registry = urlsplit(p["registry"])
            require(target.scheme == registry.scheme == "https" and
                    target.netloc == registry.netloc == "shawlaw.github.io" and
                    target.path.startswith("/") and target.path.endswith("/") and
                    registry.path.startswith(target.path) and
                    not (target.query or target.fragment or registry.query or registry.fragment),
                    f"{ident} 的在线入口或清单地址不合法")
        for key in ("icon", "screenshot"):
            if key in p:
                asset_path(p[key])
        if "screenshot_source" in p:
            remote = p["screenshot_source"]
            require("screenshot" in p and re.fullmatch(r"[A-Za-z0-9._-]+", remote["ref"]) and
                    re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", remote["path"]) and
                    not set(remote["path"].split("/")).intersection((".", "..")) and
                    re.fullmatch(r"[a-f0-9]{64}", remote["seed_sha256"]), f"{ident} 的截图来源不合法")
        if "milestone" in p:
            date.fromisoformat(p["milestone"]["date"])
        require(p.get("description_source", "catalog") in ("catalog", "github"), f"{ident} 的简介来源不合法")
        require(p.get("screenshot_tint", "") in ("", "quota", "logcat"), f"{ident} 的截图色板不合法")
        ids.add(ident)
        repos.add(repo.lower())
    return catalog


def e(value):
    return escape(str(value), quote=True)


def link(url, label, css=""):
    u = urlsplit(url)
    require(u.scheme == "https" and u.hostname in {"github.com", "shawlaw.github.io"} and
            u.netloc == u.hostname, f"无效链接：{url}")
    return (f'<a class="{css}" href="{e(url)}" target="_blank" rel="noopener noreferrer">'
            f'{e(label)} <span aria-hidden="true">↗</span></a>')


def image_url(name):
    path = asset_path(name)
    subtype = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}[path.suffix.lower()[1:]]
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/{subtype};base64,{data}"


def image(src, alt="", width=32, height=32, lazy=False):
    return (f'<img class="" src="{e(src)}" alt="{e(alt)}" width="{width}" height="{height}"' +
            (' loading="lazy"' if lazy else '') + '>')


def repo_url(project):
    return f"https://github.com/{project['repo']}"


def card(project, state):
    name = project["name"]
    icon = (f'<span class="project-icon">{image(image_url(project["icon"]))}</span>' if "icon" in project else
            f'<span class="project-icon glyph" aria-hidden="true">{e(project.get("glyph", "◇"))}</span>')
    media = ""
    if "screenshot" in project:
        shot = state.get("screenshot")
        src = "./" + shot["file"] if shot else image_url(project["screenshot"])
        caption = shot.get("caption", "") if shot else project.get("screenshot_caption", "")
        caption = f"<figcaption>{e(caption)}</figcaption>" if caption else ""
        tint = project.get("screenshot_tint")
        css = f"product-shot product-shot-{tint}" if tint else "product-shot"
        media = (f'<figure class="{css}">' +
                 image(src, name + " 产品界面截图", width=850, height=520, lazy=True) + caption + "</figure>")
    current = state.get("latest")
    badge = link(current["url"], current["version"], "version") if current else ""
    description = state.get("description") if project.get("description_source") == "github" else None
    return f"""<article class="project-card">
      {media}
      <div class="project-copy">
        <div class="project-head">
          {icon}
          <div><h3>{e(name)}</h3><p class="project-label">{e(project["category"])}</p></div>
          {badge}
        </div>
        <p class="project-desc">{e(description or project["description"])}</p>
        {link(repo_url(project), "查看仓库", "text-link")}
      </div>
    </article>"""


def portal(project, state):
    items = "".join(f'<li>{link(t["url"], t["name"])} '
                    f'<span class="tool-version">{e(t["version"])}</span></li>' for t in state.get("tools", []))
    return f"""
      <article class="studio-strip">
        <span class="studio-mark" aria-hidden="true"><i></i><i></i><i></i><i></i></span>
        <div class="studio-copy">
          <h3>{e(project["name"])}</h3>
          <p>{e(project["description"])}</p>
          <ul class="tool-links">{items}</ul>
        </div>
        <div class="studio-actions">{link(project["homepage"], "打开 " + project["name"], "primary")}{link(repo_url(project), "源码", "text-link")}</div>
      </article>"""


def activity(project, state):
    if project["group"] == "portal":
        versions = {tool["id"]: tool for tool in state.get("tools", [])}
        order = project.get("registry_activity_order", [])
        ordered = [versions.pop(key) for key in order if key in versions] + list(versions.values())
        labels = project.get("registry_activity_labels", {})
        detail = " / ".join(f"{labels.get(tool['name'], tool['name'])} {tool['version']}" for tool in ordered)
        if state.get("date"):
            yield state["date"], project.get("activity_label", project["name"]), (
                f"站点 · {detail}" if detail else "站点"), project["homepage"]
    for rel in ([state["latest"]] if state.get("latest") else []) + state.get("previous", []):
        detail = project.get("activity_detail", project["category"])
        yield rel["date"], f"{project['name']} {rel['version']}", f"GitHub Release · {detail}", rel["url"]
    if "milestone" in project:
        event = project["milestone"]
        yield event["date"], event["title"], event["meta"], repo_url(project)


def render(output, state):
    projects = read_projects()["projects"]
    require(state["schema"] == 1, "不支持的版本快照格式")
    date.fromisoformat(state["updated"])
    current = state["projects"]
    groups = {key: [] for key in GROUPS}
    events = []
    for project in projects:
        snapshot = current.get(project["id"], {})
        group = project["group"]
        groups[group].append(portal(project, snapshot) if group == "portal" else card(project, snapshot))
        events.extend(activity(project, snapshot))
    sections = "".join(groups["portal"])
    if groups["featured"]:
        sections += '\n      <div class="feature-grid">' + "".join(groups["featured"]) + '</div>'
    if groups["tools"]:
        sections += ('\n      <div class="subhead"><h3>更多工具与基础设施</h3></div>\n'
                     '      <div class="other-grid">' + "".join(groups["tools"]) + '</div>')
    ordered = sorted(events, key=lambda item: item[0], reverse=True)[:24]
    timeline = "".join(f'<li><time datetime="{day}">{day}</time><div><h3>{link(url, title)}</h3>'
                       f'<p>{e(meta)}</p></div></li>' for day, title, meta, url in ordered)
    entries = []
    for article in read_json(HOME / "articles.json"):
        day, category = article["date"], article["category"]
        metadata = f'<time datetime="{day}">{day}</time>' if day else f'<span class="article-topic">{e(category)}</span>'
        entries.append(f'<li data-topic="{e(category)}">{link(article["url"], article["name"])}{metadata}</li>')
    replacements = {"@@AVATAR@@": image_url("avatar.webp"), "@@PROJECTS@@": sections,
                    "@@TIMELINE@@": timeline, "@@ARTICLES@@": "".join(entries), "@@SYNC_DATE@@": state["updated"]}
    template = (HOME / "index.template.html").read_text(encoding="utf-8")
    html = re.sub(r"@@[A-Z_]+@@", lambda match: replacements[match[0]], template)
    output.mkdir(parents=True, exist_ok=True)
    (output / "index.html").write_text(html, encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--out", type=Path, default=ROOT / "_site")
    build.add_argument("--status", type=Path, default=SEED)
    commands.add_parser("check")
    add = commands.add_parser("add")
    for name in ("id", "repo", "name", "description", "category"):
        add.add_argument("--" + name, required=True)
    add.add_argument("--group", choices=("featured", "tools"), default="tools")
    add.add_argument("--icon")
    add.add_argument("--screenshot")
    add.add_argument("--screenshot-source", nargs=3, metavar=("REF", "PATH", "BASELINE_IMAGE"),
                     help="自动同步源码仓库里的截图，基准文件为与本地预览素材对应的未压缩上游原图")
    add.add_argument("--screenshot-caption")
    add.add_argument("--description-source", choices=("catalog", "github"), default="catalog")
    remove = commands.add_parser("remove")
    remove.add_argument("id")
    args = parser.parse_args()
    catalog = read_projects()
    if args.command == "check":
        print(f"项目清单有效，共 {len(catalog['projects'])} 项。")
        return
    if args.command == "build":
        render(args.out, read_json(args.status))
        return
    projects = catalog["projects"]
    if args.command == "remove":
        require(any(p["id"] == args.id for p in projects), f"没有该项目：{args.id}")
        catalog["projects"] = [p for p in projects if p["id"] != args.id]
    else:
        project = {key: value for key, value in vars(args).items()
                   if key not in ("command", "screenshot_source") and value is not None}
        if args.screenshot_source:
            ref, path, baseline = args.screenshot_source
            project["screenshot_source"] = {"ref": ref, "path": path,
                                            "seed_sha256": sha256(Path(baseline).read_bytes()).hexdigest()}
        require(IDENTIFIER.fullmatch(args.id) and all(p["id"] != args.id for p in projects), "ID 无效或已存在")
        require(REPO.fullmatch(args.repo) and all(p["repo"].lower() != args.repo.lower() for p in projects),
                "仓库路径无效或已存在，应为 Shawlaw/仓库名")
        require(all(project[key].strip() for key in ("name", "description", "category")), "名称、简介和分类不能为空")
        for name in ("icon", "screenshot"):
            if name in project:
                asset_path(project[name])
        projects.append(project)
    validate_catalog(catalog)
    write_json(CONFIG, catalog)
    print(f"已更新项目清单：{args.id}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(str(error)) from error
