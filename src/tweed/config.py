from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


DEFAULT_CONFIG = Path.home() / ".config" / "tweed" / "config.toml"


class Config:

    def __init__(self, path=None):
        self.path = Path(path) if path else DEFAULT_CONFIG

        if self.path.exists():
            with open(self.path, "rb") as f:
                self.data = tomllib.load(f)
        else:
            self.data = {}

    @property
    def vault(self):
        value = self.data.get("vault")

        if value is None:
            return None

        return Path(value).expanduser()
