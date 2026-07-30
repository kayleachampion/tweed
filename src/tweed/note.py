from pathlib import Path
import frontmatter


class Note:
    """Represents a markdown note."""

    def __init__(self, path):
        self.path = Path(path)

        self.metadata = {}
        self.content = ""


    @property
    def title(self):
        return self.get("title", self.path.stem)


    def load(self):
        """Load the note from disk."""

        if not self.path.exists():
            raise FileNotFoundError(self.path)

        post = frontmatter.load(self.path)

        self.metadata = dict(post.metadata)
        self.content = post.content

        return self


    def save(self):
        """Write the note to disk."""

        post = frontmatter.Post(self.content, **self.metadata)

        self.path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as f:
            frontmatter.dump(post, f)

    def __getitem__(self, key):
        return self.metadata[key]

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def get(self, key, default=None):
        return self.metadata.get(key, default)


    @property
    def id(self):
        return self.get("id", "")


    @property
    def kind(self):
        return self.get("type", "")
