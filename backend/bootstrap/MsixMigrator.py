import os
import tkinter
import shutil
from tkinter import messagebox
from pathlib import Path
from system.utils import get_app_dir


OLD_APP_ID = "SystemDesignK2.Quality-Work_11k7dxfa5g3gm"
APP_NAME ="Quality-Work"
local_appdata_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local")
#old_base_path = os.path.join(os.environ["LOCALAPPDATA"], "Packages", OLD_APP_ID)
old_base_path = os.path.join(local_appdata_path, "Packages", OLD_APP_ID)
old_data_path = os.path.join(old_base_path, "LocalCache", "Local", APP_NAME)


def is_old_app_exist():
    if os.path.exists(old_base_path):
        return True
    else:
        return False


def migrate_msix_data():
    new_data_path = get_app_dir()
    print(new_data_path)
    flag_file = os.path.join(new_data_path, "migrated.txt")
    if os.path.exists(flag_file):
        # フラグファイルがある場合はなにもせず終了
        return True
    if not is_old_app_exist():
        # 旧版がなければなにもせずに抜ける
        return True
    
    ret = messagebox.askyesno('Quality-Work', '旧版(Ver3.5)のQuality-Worが見つかりました。データを移行しますか？') 
    if ret:    #「はい」を選択した場合はTrue
        #file_list =  [p for p in Path(old_data_path).rglob('*') if p.is_file()]
        #for file in file_list:
        #    print(file)
        
        if os.path.exists(new_data_path):
            cpd = messagebox.askyesno('Quality-Work','移行先にはすでにデーターが存在します。旧版のデータを上書きしますが良いですか？')
            if not cpd:
                with open(flag_file, "w") as f:
                    f.write("migration complete!")
                return True
        shutil.copytree(old_data_path, get_app_dir(), dirs_exist_ok=True)
        messagebox.showinfo('Quality-Work', 'データーを移行しました')
        # データ移行が完了していれば、判定のためのフラグファイルを作る
        
        with open(flag_file, "w") as f:
            f.write("migration complete!")
        uinst = messagebox.askyesno('Quality-Work', '旧版(Ver3.5)をアンインストールしますか？ 今はしない場合は「いいえ」をクリックしてください。')
        if uinst:
            nxt = messagebox.askokcancel('Quality-Work', '「OK」を押すとアプリの一覧画面が開きます。ここから「Quality-Work」をアンインストールしてください')
            if nxt:
                os.system("start ms-settings:appsfeatures")
    return True