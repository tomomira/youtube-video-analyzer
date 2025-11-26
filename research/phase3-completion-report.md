# Phase 3 完了報告: エクスポート・拡張機能

## 概要

Phase 3では、検索結果のエクスポート機能と、検索条件のプリセット保存・検索履歴機能を実装しました。これにより、ユーザーは検索結果をExcelファイルやGoogle Spreadsheetsに出力でき、よく使う検索条件を保存して再利用したり、過去の検索を振り返ることができるようになります。

## 実装した機能

### 1. Excelエクスポート機能

**ファイル**: `src/infrastructure/excel_exporter.py`

#### 何をするものか

検索結果の動画情報をExcelファイル(.xlsx)に出力する機能です。動画の詳細情報を表形式で整理し、見やすくフォーマットされたExcelファイルとして保存します。

#### なぜ必要か

- **データの永続化**: 検索結果をファイルとして保存し、後で参照できる
- **データ分析**: Excelで開いて、さらに分析・加工が可能
- **レポート作成**: 動画リストを報告書や企画書の資料として活用できる
- **オフライン参照**: インターネット接続なしでも動画情報を確認できる

#### 主な機能

1. **ヘッダー行の作成**
   - タイトル、URL、チャンネル名、再生回数など14項目のヘッダー
   - 青色の背景、白色の太字テキストで視認性向上

2. **データのフォーマット**
   - 再生回数、いいね数、コメント数: カンマ区切りの数値形式
   - 公開日: `YYYY-MM-DD` 形式
   - URL、サムネイルURL: クリック可能なハイパーリンク
   - タグ: カンマ区切りの文字列

3. **カラム幅の自動調整**
   - 日本語を考慮した幅計算（全角文字は2文字分）
   - 最小20文字、最大80文字に制限して読みやすさを確保

#### 使用例

```python
from src.infrastructure.excel_exporter import ExcelExporter
from src.domain.models import VideoInfo

exporter = ExcelExporter()

# 動画リストをExcelに出力
exporter.export(videos, "検索結果.xlsx")
```

#### 技術的な詳細

- **ライブラリ**: `openpyxl`（Excelファイル生成）
- **スタイリング**: Font、Alignment、PatternFillを使用
- **エラーハンドリング**: 空のリスト、ファイル書き込みエラーに対応

---

### 2. Google Sheetsエクスポート機能

**ファイル**: `src/infrastructure/sheets_exporter.py`

#### 何をするものか

検索結果の動画情報をGoogle Spreadsheetsに直接書き込む機能です。クラウド上のスプレッドシートに出力することで、複数人での共有や共同編集が可能になります。

#### なぜ必要か

- **クラウド連携**: Googleドライブに自動保存され、どこからでもアクセス可能
- **共同作業**: チームメンバーと検索結果を共有して議論できる
- **リアルタイム更新**: 最新の検索結果をクラウドで管理
- **Googleエコシステム統合**: GoogleドキュメントやGoogleスライドとの連携が容易

#### 主な機能

1. **スプレッドシートの自動作成・取得**
   - 指定された名前のスプレッドシートが存在しない場合は新規作成
   - 既存のスプレッドシートがある場合は上書き

2. **一括データ書き込み**
   - ヘッダーとデータをまとめて書き込み（APIコール数削減）
   - 効率的な処理で高速化

3. **フォーマット設定**
   - ヘッダー行: 青色背景、白色太字、中央揃え
   - カラム幅: 各項目に適した幅に自動調整

4. **エラーハンドリング**
   - gspreadライブラリの有無をチェック
   - 認証情報ファイルの存在確認
   - API呼び出しエラーに対応

#### 使用例

```python
from src.infrastructure.sheets_exporter import SheetsExporter

# 認証情報ファイルを指定
exporter = SheetsExporter(credentials_path="credentials.json")

# Google Sheetsに出力
url = exporter.export(
    videos,
    spreadsheet_name="YouTube動画リスト",
    worksheet_name="2025年1月検索結果"
)

print(f"スプレッドシートURL: {url}")
```

