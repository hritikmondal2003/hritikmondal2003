import os
import re
import requests
from datetime import datetime, timezone

USERNAME = os.getenv("GH_USERNAME", "hritikmondal2003")
README_FILE = "README.md"
MAX_REPOS = int(os.getenv("MAX_REPOS", "15"))  # how many to show in the list
INCLUDE_FORKS = os.getenv("INCLUDE_FORKS", "false").lower() == "true"

def fetch_public_repos(username: str, token: str | None = None):
    """Fetch all public repos for the user with pagination."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos = []
    page = 1
    while True:
        params = {
            "per_page": 100,
            "page": page,
            "type": "owner",
            "sort": "updated",
            "direction": "desc",
        }
        r = requests.get(
            f"https://api.github.com/users/{username}/repos",
            headers=headers,
            params=params,
            timeout=30,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        for repo in batch:
            if not INCLUDE_FORKS and repo.get("fork", False):
                continue
            if repo.get("visibility") != "public":
                continue
            if repo.get("archived", False):
                continue
            repos.append(repo)
        page += 1
    return repos

def format_repo_line(repo: dict) -> str:
    name = repo["name"]
    url = repo["html_url"]
    desc = (repo.get("description") or "No description").strip()
    stars = repo.get("stargazers_count", 0)
    pushed_at = repo.get("pushed_at")
    date_str = ""
    if pushed_at:
        dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00")).astimezone(timezone.utc)
        date_str = dt.strftime("%Y-%m-%d")
    line = f"- [{name}]({url}) — {desc} (⭐ {stars} · ⏱ {date_str})"
    return line

def replace_between_markers(text: str, start_marker: str, end_marker: str, new_content: str) -> str:
    pattern = re.compile(
        rf"({re.escape(start_marker)})(.*?){re.escape(end_marker)}",
        re.DOTALL,
    )
    return pattern.sub(rf"\1{new_content}{end_marker}", text)

def main():
    token = os.getenv("GH_TOKEN")  # optional, for higher rate limits
    repos = fetch_public_repos(USERNAME, token)
    # sort again just in case (most recently pushed first)
    repos.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)

    total_count = len(repos)
    list_md = "\n".join(format_repo_line(r) for r in repos[:MAX_REPOS])

    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()

    # Update count
    readme = replace_between_markers(
        readme,
        "<!-- REPO_COUNT:START -->",
        "<!-- REPO_COUNT:END -->",
        str(total_count),
    )

    # Update list
    readme = replace_between_markers(
        readme,
        "<!-- REPO_LIST:START -->",
        "<!-- REPO_LIST:END -->",
        f"\n{list_md}\n" if list_md else "\n_No public repositories found._\n",
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"Updated README with {total_count} public repos (showing {min(total_count, MAX_REPOS)}).")

if __name__ == "__main__":
    main()
