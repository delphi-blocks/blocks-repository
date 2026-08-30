import json
import re
import os
from pathlib import Path
from packaging.version import Version, InvalidVersion
import urllib.request
import urllib.error
import ssl
import time

REPO_ROOT = Path(__file__).parent.parent / ".blocks" / "repository"
GITHUB_API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def api_headers():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "blocks-checker"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers


def api_get(url):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers=api_headers())
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  [WARN] Rate limited or forbidden: {url}")
        elif e.code == 404:
            print(f"  [WARN] Not found: {url}")
        else:
            print(f"  [WARN] HTTP {e.code}: {url}")
        return None
    except Exception as e:
        print(f"  [WARN] Request failed: {e}")
        return None


def parse_version_key(v_str):
    try:
        return Version(v_str)
    except InvalidVersion:
        return None


def collect_manifests():
    """Group manifests by project id, keeping only the latest version."""
    projects = {}
    for manifest_path in REPO_ROOT.rglob("*.manifest.json"):
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)

        pid = data.get("id", "")
        version = data.get("version", "")
        repo_info = data.get("repository", {})
        repo_type = repo_info.get("type", "")
        repo_url = repo_info.get("url", "")

        if repo_type != "github":
            continue

        ver_key = parse_version_key(version)
        if ver_key is None:
            continue

        if pid not in projects or ver_key > projects[pid]["ver_key"]:
            projects[pid] = {
                "ver_key": ver_key,
                "version": version,
                "url": repo_url,
                "name": data.get("name", pid),
            }

    return projects


def extract_owner_repo(url):
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)", url)
    if m:
        return m.group(1), m.group(2)
    return None, None


def classify_url(url):
    if "/tree/" in url:
        return "release"
    if "/commit/" in url:
        sha = url.rsplit("/commit/", 1)[1]
        return "commit", sha
    return "unknown"


def check_release(owner, repo, current_version):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/releases/latest"
    data = api_get(url)
    if not data:
        tags_url = f"{GITHUB_API}/repos/{owner}/{repo}/tags?per_page=5"
        tags = api_get(tags_url)
        if tags and len(tags) > 0:
            latest_tag = tags[0]["name"]
            return latest_tag, None
        return None, None

    tag = data.get("tag_name", "")
    published = data.get("published_at", "")
    return tag, published


def check_commit(owner, repo, commit_sha):
    commits_url = f"{GITHUB_API}/repos/{owner}/{repo}/commits?per_page=1"
    data = api_get(commits_url)
    if not data or len(data) == 0:
        return None, None, False

    latest_sha = data[0]["sha"]
    latest_date = data[0]["commit"]["committer"]["date"]
    has_newer = not latest_sha.startswith(commit_sha[:7]) and latest_sha != commit_sha
    return latest_sha, latest_date, has_newer


def normalize_tag(tag):
    tag = tag.lstrip("v").lstrip("V")
    return tag


def main():
    projects = collect_manifests()
    print(f"Found {len(projects)} GitHub projects\n")
    print(f"{'Project':<40} {'Current':<18} {'Latest':<18} {'Status'}")
    print("-" * 110)

    for pid in sorted(projects.keys()):
        info = projects[pid]
        owner, repo = extract_owner_repo(info["url"])
        if not owner:
            continue

        classification = classify_url(info["url"])
        time.sleep(0.5)

        if classification == "release":
            latest_tag, published = check_release(owner, repo, info["version"])
            if latest_tag is None:
                print(f"{info['name']:<40} {info['version']:<18} {'?':<18} Could not fetch")
                continue

            latest_ver_str = normalize_tag(latest_tag)
            current_ver = parse_version_key(info["version"])
            latest_ver = parse_version_key(latest_ver_str)

            if latest_ver and current_ver and latest_ver > current_ver:
                pub_info = f" (published: {published[:10]})" if published else ""
                print(f"{info['name']:<40} {info['version']:<18} {latest_tag:<18} UPDATE AVAILABLE{pub_info}")
            elif latest_ver and current_ver and latest_ver == current_ver:
                print(f"{info['name']:<40} {info['version']:<18} {latest_tag:<18} Up to date")
            else:
                print(f"{info['name']:<40} {info['version']:<18} {latest_tag:<18} Up to date (or unparseable)")

        elif isinstance(classification, tuple) and classification[0] == "commit":
            commit_sha = classification[1]
            latest_sha, latest_date, has_newer = check_commit(owner, repo, commit_sha)
            if latest_sha is None:
                print(f"{info['name']:<40} {info['version']:<18} {'?':<18} Could not fetch")
                continue

            if has_newer:
                print(f"{info['name']:<40} {info['version']:<18} {latest_sha[:12]:<18} NEWER COMMIT (date: {latest_date[:10]})")
            else:
                print(f"{info['name']:<40} {info['version']:<18} {commit_sha[:12]:<18} Up to date")
        else:
            print(f"{info['name']:<40} {info['version']:<18} {'N/A':<18} Unknown URL format")


if __name__ == "__main__":
    main()
