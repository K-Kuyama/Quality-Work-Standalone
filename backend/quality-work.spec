# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['quality-work.py'],
    pathex=[],
    binaries=[],
    datas=[
        # --- アプリ固有データ ---
        ('media/audio_settings.json','media'),
        ('fixture.json','.'),
        ('QTicon_S.ico','.'),
        ('QW3.png','.'),
        ('frontend/*','frontend'),
        ('frontend/static/css/*','frontend/static/css'),
        ('frontend/static/js/*','frontend/static/js'),
        ('frontend/static/media/*','frontend/static/media'),
        #('templates/index.html','templates'),
        # --- janome辞書 ---
        ('.venv/lib/python3.11/site-packages/janome/sysdic/entries_compact*.py','janome/sysdic'),
        ('.venv/lib/python3.11/site-packages/janome/sysdic/entries_extra*.py','janome/sysdic'),        
    ],
    hiddenimports=[
        'activities.apps','activities.urls',
        'rest_framework.parsers','rest_framework.negotiation','rest_framework.metadata',
    ],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        #使わないと思われるdjangoのモジュールを消去
        'django.contrib.admin', #'django.contrib.auth',
        'django.contrib.admindocs',
        'django.contrib.flatpages',
        'django.contrib.redirects',
        'django.contrib.sites',
        # 使わないscipyモジュールを除外
        #'scipy.fft',
        #'scipy.fft','scipy.signal','scipy.integrate',
        #'scipy.io','scipy.interpolate','scipy.ndimage',
        'sklearn.datasets','sklearn.cluster','sklearn.decomposition',
        'sklearn.tree','sklearn.ensemble','sklearn.neural_network',
        'sklearn.manifold','sklearn.mixture','sklearn.cross_decomposition',
        #'scipy.ndimage',    # 画像処理（今回不要）
        #'scipy.integrate',  # 数値積分（今回不要）
        #'scipy.fft',        # 高速フーリエ変換（今回不要）
        #'scipy.interpolate',# 補間処理（今回不要）
        #'scipy.spatial',    # 空間幾何構造（k-NN等を使わないなら不要）
        #'scipy.signal',     # 信号処理（今回不要）
        #'scipy.cluster',    # クラスタリング（今回不要）
        #'scipy.fft','scipy.signal','scipy.optimize','scipy.integrate',
        #'scipy.stats','scipy.io','scipy.interpolate','scipy.ndimage','scipy.linalg',
    ],
    noarchive=False,
)

def filter_all_django_locales(datas):
    new_datas = []
    for dest, source, kind in datas:
        # django/conf/locale または django/contrib/.../locale を対象にする
        if 'django' in dest and 'locale' in dest:
            # 日本語 (ja) 関連、またはベースとなるディレクトリ構造以外はスキップ
            # (pathに 'ja' が含まれるか、__init__.py などは残す)
            if '/ja/' in dest or dest.endswith('ja') or dest.endswith('__init__.py'):
                new_datas.append((dest, source, kind))
            else:
                continue
        else:
            new_datas.append((dest, source, kind))
    return new_datas

# フィルタリングの適用
a.datas = filter_all_django_locales(a.datas)



pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='quality-work',
    debug=False,
    strip=True,
    upx=True,
    console=True,
    icon='QTicon_S.ico',
)

# Info.plist に含めるプライバシー説明文を定義
# ここに記載した文章が、ユーザーへの許可ダイアログに表示される
info_plist_content = {
    'CFBundleIdentifier': 'jp.systemdesignk2.daemon-start',
    'CFBundleName': 'daemon_start',
    'CFBundlePackageType': 'APPL',
    'CFBundleShortVersionString': '1.0.0',
    'NSMicrophoneUsageDescription': '音声デバイスの使用状況を確認するためにマイクへのアクセス権限が必要です。',
    'NSAppleEventsUsageDescription': 'アクティブなアプリケーション情報を取得するために、システムイベントの制御が必要です。',
    # macOSのセキュリティ緩和（これを入れないと署名後にロードエラーになります）
    'com.apple.security.cs.disable-library-validation': True,
    'com.apple.security.cs.allow-jit': True,
}


coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    #strip=False,
    strip=True,
    upx=True,
    name='quality-work',
    # 3. ここで Info.plist を生成するように設定を追加
    info_plist=info_plist_content,
)

# app形式にするための設定を追加
app = BUNDLE(
    coll, # ← exeではない
    name='quality-work.app',
    bundle_id='jp.systemdesignk2.quality-work',
    info_plist=info_plist_content,
    )
    
import shutil
import os

# 1. パスの設定
# COLLECTで作成された中身が quality-work.app/Contents/Resources に集約されます
app_path = os.path.join(DISTPATH, 'quality-work.app')
resource_dest = os.path.join(app_path, 'Contents', 'Resources', 'templates')
source_templates = os.path.abspath('templates') # 開発環境のtemplatesフォルダ
frameworks_dir = os.path.join(app_path, 'Contents', 'Frameworks')
link_path = os.path.join(frameworks_dir, 'templates')

# 2. コピーの実行
if os.path.exists(app_path):
    print(f"--- Post-Build Process: Copying templates ---")
    if os.path.exists(resource_dest):
        shutil.rmtree(resource_dest)
    
    # templatesフォルダごとコピー
    shutil.copytree(source_templates, resource_dest)
    print(f"Successfully copied templates to: {resource_dest}")
else:
    print(f"Error: {app_path} not found. Skipping copy.")

# 3. Frameworks 配下にシンボリックリンクを作成する
# Frameworks ディレクトリがなければ作成
if not os.path.exists(frameworks_dir):
    os.makedirs(frameworks_dir)
    
# リンク・ファイル・ディレクトリのいずれも存在しない場合のみ実行
if not (os.path.exists(link_path) or os.path.islink(link_path)):
    try:
        # 相対パスでリンク作成
        os.symlink('../Resources/templates', link_path)
        print(f"Created symbolic link: {link_path} -> ../Resources/templates")
    except Exception as e:
        print(f"Warning: Failed to create symlink: {e}")
else:
    print(f"Skip: {target_name} already exists in Frameworks (Link or File).")

print("--- Safe Post-Build Process Completed ---")