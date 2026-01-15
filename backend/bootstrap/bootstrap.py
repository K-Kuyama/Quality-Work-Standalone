import sys
import os
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from system.utils import get_app_dir
from .Migrator import MigratorManager


CURRENT_SCHEMA_VERSION = 3


#### DB関係のファイルパス取得関数

def get_db_path() -> Path:
    """
    インストールされた（あるいはインストールする）データベースファイルの場所を返す
    """
    return get_app_dir() / "db.sqlite3"


def get_bundled_resource_path(relative_path: str) -> Path:
    """
    PyInstallerで同梱されたリソースの実体パスを返す
    """
    if getattr(sys, "frozen", False):
        # PyInstaller 実行時
        #base_path = Path(sys._MEIPASS) / "_internal"
        base_path = Path(sys._MEIPASS)
    else:
        # 開発時
        base_path = Path(__file__).resolve().parent.parent
    return base_path / relative_path

def backup_old_db(db_path):
    """
    すでに存在していたデータベースファイルの名前を変更。そのパスを返す。
    
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.with_suffix(f".bak_{ts}")
    shutil.move(db_path, backup_path)
    return backup_path

def read_schema_version(conn):
    try:
        row = conn.execute(
            "SELECT value FROM system_qwmeta WHERE key='schema_version'"
        ).fetchone()
        return int(row[0])
    except Exception:
        return 0  # 超古いDB想定


### 設定ファイル関係の取得関数

def get_audio_conf_path():
     return get_app_dir() / "config" / "audio_settings.json"

def migrate_audio_conf():
    audio_path = get_audio_conf_path()
    # ファイルを格納するディレクトリがなければ作る
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    if not audio_path.exists():
        template_audio_path = get_bundled_resource_path("media/audio_settings.json")
        if not template_audio_path.exists():
            raise RuntimeError("audio_settings template not found")
        shutil.copyfile(template_audio_path, audio_path)
    return True


def migrate_db():
    db_path = get_db_path()
    # ファイルを格納するディレクトリがなければ作る
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        # データベースファイルがない場合、データベーステンプレートファイルをコピー
        template_db = get_bundled_resource_path("db.sqlite3")
        print(f"tmp DB path ={template_db}")
        if not template_db.exists():
            raise RuntimeError("Bundled DB template not found")
        shutil.copyfile(template_db, db_path)
        return True
    else:
        old_conn = sqlite3.connect(db_path)
        old_version = read_schema_version(old_conn)
        old_conn.close()
        print(f"old:{old_version} new:{CURRENT_SCHEMA_VERSION}")
        if old_version == CURRENT_SCHEMA_VERSION:
            # バージョンが同じであれば、今あるデータベースファイルをそのまま使う
            return True
        if old_version > CURRENT_SCHEMA_VERSION:
            # ありえないのでエラー
            raise RuntimeError("DB version is newer than application")
        
        '''
        バージョンが現在のバージョンより古い場合は、移行を行う
        '''
        # 既存データベースファイルの名称を変更
        backup_path = backup_old_db(db_path)
        # データベーステンプレートファイルをdb_pathにコピー
        template_db = get_bundled_resource_path("db.sqlite3")
        if not template_db.exists():
            raise RuntimeError("Bundled DB template not found")
        shutil.copyfile(template_db, db_path)
        
        mt = MigratorManager.getMigrator(old_version, CURRENT_SCHEMA_VERSION)
        mt.migrate(backup_path, db_path)

        return True
    
def bootstart():
    migrate_db()
    migrate_audio_conf()
    return True