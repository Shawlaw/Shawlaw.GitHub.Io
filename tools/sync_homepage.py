"""Refresh public project metadata and configured screenshots at build time."""
import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import struct
from urllib.error import HTTPError
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from homepage import IDENTIFIER, ROOT, SEED, read_json, read_projects, require, write_json

API = "https://api.github.com/repos/"
RAW = "https://raw.githubusercontent.com/"
CHINA = timezone(timedelta(hours=8))
SNAPSHOT_FILE = "status.json"
MEDIA = "project-media"
ASSET_NAME = re.compile(r"[a-z0-9-]+-[a-f0-9]{64}\.(?:png|jpg|webp)")


def local_day(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(CHINA).date().isoformat()


def today():
    return datetime.now(CHINA).date().isoformat()


class SameHostRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, destination):
        original, redirected = urlsplit(request.full_url), urlsplit(destination)
        require(redirected.scheme == original.scheme and redirected.netloc == original.netloc,
                "上游地址跨域跳转")
        return super().redirect_request(request, fp, code, message, headers, destination)


def fetch(url, token="", maximum=2 * 1024 * 1024):
    headers = {"User-Agent": "Shawlaw-Pages", "Cache-Control": "no-cache"}
    if url.startswith(API):
        headers["Accept"] = "application/vnd.github+json"
        if token:
            headers["Authorization"] = "Bearer " + token
    with build_opener(SameHostRedirect()).open(Request(url, headers=headers), timeout=12) as response:
        payload = response.read(maximum + 1)
        require(len(payload) <= maximum, "上游响应超过大小限制")
        return payload


def json_fetch(url, token=""):
    try:
        return json.loads(fetch(url, token))
    except HTTPError as error:
        if not (token and url.startswith(API) and error.code in (403, 404)):
            raise
        return json.loads(fetch(url))


def release_snapshot(release, repo):
    tag = release["tag_name"]
    require(not release["draft"] and not release["prerelease"] and
            isinstance(tag, str) and 0 < len(tag) <= 128, "Release 状态或 tag 无效")
    return {"version": tag, "date": local_day(release["published_at"]),
            "url": f"https://github.com/{repo}/releases/tag/{quote(tag, safe='')}"}


def sync_release(project, metadata, token):
    repo = project["repo"]
    endpoint = API + repo
    snapshot = {"kind": "release", "latest": None}
    description = metadata.get("description")
    if (project.get("description_source") == "github" and isinstance(description, str)
            and description.strip() and description != project.get("description_baseline")):
        snapshot["description"] = description
    try:
        latest = json_fetch(endpoint + "/releases/latest", token)
    except HTTPError as error:
        if error.code != 404:
            raise
        recent = json_fetch(endpoint + "/releases?per_page=20", token)
        require(isinstance(recent, list) and not any(not r["draft"] and not r["prerelease"] for r in recent),
                f"{repo} 的 Release 接口返回不一致")
        return snapshot
    snapshot["latest"] = release_snapshot(latest, repo)
    return snapshot


def sync_registry(project, previous, metadata):
    registry = json_fetch(project["registry"])
    require(registry["schemaVersion"] == 1 and isinstance(registry["tools"], list), "工具清单版本或结构无效")
    tools, ids = [], set()
    portal = urlsplit(project["homepage"])
    for item in registry["tools"]:
        if item["status"] != "available":
            continue
        ident, version, name = item["id"], item["version"], item["name"]
        target = urlsplit(urljoin(project["homepage"], item["href"]))
        require(IDENTIFIER.fullmatch(ident) and ident not in ids and
                isinstance(name, str) and 0 < len(name.strip()) <= 100 and
                isinstance(version, str) and 0 < len(version.strip()) <= 60 and
                target.scheme == "https" and target.netloc == portal.netloc and target.path.startswith(portal.path)
                and "%" not in target.path and "\\" not in target.path
                and not (target.query or target.fragment), "已上线工具的字段无效")
        tools.append({"id": ident, "name": name, "version": version, "url": target.geturl()})
        ids.add(ident)
    pushed = local_day(metadata["pushed_at"])
    unchanged = tools == previous.get("tools", [])
    day = previous.get("date", pushed) if unchanged else today()
    return {"kind": "registry", "date": day, "tools": tools}


