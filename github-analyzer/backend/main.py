from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from github_api import GitHubAPIError, get_user_data, get_user_repos
from github_user import GitHubUser


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/user")
def get_user(username: str):
    """
    Return followers, repos, most used language and all languages for a GitHub user.
    .strip removes spaces
    """
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Please provide a GitHub username.")

    try:
        user_data = get_user_data(username)
        if user_data is None:
            raise HTTPException(status_code=404, detail=f"GitHub user '{username}' does not exist.")
        repos = get_user_repos(username) or []
    except GitHubAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    return GitHubUser.from_api(user_data, repos).to_dict()
