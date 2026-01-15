import sys
from pathlib import Path

APP_NAME = "Quality-Work"

def get_app_dir():
    """
    定義ファイルなどを格納するユーザーApplicationフォルダの場所を返す
    """
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    elif sys.platform == "win32":
        local_appdata = os.environ.get("LOCALAPPDATA")
        if not local_appdata:
            raise RuntimeError("LOCALAPPDATA is not set")
        return Path(local_appdata) / APP_NAME
    else:
        # Linux (将来用 / 保険)
        return Path.home() / f".{APP_NAME.lower()}"