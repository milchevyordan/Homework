from collections import Counter


class GitHubUser:
    def __init__(self, username, followers=0, repos=None, name=None, avatar_url=None, profile_url=None):
        self.username = username
        self.followers = followers
        self.repos = repos or []
        self.name = name
        self.avatar_url = avatar_url
        self.profile_url = profile_url

    @classmethod
    def from_api(cls, user_data, repos):
        """Build a GitHubUser from the raw GitHub API user payload and the list of repos."""
        return cls(
            username=user_data.get("login"),
            followers=user_data.get("followers", 0),
            repos=repos,
            name=user_data.get("name"),
            avatar_url=user_data.get("avatar_url"),
            profile_url=user_data.get("html_url"),
        )

    @property
    def has_repos(self):
        return len(self.repos) > 0

    @property
    def has_followers(self):
        return self.followers > 0

    def get_language_counts(self):
        """Return a Counter of language -> number of repos using it. Repos without a language are skipped."""
        return Counter(repo["language"] for repo in self.repos if repo.get("language"))

    def get_most_used_language(self):
        """
        Return the most used language across all repos (by number of repos), or None if no repo has one.
        Ties are broken alphabetically so the result is deterministic.
        """
        counts = self.get_language_counts()
        if not counts:
            return None
        return min(counts.items(), key=lambda item: (-item[1], item[0]))[0]

    def get_all_languages(self):
        """Return all languages used across repos, sorted by usage (most used first)."""
        counts = self.get_language_counts()
        return sorted(counts, key=lambda lang: (-counts[lang], lang))

    def to_dict(self):
        counts = self.get_language_counts()
        messages = {}
        if not self.has_followers:
            messages["followers"] = f"{self.username} does not have any followers yet."
        if not self.has_repos:
            messages["repos"] = f"{self.username} does not have any public repositories."
        elif not counts:
            messages["languages"] = f"None of {self.username}'s repositories have a detected language."

        return {
            "username": self.username,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "profile_url": self.profile_url,
            "followers": self.followers,
            "repos": self.repos,
            "repo_count": len(self.repos),
            "most_used_language": self.get_most_used_language(),
            "languages": [{"name": lang, "count": counts[lang]} for lang in self.get_all_languages()],
            "messages": messages,
        }