#### 技術的な詳細

- **ライブラリ**: `gspread`、`google-auth`
- **認証**: サービスアカウント認証（OAuth2）
- **スコープ**: `spreadsheets`、`drive`
- **API最適化**: batch_updateで一括操作

#### セットアップ方法

1. Google Cloud Consoleでプロジェクトを作成
2. Google Sheets API、Google Drive APIを有効化
3. サービスアカウントを作成してJSONキーをダウンロード
4. `.env`に`GOOGLE_CREDENTIALS_PATH`を設定

---

### 3. SQLiteデータベース初期化

**ファイル**: `src/database/init_db.py`

#### 何をするものか

プリセットと検索履歴を保存するためのSQLiteデータベースを初期化する機能です。アプリケーション起動時に必要なテーブルが存在しない場合は自動的に作成します。

#### なぜ必要か

- **データの永続化**: アプリケーションを閉じても検索条件や履歴が保持される
- **軽量**: SQLiteは追加のサーバー不要で動作する組み込みデータベース
- **高速**: ローカルファイルベースで高速アクセス
- **標準ライブラリ**: Pythonの標準ライブラリで追加インストール不要

#### テーブル構成

##### search_presetsテーブル（検索プリセット）

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | INTEGER | 主キー（自動採番） |
| name | TEXT | プリセット名（ユニーク） |
| keyword | TEXT | 検索キーワード |
| min_view_count | INTEGER | 最小再生回数 |
| max_view_count | INTEGER | 最大再生回数 |
| video_type | TEXT | 動画タイプ（NORMAL/SHORT/ALL） |
| published_after | TEXT | 公開日開始（ISO 8601形式） |
| published_before | TEXT | 公開日終了（ISO 8601形式） |
| max_results | INTEGER | 最大取得件数 |
| sort_order | TEXT | ソート順 |
| created_at | TEXT | 作成日時（ISO 8601形式） |
| updated_at | TEXT | 更新日時（ISO 8601形式） |

##### search_historyテーブル（検索履歴）

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | INTEGER | 主キー（自動採番） |
| keyword | TEXT | 検索キーワード |
| min_view_count | INTEGER | 最小再生回数 |
| max_view_count | INTEGER | 最大再生回数 |
| video_type | TEXT | 動画タイプ |
| published_after | TEXT | 公開日開始 |
| published_before | TEXT | 公開日終了 |
| max_results | INTEGER | 最大取得件数 |
| sort_order | TEXT | ソート順 |
| result_count | INTEGER | 検索結果件数 |
| searched_at | TEXT | 検索日時（ISO 8601形式） |

**インデックス**: `searched_at`に降順インデックス（最新順の取得を高速化）

#### 使用例

```python
from src.database.init_db import DatabaseInitializer

# データベース初期化
initializer = DatabaseInitializer("youtube_analyzer.db")
initializer.initialize()

# データベースリセット（すべてのデータ削除）
initializer.reset_database()
```

#### コマンドライン実行

```bash
# 通常の初期化
python src/database/init_db.py

# リセット（全データ削除）
python src/database/init_db.py --reset
```

---

### 4. プリセット管理サービス

**ファイル**: `src/application/preset_service.py`

#### 何をするものか

検索条件をプリセットとして保存・読込・削除する機能です。よく使う検索条件に名前を付けて保存し、次回以降は名前を選ぶだけで同じ条件で検索できます。

#### なぜ必要か

- **効率化**: 毎回同じ条件を入力する手間が省ける
- **再現性**: 過去と同じ条件で検索を再実行できる
- **ユースケース管理**: 目的別に複数の検索条件セットを管理
- **ベストプラクティス共有**: チームで有用な検索条件を共有可能

#### 主な機能

