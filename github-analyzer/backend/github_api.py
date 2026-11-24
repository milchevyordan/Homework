import os

import requests


BASE_URL = "https://api.github.com"
TIMEOUT = 10
PER_PAGE = 100


class GitHubAPIError(Exception):
    """Raised when GitHub responds with something other than success / not found."""

    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _headers():
    headers = {"Accept": "application/vnd.github+json"}
    # Optional: set GITHUB_TOKEN to raise the rate limit from 60 to 5000 requests/hour.
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get(url, params=None):
    try:
        response = requests.get(url, headers=_headers(), params=params, timeout=TIMEOUT)
    except requests.RequestException as exc:
        raise GitHubAPIError(f"Could not reach GitHub: {exc}") from exc

    if response.status_code == 404:
        return None
    if response.status_code in (403, 429) and response.headers.get("X-RateLimit-Remaining") == "0":
        raise GitHubAPIError(
            "GitHub API rate limit exceeded. Please try again later.", status_code=429
        )
    if not response.ok:
        raise GitHubAPIError(f"GitHub API returned an error ({response.status_code}).")
    return response.json()


def get_user_data(username):
    """
    Call the GitHub API and return a dict with the user's data, or None if the user does not exist.
    """
    return _get(f"{BASE_URL}/users/{username}")


def get_user_repos(username):
    """
    Call the GitHub API and return a list of dicts (repo name, language/technology),
    or None if the user does not exist. Follows pagination so all public repos are returned.
    """
    repos = []
    page = 1
    while True:
        data = _get(
            f"{BASE_URL}/users/{username}/repos",
            params={"per_page": PER_PAGE, "page": page, "sort": "updated"},
        )
        if data is None:
            return None if page == 1 else repos

        repos.extend(
            {
                "name": repo.get("name"),
                "language": repo.get("language"),
                "url": repo.get("html_url"),
                "description": repo.get("description"),
                "stars": repo.get("stargazers_count", 0),
                "fork": repo.get("fork", False),
            }
            for repo in data
        )

        if len(data) < PER_PAGE:
            return repos
        page += 1
