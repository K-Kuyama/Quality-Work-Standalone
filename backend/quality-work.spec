# -*- mode: python ; coding: utf-8 -*-
#from PyInstaller.utils.hooks import collect_submodules

#sklearnに関係しては、静的解析で解決できないやり方で
#モジュールインポートしているので、hiddenimportsに関連するモジュールを定義する必要がある。
# sklearnのサブモジュール及び、scipy, joblib, threadpoolctl
# これらについてはモジュールを_internalの中にコピーして抱え持つ必要があり、
# datasに定義しておく必要がある。ただし、サイズが大きくなってしまうため、
# sklearn, scipyは必要なものだけをdatasに入れておき、不要なものはexcludesで除外する。





# --- scikit-learn関連 ---
sklearn_hiddenimports = [
    'sklearn', 'sklearn._config', 'sklearn._distributor_init',  
    'sklearn.base', 'sklearn.utils',
    'sklearn.feature_extraction', 'sklearn.feature_extraction.text',
    'sklearn.linear_model', 'sklearn.model_selection',
    'sklearn.metrics', 'sklearn.preprocessing',
    'sklearn.exceptions',
    'sklearn.externals',           
    'sklearn.externals._joblib',   
    'sklearn.externals._joblib.externals.loky',  
    'sklearn.externals.array_api_compat',        
    'sklern._cyutility',
    'sklearn.utils._isfinite',  # ← Cython モジュールも追加
    'sklearn._loss',
    'sklearn.svm',
]

scipy_hiddenimports = [
    'scipy',
    'scipy.__init__',   
    'scipy.__config__',
    'scipy.version',
    'scipy.sparse',
    'scipy.special',
    'scipy._lib',            
    'scipy._lib._util',      
    'scipy._cyutility', 
    'scipy.linalg',
    'scipy.stats',
    'scipy.spatial',
    'scipy.constants',
    'scipy.optimize',
    'scipy.fft',
    'scipy.integrate', 
    'scipy.interpolate',
    'scipy.ndimage',
]


a = Analysis(
    ['quality-work.py'],
    pathex=[],
    binaries=[],
    datas=[
        # --- アプリ固有データ ---
        ('media/audio_settings.json','media'),
        ('fixture.json','.'),
        ('frontend/*','frontend/'),
        ('frontend/static/css/*','frontend/static/css'),
        ('frontend/static/js/*','frontend/static/js'),
        ('frontend/static/media/*','frontend/static/media'),
        ('templates/index.html','templates'),

        # --- janome辞書 ---
        ('.venv/lib/python3.11/site-packages/janome/sysdic/entries_compact*.py','janome/sysdic'),
        ('.venv/lib/python3.11/site-packages/janome/sysdic/entries_extra*.py','janome/sysdic'),

        # --- sklearn関係（必要部分のみ） ---
        ('.venv/lib/python3.11/site-packages/sklearn/__init__.py', 'sklearn'),
        ('.venv/lib/python3.11/site-packages/sklearn/_config.py', 'sklearn'),
        ('.venv/lib/python3.11/site-packages/sklearn/_distributor_init.py', 'sklearn'),  # ← 追加！
        ('.venv/lib/python3.11/site-packages/sklearn/base.py', 'sklearn'),
        ('.venv/lib/python3.11/site-packages/sklearn/utils', 'sklearn/utils'),
        ('.venv/lib/python3.11/site-packages/sklearn/feature_extraction', 'sklearn/feature_extraction'),
        ('.venv/lib/python3.11/site-packages/sklearn/linear_model', 'sklearn/linear_model'),
        ('.venv/lib/python3.11/site-packages/sklearn/model_selection', 'sklearn/model_selection'),
        ('.venv/lib/python3.11/site-packages/sklearn/metrics', 'sklearn/metrics'),
        ('.venv/lib/python3.11/site-packages/sklearn/preprocessing', 'sklearn/preprocessing'),
        ('.venv/lib/python3.11/site-packages/sklearn/__check_build', 'sklearn/__check_build'),
        ('.venv/lib/python3.11/site-packages/sklearn/.dylibs/*', 'sklearn/.dylibs'),
        ('.venv/lib/python3.11/site-packages/sklearn/exceptions.py', 'sklearn'),
        ('.venv/lib/python3.11/site-packages/sklearn/externals', 'sklearn/externals'),
        ('.venv/lib/python3.11/site-packages/sklearn/_cyutility*.so', 'sklearn/'),
        ('.venv/lib/python3.11/site-packages/sklearn/utils/_isfinite*.so', 'sklearn/utils/'),
        ('.venv/lib/python3.11/site-packages/sklearn/_loss', 'sklearn/_loss'),
        ('.venv/lib/python3.11/site-packages/sklearn/svm', 'sklearn/svm'),

        # --- 依存関係 ---
        ('.venv/lib/python3.11/site-packages/threadpoolctl.py', '.'),
        ('.venv/lib/python3.11/site-packages/joblib', 'joblib'),
        #('.venv/lib/python3.11/site-packages/scipy', 'scipy'),
        ('.venv/lib/python3.11/site-packages/scipy/*.py', 'scipy'),
        #('.venv/lib/python3.11/site-packages/scipy/__config__.py', 'scipy'),
        ('.venv/lib/python3.11/site-packages/scipy/sparse', 'scipy/sparse'),
        ('.venv/lib/python3.11/site-packages/scipy/special', 'scipy/special'),
        # .venv/lib/python3.11/site-packages/scipy/_lib の全ファイルを含める
        ('.venv/lib/python3.11/site-packages/scipy/_lib', 'scipy/_lib'),
        ('.venv/lib/python3.11/site-packages/scipy/_cyutility*.so', 'scipy/'),  # macOSの場合は .so
        ('.venv/lib/python3.11/site-packages/scipy/linalg', 'scipy/linalg'),
        ('.venv/lib/python3.11/site-packages/scipy/stats', 'scipy/stats'),
        ('.venv/lib/python3.11/site-packages/scipy/spatial', 'scipy/spatial'),
        ('.venv/lib/python3.11/site-packages/scipy/constants', 'scipy/constants'),
        ('.venv/lib/python3.11/site-packages/scipy/optimize', 'scipy/optimize'),
        ('.venv/lib/python3.11/site-packages/scipy/fft', 'scipy/fft'),
        ('.venv/lib/python3.11/site-packages/scipy/integrate', 'scipy/integrate'),
        ('.venv/lib/python3.11/site-packages/scipy/interpolate', 'scipy/interpolate'),
        ('.venv/lib/python3.11/site-packages/scipy/ndimage', 'scipy/ndimage'),
        # --- オーディオ関係 ---
        ('.venv/lib/python3.11/site-packages/CoreAudio', 'CoreAudio'),
    ],

    hiddenimports=[
        'activities.apps','activities.urls',
        'rest_framework.parsers','rest_framework.negotiation','rest_framework.metadata',
        'threadpoolctl','joblib'
    ] + sklearn_hiddenimports + scipy_hiddenimports,

    excludes=[
        # 不要な重いモジュールを除外
        'sklearn.datasets','sklearn.cluster','sklearn.decomposition',
        'sklearn.tree','sklearn.ensemble','sklearn.neural_network',
        'sklearn.manifold','sklearn.mixture','sklearn.cross_decomposition',
        'scipy.fft','scipy.signal','scipy.optimize','scipy.integrate',
        'scipy.stats','scipy.io','scipy.interpolate','scipy.ndimage','scipy.linalg',
    ],
    

    noarchive=False,
)

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