1. **プリセットの保存**
   - 検索条件に名前を付けて保存
   - 同じ名前のプリセットは上書き更新

2. **プリセットの読み込み**
   - 名前でプリセットを検索して取得
   - SearchCriteriaオブジェクトとして復元

3. **プリセット一覧取得**
   - すべてのプリセットを更新日時の降順で取得
   - UI上でリスト表示やドロップダウンに使用

4. **プリセットの削除**
   - 不要になったプリセットを削除

#### 使用例

```python
from src.application.preset_service import PresetService
from src.domain.models import SearchCriteria, VideoType

service = PresetService()

# プリセットを保存
criteria = SearchCriteria(
    keyword="Python チュートリアル",
    min_view_count=10000,
    video_type=VideoType.NORMAL,
    max_results=50
)
preset = service.save_preset("初心者向けPython動画", criteria)

# プリセットを読み込み
loaded_preset = service.load_preset("初心者向けPython動画")
criteria = loaded_preset.criteria

# プリセット一覧を取得
all_presets = service.list_presets()
for preset in all_presets:
    print(f"{preset.name}: {preset.criteria.keyword}")

# プリセットを削除
service.delete_preset("初心者向けPython動画")
```

#### 技術的な詳細

- **データベース**: SQLiteを使用
- **自動初期化**: データベースファイルがない場合は自動作成
- **更新判定**: 同じ名前のプリセットは更新、新規名は挿入
- **日時管理**: created_at、updated_atを自動記録

---

### 5. 検索履歴サービス

**ファイル**: `src/application/history_service.py`

#### 何をするものか

過去に実行した検索の履歴を自動的に記録・取得する機能です。いつ、どんなキーワードで、何件の結果が得られたかを保存し、後で振り返ることができます。

#### なぜ必要か

- **検索の振り返り**: 過去の検索内容を確認できる
- **再検索**: 同じ条件で再度検索したいときに便利
- **分析**: どのキーワードがよく使われているかを把握
- **学習**: 効果的な検索条件のパターンを発見

#### 主な機能

1. **検索履歴の自動記録**
   - 検索完了時に自動的に履歴を保存
   - 検索条件、結果件数、実行日時を記録

2. **最近の検索履歴取得**
   - 新しい順に指定件数まで取得
   - デフォルトは最新50件

3. **キーワード検索**
   - 特定のキーワードを含む履歴を検索
   - LIKE検索で部分一致対応

4. **履歴の削除**
   - 個別削除: IDで指定して削除
   - 一括削除: すべての履歴をクリア

#### 使用例

```python
from src.application.history_service import HistoryService
from src.domain.models import SearchCriteria

service = HistoryService()

# 検索履歴を記録（通常はMainWindowが自動で実行）
criteria = SearchCriteria(keyword="Python")
history = service.add_history(criteria, result_count=42)

# 最近の検索履歴を取得
recent_history = service.get_recent_history(limit=10)
for h in recent_history:
    print(f"{h.searched_at}: {h.criteria.keyword} ({h.result_count}件)")

# キーワードで検索
python_history = service.search_history("Python")

# 履歴を削除
service.delete_history(history.id)

# すべての履歴をクリア
deleted_count = service.clear_all_history()
```

#### 技術的な詳細

- **自動記録**: MainWindowで検索完了時に自動実行
- **インデックス**: searched_atに降順インデックスで高速取得
- **ISO 8601形式**: 日時はISO 8601形式で保存（タイムゾーン対応）

---

### 6. MainWindowへの統合

**ファイル**: `src/ui/main_window.py`（更新）

#### 実装した統合機能

1. **Excelエクスポートの実装**
   - `_execute_export()`メソッドでExcelExporterを呼び出し
   - ダミー処理を実際のエクスポート処理に置き換え

2. **検索履歴の自動記録**
   - `_search_completed()`で検索成功時に自動的に履歴を保存
   - 検索条件を`_last_search_criteria`に保持

