"""Local editor and GitHub Pages publisher for the X-ING portfolio."""
from argparse import ArgumentParser
from hashlib import sha256
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from json import dumps, loads
from mimetypes import guess_type
from os import environ
from pathlib import Path
from shutil import copyfile
from subprocess import CalledProcessError, TimeoutExpired, run
from sys import executable
from tempfile import TemporaryDirectory
from threading import Lock
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen

from build import COURSES, PLAN
from content import CONTENT, read_content, validate

ROOT = CONTENT.parents[1]
REPO = "https://github.com/3315531721/3315531721.github.io.git"
RAW_CONTENT = "https://raw.githubusercontent.com/3315531721/3315531721.github.io/main/_source/content.json"
STATE = CONTENT.with_name(".local-published")
LOCK = Lock()
PAGES = {"index.html", "courses.html", "plan.html", "projects.html", "notes.html"}
PAGES.update(f"courses/{slug}.html" for slug in COURSES)
ASSETS = {
    "assets/bootstrap.min.css", "assets/portfolio.css", "assets/portfolio.js",
    "assets/search-index.js", "assets/mnist-samples.png", "assets/sakurairo-cover.webp",
    "assets/study-desk.webp",
}


def digest(raw):
    return sha256(raw).hexdigest()


def rebuild():
    run([executable, "-B", str(CONTENT.with_name("build.py"))], cwd=ROOT,
        check=True, capture_output=True, timeout=15)


def save(data, revision):
    previous = CONTENT.read_bytes()
    if digest(previous) != revision:
        raise ValueError("草稿已在另一处编辑，请刷新后台再保存。")
    clean = validate(data, COURSES)
    serialized = (dumps(clean, ensure_ascii=False, indent=2) + "\n").encode()
    temporary = CONTENT.with_suffix(".tmp")
    temporary.write_bytes(serialized)
    temporary.replace(CONTENT)
    try:
        rebuild()
    except (CalledProcessError, TimeoutExpired):
        temporary.write_bytes(previous)
        temporary.replace(CONTENT)
        rebuild()
        raise ValueError("生成页面失败，已恢复上一版。")
    return digest(serialized)


def establish_baseline():
    if STATE.exists():
        return
    try:
        with urlopen(RAW_CONTENT, timeout=6) as response:
            public_content = response.read(131073)
        validate(loads(public_content), COURSES)
    except (OSError, ValueError):
        return
    STATE.write_text(digest(public_content) + "\n", encoding="utf-8")


def git(repo, *args, check=True):
    return run(["git", *args], cwd=repo, check=check, capture_output=True,
               text=True, timeout=35, env={**environ, "GIT_TERMINAL_PROMPT": "0"})


def publish(revision):
    if digest(CONTENT.read_bytes()) != revision:
        raise ValueError("请保存当前草稿后再发布。")
    establish_baseline()
    if not STATE.exists():
        raise ValueError("暂时无法读取 GitHub 的已发布版本。")
    with TemporaryDirectory(prefix="xing-admin-publish-") as temporary:
        repo = Path(temporary)
        git(repo, "clone", "--depth", "1", "--branch", "main", REPO, ".")
        if (repo / "_source/build.py").read_bytes() != (ROOT / "_source/build.py").read_bytes():
            raise ValueError("GitHub 上的站点模板已更新，请同步本地项目后再发布。")
        if digest((repo / "_source/content.json").read_bytes()) != STATE.read_text().strip():
            raise ValueError("GitHub 上的内容已更新，请先合并最新内容。")
        files = sorted(PAGES | {"assets/search-index.js", "_source/content.json"})
        for file in files:
            copyfile(ROOT / file, repo / file)
        git(repo, "add", "--", *files)
        delta = git(repo, "diff", "--cached", "--quiet", check=False)
        if delta.returncode == 0:
            return {"message": "发布版本已包含当前内容。"}
        if delta.returncode != 1:
            raise ValueError("Git 无法检查发布内容。")
        git(repo, "diff", "--cached", "--check")
        git(repo, "-c", "user.name=3315531721",
            "-c", "user.email=50486879+3315531721@users.noreply.github.com",
            "commit", "-m", "Update learning portfolio content")
        commit = git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
        git(repo, "push", "origin", "HEAD:main")
        STATE.write_text(revision + "\n", encoding="utf-8")
        return {"message": f"已提交 {commit}。GitHub Pages 完成部署后即可查看。"}


class Admin(BaseHTTPRequestHandler):
    def allowed_host(self):
        return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

    def reply(self, status, data, mime):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(data)

    def json(self, status, value):
        self.reply(status, dumps(value, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def file(self, path):
        mime = guess_type(path.name)[0] or "application/octet-stream"
        if mime.startswith("text/") or mime == "application/javascript":
            mime += "; charset=utf-8"
        self.reply(HTTPStatus.OK, path.read_bytes(), mime)

    def do_GET(self):
        if not self.allowed_host():
            return self.json(HTTPStatus.FORBIDDEN, {"error": "请从本地后台地址进入。"})
        path = unquote(urlsplit(self.path).path)
        if path == "/":
            return self.file(CONTENT.with_name("admin.html"))
        if path == "/admin.js":
            return self.file(CONTENT.with_name("admin.js"))
        if path == "/api/content":
            with LOCK:
                data = read_content(COURSES)
                revision = digest(CONTENT.read_bytes())
            defaults = {slug: {"title": name, "intro": intro, "task": task}
                        for slug, (name, _, intro, task) in COURSES.items()}
            return self.json(HTTPStatus.OK, {"data": data, "revision": revision,
                                           "courses": defaults, "plan": {title: desc for title, _, desc in PLAN}})
        if path.startswith("/preview/"):
            relative = path.removeprefix("/preview/") or "index.html"
            if relative in PAGES or relative in ASSETS:
                return self.file(ROOT / relative)
        return self.json(HTTPStatus.NOT_FOUND, {"error": "页面不存在。"})

    def do_PUT(self):
        self.mutation("/api/content", lambda request: {"revision": save(request["data"], request["revision"])})

    def do_POST(self):
        self.mutation("/api/publish", lambda request: publish(request["revision"]))

    def mutation(self, route, action):
        if not self.allowed_host() or self.headers.get("Origin") != f"http://127.0.0.1:{self.server.server_port}":
            return self.json(HTTPStatus.FORBIDDEN, {"error": "请求来源不属于本地后台。"})
        if urlsplit(self.path).path != route or self.headers.get_content_type() != "application/json":
            return self.json(HTTPStatus.BAD_REQUEST, {"error": "请求地址或格式无效。"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 131072:
                raise ValueError("内容为空或超过 128 KB。")
            request = loads(self.rfile.read(length))
            with LOCK:
                response = action(request)
        except (ValueError, KeyError, TypeError) as exc:
            return self.json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except (CalledProcessError, TimeoutExpired, OSError):
            return self.json(HTTPStatus.BAD_GATEWAY, {"error": "发布失败。请检查当前 GitHub 登录和网络后重试。"})
        return self.json(HTTPStatus.OK, response)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=57821)
    args = parser.parse_args()
    rebuild()
    establish_baseline()
    with ThreadingHTTPServer(("127.0.0.1", args.port), Admin) as server:
        print(f"作品集管理后台 http://127.0.0.1:{server.server_port}/", flush=True)
        server.serve_forever()