def image_extension(blob):
    if blob.startswith(b"\x89PNG\r\n\x1a\n") and blob[12:16] == b"IHDR":
        width, height = struct.unpack(">II", blob[16:24])
        require(0 < width <= 6000 and 0 < height <= 6000 and blob[-8:-4] == b"IEND", "PNG 尺寸或结构无效")
        return "png"
    if blob.startswith(b"\xff\xd8\xff") and blob.endswith(b"\xff\xd9"):
        return "jpg"
    if blob.startswith(b"RIFF") and blob[8:12] == b"WEBP" and int.from_bytes(blob[4:8], "little") + 8 == len(blob):
        return "webp"
    raise ValueError("截图格式无效，应为 PNG / JPEG / WebP")


def sync_screenshot(project, cache):
    source = project["screenshot_source"]
    blob = fetch(f"{RAW}{project['repo']}/{source['ref']}/{source['path']}", maximum=3 * 1024 * 1024)
    digest = sha256(blob).hexdigest()
    if digest == source["seed_sha256"]:
        return None
    path = Path(MEDIA) / f"{project['id']}-{digest}.{image_extension(blob)}"
    output = cache / path
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(blob)
    return {"file": path.as_posix(), "caption": source.get("caption", "")}


def read_snapshot(cache):
    path = cache / SNAPSHOT_FILE
    if not path.is_file():
        return read_json(SEED), False
    try:
        cached = read_json(path)
        require(cached["schema"] == 1 and isinstance(cached["projects"], dict), "缓存格式无效")
    except (ValueError, TypeError, KeyError, OSError):
        print("缓存不可用，使用仓库快照。")
        return read_json(SEED), False
    return cached, True


def sync(cache, publish, token):
    previous, restored = read_snapshot(cache)
    projects = read_projects()["projects"]
    current = {"schema": 1, "updated": previous["updated"], "projects": {}}
    errors = []
    for project in projects:
        ident, repo = project["id"], project["repo"]
        old = previous["projects"].get(ident, {})
        if old.get("repo") != repo:
            old = {}
        try:
            metadata = json_fetch(API + repo, token)
            require(metadata["full_name"].lower() == repo.lower() and metadata["private"] is False,
                    "仓库应为清单指定的公开仓库")
            if project["group"] == "portal":
                new = sync_registry(project, old, metadata)
            else:
                new = sync_release(project, metadata, token)
        except (OSError, ValueError, TypeError, KeyError) as error:
            errors.append(f"{ident}: {error}")
            new = {key: val for key, val in old.items() if key != "screenshot"}
        if "screenshot_source" in project:
            try:
                screenshot = sync_screenshot(project, cache)
            except (OSError, ValueError, TypeError, KeyError, struct.error) as error:
                errors.append(f"{ident} 截图: {error}")
                screenshot = old.get("screenshot")
            if screenshot:
                file = Path(screenshot["file"])
                require(file.parent == Path(MEDIA) and ASSET_NAME.fullmatch(file.name), "截图缓存路径无效")
                if (cache / file).is_file():
                    new["screenshot"] = screenshot
                else:
                    errors.append(f"{ident} 截图缓存丢失")
        new["repo"] = repo
        current["projects"][ident] = new
    for item in errors:
        print("同步异常：" + item)
    if errors and not restored:
        raise ValueError("本次缺少上次部署的缓存且上游同步失败。保留当前线上部署，下次再试。")
    changed = current["projects"] != previous["projects"]
    if changed:
        current["updated"] = today()
    for entry in current["projects"].values():
        if "screenshot" in entry:
            file = Path(entry["screenshot"]["file"])
            dest = publish / file
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(cache / file, dest)
    if changed or not restored:
        write_json(cache / SNAPSHOT_FILE, current)
    live_images = {Path(entry["screenshot"]["file"]).name
                   for entry in current["projects"].values() if "screenshot" in entry}
    for path in (cache / MEDIA).glob("*"):
        if ASSET_NAME.fullmatch(path.name) and path.name not in live_images:
            path.unlink()
    return changed or not restored, bool(errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=ROOT / "_homepage-cache")
    parser.add_argument("--out", type=Path, default=ROOT / "_site")
    args = parser.parse_args()
    changed, degraded = sync(args.cache, args.out, os.getenv("GH_TOKEN", ""))
    print(f"同步完成，数据变动或首次构建：{changed}，部分数据降级：{degraded}")
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f"changed={str(changed).lower()}\n")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(str(error)) from error