3. **サービスの初期化**
   - `HistoryService`と`ExcelExporter`のインスタンスを作成
   - アプリケーション起動時に初期化

#### 動作フロー

```
[ユーザーが検索実行]
    ↓
[MainWindow._on_search()]
    ↓
[別スレッドで検索実行]
    ↓
[VideoSearchService.search()]
    ↓
[検索完了]
    ↓
[MainWindow._search_completed()]
    ↓
├─ [ResultPanel.display_results()] ← 画面に表示
└─ [HistoryService.add_history()] ← 履歴に記録

[ユーザーがExcelエクスポート]
    ↓
[MainWindow._on_export()]
    ↓
[ファイル保存ダイアログ]
    ↓
[別スレッドでエクスポート実行]
    ↓
[ExcelExporter.export()]
    ↓
[エクスポート完了メッセージ表示]
```

---

## Phase 3で作成したファイル一覧

### 新規作成ファイル

1. `src/infrastructure/excel_exporter.py` - Excelエクスポート機能
2. `src/infrastructure/sheets_exporter.py` - Google Sheetsエクスポート機能
3. `src/database/init_db.py` - データベース初期化
4. `src/application/preset_service.py` - プリセット管理サービス
5. `src/application/history_service.py` - 検索履歴サービス

### 更新ファイル

6. `src/ui/main_window.py` - エクスポート・履歴機能の統合

### ドキュメント

7. `research/phase3-completion-report.md` - この完了報告書

---

## 技術的なハイライト

### 1. エクスポート機能の設計

#### Excelエクスポートの工夫

- **日本語対応の幅計算**: 全角文字を2文字分としてカウント
- **ハイパーリンク**: URLをクリック可能にして利便性向上
- **数値フォーマット**: カンマ区切りで可読性向上

#### Google Sheetsの最適化

- **一括書き込み**: `update()`で全データを一度に書き込みAPIコール数削減
- **batch_update**: カラム幅設定を一括実行

### 2. データベース設計

#### 正規化とインデックス

- **ユニーク制約**: プリセット名の重複防止
- **インデックス**: searched_atで高速な時系列検索

#### 日時の扱い

- **ISO 8601形式**: `datetime.isoformat()`で標準形式に統一
- **タイムゾーン対応**: datetimeオブジェクトをそのまま保存可能

### 3. サービス層の責務分離

- **PresetService**: プリセット管理のみ
- **HistoryService**: 履歴管理のみ
- **単一責任の原則**: 各サービスが明確な役割を持つ

### 4. エラーハンドリング

すべてのサービスで以下のエラーハンドリングを実装：

- **入力バリデーション**: 空のデータ、不正な値をチェック
- **ファイルI/O**: ファイル書き込み失敗に対応
- **データベース**: 接続エラー、SQL実行エラーに対応
- **ロギング**: すべてのエラーをログに記録

---

## テストとデバッグ

### 動作確認方法

#### 1. データベース初期化

```bash
python src/database/init_db.py
```

**確認内容**:
- `youtube_analyzer.db`ファイルが作成される
- search_presetsテーブルが作成される
- search_historyテーブルが作成される

#### 2. プリセット機能のテスト

```python
from src.application.preset_service import PresetService
from src.domain.models import SearchCriteria, VideoType

service = PresetService()

# プリセット保存
criteria = SearchCriteria(keyword="Python", max_results=50)
preset = service.save_preset("テスト", criteria)
print(f"保存成功: {preset.name}")

# プリセット読み込み
loaded = service.load_preset("テスト")
print(f"読み込み成功: {loaded.criteria.keyword}")

# 一覧取得
presets = service.list_presets()
print(f"プリセット数: {len(presets)}")
```

#### 3. 検索履歴のテスト

