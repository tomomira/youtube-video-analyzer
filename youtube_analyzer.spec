# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller .spec file for YouTube Video Analyzer

このファイルはPyInstallerでスタンドアロン実行可能ファイルを作成するための設定ファイルです。

使い方:
    # Windowsの場合
    build.bat

    # macOS/Linuxの場合
    bash build.sh

または直接PyInstallerを実行:
    pyinstaller youtube_analyzer.spec
"""

block_cipher = None

# 分析フェーズ: 依存関係を解析
a = Analysis(
    ['src/main.py'],  # エントリーポイント
    pathex=[],
    binaries=[],
    datas=[
        # .envファイル（環境変数テンプレート）
        ('.env.example', '.'),
        # ドキュメント
        ('docs', 'docs'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        # tkinterとその依存関係
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.filedialog',
        # Google API関連
        'googleapiclient',
        'googleapiclient.discovery',
        'googleapiclient.errors',
        'google.auth',
        'google.auth.transport.requests',
        'google_auth_oauthlib',
        # gspread（オプション）
        'gspread',
        # その他
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.utils',
        'isodate',
        'dotenv',
        'sqlite3',
        'webbrowser',
        'threading',
        'datetime',
        'logging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # テスト関連（不要）
        'pytest',
        'pytest-mock',
        'pytest-cov',
        # 開発ツール（不要）
        'black',
        'flake8',
        'mypy',
        'pylint',
        'bandit',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZアーカイブ: Pythonモジュールをアーカイブ化
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXEファイル: 実行可能ファイルを生成
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YouTubeVideoAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # UPXで圧縮（サイズ削減）
    console=False,  # コンソールウィンドウを表示しない（GUIアプリ）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # アイコンファイルがある場合はここで指定: icon='app_icon.ico'
)

# COLLECT: すべてのファイルを1つのディレクトリに集める
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YouTubeVideoAnalyzer',
)

# macOS用: アプリケーションバンドルを作成
# Windowsでは無視される
import sys
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='YouTubeVideoAnalyzer.app',
        icon=None,  # macOS用アイコン: icon='app_icon.icns'
        bundle_identifier='com.youtube.video.analyzer',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
        },
    )
