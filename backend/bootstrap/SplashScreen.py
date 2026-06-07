import tkinter as tk
import os
import sys
from system.utils import get_app_dir
from bootstrap.bootstrap import get_bundled_resource_path

def show_splash_screen(version, duration_ms=5000):
    """
    ロゴ画面とバージョンを画面中央に数秒間表示
    """
    root = tk.Tk()
    root.overrideredirect(True) #ウインドウの枠線やタイトルバーを非表示にする

    # -- デザイン設定 --
    bg_color = "#FFFFFF"
    root.configure(bg=bg_color)

    window_width = 246
    window_height = 300

    # -- 画面中央への配置 --
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # -- 画像の配置 --
    logo_file_path = get_bundled_resource_path("QwLogo.png")
    logo_img = tk.PhotoImage(file=logo_file_path)
    
    label_logo = tk.Label(root, image=logo_img, bg=bg_color)
    label_logo.pack(expand=True, pady=(0,0))
    label_logo.image = logo_img #画像データを保持する

    # -- バージョン情報の配置 --
    current_version = "Version " + version

    label_version = tk.Label(
        root,
        text=current_version,
        font=("Meiryo UI", 12),
        fg="#011c29",
        bg=bg_color
    )

    label_version.pack(expand=True, pady=(0,10))

    # 最前面に表示
    root.attributes("-topmost", True)

    # 指定時間後に閉じる
    root.after(duration_ms, root.destroy)
    root.mainloop()

if __name__ == '__main__':
    show_splash_screen("3.6")
    