```python
from src.application.history_service import HistoryService
from src.domain.models import SearchCriteria

service = HistoryService()

# 履歴追加
criteria = SearchCriteria(keyword="Python")
history = service.add_history(criteria, result_count=42)
print(f"履歴追加: ID={history.id}")

# 最近の履歴取得
recent = service.get_recent_history(limit=5)
for h in recent:
    print(f"{h.searched_at}: {h.criteria.keyword} ({h.result_count}件)")
```

#### 4. Excelエクスポートのテスト

```python
from src.infrastructure.excel_exporter import ExcelExporter
from src.domain.models import VideoInfo
from datetime import datetime

exporter = ExcelExporter()

# ダミーデータでテスト
video = VideoInfo(
    video_id="test123",
    title="テスト動画",
    url="https://www.youtube.com/watch?v=test123",
    channel_name="テストチャンネル",
    channel_id="UC1234567890",
    view_count=1000,
    like_count=50,
    comment_count=10,
    published_at=datetime.now(),
    duration_seconds=180,
    is_short=False
)

exporter.export([video], "test_export.xlsx")
print("Excelファイルを確認してください: test_export.xlsx")
```

---

## 既知の制限事項と今後の改善案

### 制限事項

1. **Google Sheetsエクスポート**
   - サービスアカウント認証が必要（セットアップがやや複雑）
   - gspreadライブラリの追加インストールが必要

2. **検索履歴**
   - 履歴が増えすぎると表示が遅くなる可能性
   - 現在は全件保持（自動削除機能なし）

3. **プリセット**
   - UI上でのプリセット選択機能は未実装
   - 現在はCLIやPythonコードからのみ利用可能

### 今後の改善案

1. **Phase 4（UI拡張）での実装予定**
   - プリセット選択ドロップダウン
   - 検索履歴の表示パネル
   - Google Sheetsエクスポートボタン

2. **パフォーマンス改善**
   - 検索履歴の自動アーカイブ（古い履歴を削除）
   - ページネーション対応

3. **機能拡張**
   - プリセットのインポート・エクスポート（JSON形式）
   - 検索履歴の統計情報表示

---

## まとめ

Phase 3では、以下の機能を実装しました：

✅ **Excelエクスポート**: 検索結果を.xlsxファイルに出力
✅ **Google Sheetsエクスポート**: クラウド上のスプレッドシートに出力
✅ **SQLiteデータベース**: プリセット・履歴を保存する基盤
✅ **プリセット管理**: 検索条件の保存・読込・削除
✅ **検索履歴**: 過去の検索を自動記録・振り返り

これらの機能により、ユーザーは：
- 検索結果をファイルやクラウドに保存できる
- よく使う検索条件を保存して効率化できる
- 過去の検索を振り返り、再検索できる

### 次のフェーズ

**Phase 4: UI拡張・統合テスト**
- プリセット選択UIの実装
- 検索履歴表示パネルの追加
- Google Sheetsエクスポートボタンの追加
- 統合テストの実施
- パフォーマンステスト

---

## 付録: 環境変数設定

### .envファイル

```bash
# YouTube Data API v3
YOUTUBE_API_KEY=your_api_key_here

# Google Sheets API（オプション）
GOOGLE_CREDENTIALS_PATH=credentials.json

# アプリケーション設定
LOG_LEVEL=INFO
MAX_SEARCH_RESULTS=500
DATABASE_PATH=youtube_analyzer.db
```

### 必須設定

- `YOUTUBE_API_KEY`: YouTube Data API v3のAPIキー（必須）
- `DATABASE_PATH`: SQLiteデータベースファイルのパス（オプション、デフォルト: youtube_analyzer.db）

### オプション設定

- `GOOGLE_CREDENTIALS_PATH`: Google API認証情報のJSONファイルパス（Google Sheetsエクスポートを使う場合のみ必須）

---

**Phase 3 完了日**: 2025年11月26日
**実装者**: Claude Code
**次のフェーズ**: Phase 4（UI拡張・統合テスト）
