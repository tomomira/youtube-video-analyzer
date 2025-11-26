# Phase 4 完了報告: UI拡張・統合テスト

## 概要

Phase 4では、Phase 3で実装したエクスポート・拡張機能をUIに統合し、統合テストを作成しました。これにより、ユーザーはGUIから直接プリセット管理、検索履歴の閲覧、Google Sheetsへのエクスポートが可能になりました。

## 実装した機能

### 1. プリセット管理UI（SearchPanel拡張）

**ファイル**: `src/ui/search_panel.py`（更新）

#### 何をするものか

SearchPanelの最上部にプリセット管理機能を追加しました。ユーザーは検索条件を名前を付けて保存し、後で呼び出すことができます。

#### 追加したUI要素

1. **プリセット選択コンボボックス**
   - 保存済みのプリセット一覧から選択可能
   - 読み取り専用

2. **読込ボタン**
   - 選択したプリセットの検索条件を入力フィールドに反映

3. **保存ボタン**
   - 現在の検索条件をプリセットとして保存
   - プリセット名を入力ダイアログで指定

4. **削除ボタン**
   - 選択したプリセットを削除
   - 確認ダイアログを表示

#### 主な実装内容

```python
# プリセット選択UI
preset_frame = ttk.Frame(self)
self.preset_combo = ttk.Combobox(preset_frame, state="readonly")
ttk.Button(preset_frame, text="読込", command=self._load_preset)
ttk.Button(preset_frame, text="保存", command=self._save_preset)
ttk.Button(preset_frame, text="削除", command=self._delete_preset)
```

#### 動作フロー

```
[保存]
1. ユーザーが検索条件を入力
2. 「保存」ボタンをクリック
3. プリセット名入力ダイアログ表示
4. PresetService.save_preset()で保存
5. プリセット一覧を更新

[読込]
1. プリセットをコンボボックスから選択
2. 「読込」ボタンをクリック
3. PresetService.load_preset()で読込
4. 検索条件を入力フィールドに設定

[削除]
1. プリセットをコンボボックスから選択
2. 「削除」ボタンをクリック
3. 確認ダイアログ表示
4. PresetService.delete_preset()で削除
5. プリセット一覧を更新
```

---

### 2. 検索履歴パネル（新規作成）

**ファイル**: `src/ui/history_panel.py`

#### 何をするものか

過去の検索履歴を一覧表示する独立したウィンドウです。履歴から再検索したり、不要な履歴を削除したりできます。

#### UI構成

1. **ツールバー**
   - 更新ボタン: 履歴一覧を最新の状態に更新
   - すべてクリアボタン: 全履歴を削除（確認あり）
   - 履歴件数ラベル: 現在の履歴数を表示

2. **履歴テーブル（Treeview）**
   - 検索日時: YYYY-MM-DD HH:MM:SS形式
   - キーワード: 検索キーワード
   - 結果件数: 「○件」形式
   - 条件: 再生回数範囲、動画タイプの概要

3. **ボタンパネル**
   - この条件で再検索: 選択した履歴で再検索
   - 削除: 選択した履歴を削除
   - 閉じる: ウィンドウを閉じる

#### 主な機能

```python
class HistoryPanel(tk.Toplevel):
    """検索履歴パネル（別ウィンドウ）"""

    def _load_history(self):
        """最近100件の履歴を取得して表示"""
        histories = self.history_service.get_recent_history(limit=100)
        # Treeviewに表示

    def _research_selected(self):
        """選択した履歴で再検索"""
        history = self._get_selected_history()
        self.on_search_callback(history.criteria)
        self.destroy()  # ウィンドウを閉じる
```

#### ダブルクリック動作

- 履歴アイテムをダブルクリックすると、その条件で即座に再検索が実行されます
- メインウィンドウの検索パネルに条件が設定され、検索が開始されます

---

### 3. MainWindowへの統合

**ファイル**: `src/ui/main_window.py`（更新）

#### 追加したメニュー項目

##### ファイルメニュー

- **Excelにエクスポート**: 現在の検索結果をExcelファイルに出力
- **Google Sheetsにエクスポート**: 現在の検索結果をGoogle Spreadsheetsに出力
- 終了

##### 表示メニュー（新規）

- **検索履歴**: 検索履歴パネルを開く

#### Google Sheetsエクスポート機能

```python
def _export_to_sheets(self):
    """Google Sheetsエクスポート"""
    # スプレッドシート名を入力
    spreadsheet_name = simpledialog.askstring(
        "Google Sheetsエクスポート",
        "スプレッドシート名を入力してください:",
        initialvalue="YouTube動画リスト"
    )

    # 別スレッドでエクスポート実行
    thread = threading.Thread(
        target=self._execute_sheets_export,
        args=(videos, spreadsheet_name),
        daemon=True
    )
    thread.start()
```

#### エラーハンドリング

Google Sheetsエクスポートでは、以下のエラーを適切に処理：

1. **gspreadライブラリ未インストール**
   ```
   Google Sheetsエクスポートに必要なライブラリがインストールされていません。
   以下のコマンドを実行してください:
   pip install gspread google-auth
   ```

2. **認証情報未設定**
   ```
   Google API認証情報が設定されていません。
   .envファイルにGOOGLE_CREDENTIALS_PATHを設定してください。
   ```

#### クリップボード連携

Google Sheetsエクスポート完了時、スプレッドシートのURLを自動的にクリップボードにコピーします。

```python
def _sheets_export_completed(self, url: str):
    # URLをクリップボードにコピー
    self.root.clipboard_clear()
    self.root.clipboard_append(url)

    messagebox.showinfo(
        "Google Sheetsエクスポート完了",
        f"スプレッドシートに保存しました。\n\nURL（クリップボードにコピー済み）:\n{url}"
    )
```

---

### 4. 統合テスト

**ファイル**: `tests/test_integration.py`

#### テストクラス構成

##### TestPresetIntegration（プリセット統合テスト）

1. `test_preset_save_and_load`: プリセットの保存と読み込み
2. `test_preset_update`: 同名プリセットの上書き更新
3. `test_preset_delete`: プリセットの削除
4. `test_preset_list`: プリセット一覧の取得

##### TestHistoryIntegration（履歴統合テスト）

1. `test_history_add_and_get`: 履歴の追加と取得
2. `test_history_multiple_entries`: 複数履歴の新しい順ソート確認
3. `test_history_search`: キーワードで履歴検索
4. `test_history_delete`: 履歴の個別削除
5. `test_history_clear_all`: 全履歴のクリア

##### TestExcelExportIntegration（Excelエクスポート統合テスト）

1. `test_excel_export`: 正常なエクスポート
2. `test_excel_export_empty_list`: 空リストでのエラーハンドリング

##### TestEndToEndWorkflow（エンドツーエンドテスト）

1. `test_search_save_export_workflow`: 検索→プリセット保存→履歴記録→Excelエクスポートの一連の流れ

#### テスト結果

```
12 passed, 4 warnings in 13.27s
```

- **全テストケースが合格**: 12/12 passed
- **警告**: openpyxlの`datetime.utcnow()`非推奨警告（ライブラリ側の問題）

---

## 修正した不具合

### 1. データベーステーブル未作成エラー

**問題**: テスト実行時に `no such table: search_presets` エラー

**原因**: PresetService/HistoryServiceがファイル存在チェックのみで、空ファイルの場合テーブルが作成されない

**修正**:
```python
# 修正前
if not os.path.exists(self.db_path):
    initializer.initialize()

# 修正後
# ファイルの有無に関わらず初期化（IF NOT EXISTS句で冪等性確保）
initializer.initialize()
```

### 2. フィールド名の不一致

**問題**: `SearchCriteria`の属性名と使用箇所の不一致

**不一致箇所**:
- `sort_order` ↔ `order`
- `SearchPreset.id` ↔ `SearchPreset.preset_id`
- `SearchHistory.id` ↔ `SearchHistory.history_id`
- `SearchHistory.searched_at` ↔ `SearchHistory.executed_at`

**修正**:
- すべての参照を正しい属性名に統一
- preset_service.py: `criteria.sort_order` → `criteria.order`
- history_service.py: `criteria.sort_order` → `criteria.order`
- history_panel.py: `history.id` → `history.history_id`
- history_panel.py: `history.searched_at` → `history.executed_at`
- search_panel.py: `criteria.sort_order` → `criteria.order`
- tests/test_integration.py: `history.id` → `history.history_id`

---

## 技術的なハイライト

### 1. 別ウィンドウの実装

HistoryPanelは`tk.Toplevel`を継承し、メインウィンドウとは独立したウィンドウとして動作します。

```python
class HistoryPanel(tk.Toplevel):
    def __init__(self, parent, on_search_callback):
        super().__init__(parent)
        self.title("検索履歴")
        self.geometry("800x500")
```

**利点**:
- メインウィンドウを隠さずに履歴を確認できる
- 複数の履歴ウィンドウを同時に開ける（実装次第）
- ウィンドウサイズやタイトルを独立して設定可能

### 2. コールバックパターン

HistoryPanelからMainWindowへの通信にコールバックを使用：

```python
# MainWindow
history_panel = HistoryPanel(
    self.root,
    on_search_callback=self._on_search_from_history
)

# HistoryPanel
def _research_selected(self):
    if self.on_search_callback:
        self.on_search_callback(history.criteria)
```

### 3. 統合テストのベストプラクティス

#### 一時ファイルの使用

```python
with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
    db_path = f.name

try:
    # テスト実行
    service = PresetService(db_path)
    # ...
finally:
    # クリーンアップ
    if os.path.exists(db_path):
        os.unlink(db_path)
```

**利点**:
- テスト間の相互干渉を防ぐ
- テスト後の自動クリーンアップ
- 並列テスト実行に対応

#### エンドツーエンドテスト

実際の使用シナリオをシミュレート：

```python
def test_search_save_export_workflow(self):
    # 1. 検索条件を作成
    criteria = SearchCriteria(...)

    # 2. プリセットとして保存
    preset = preset_service.save_preset("Pythonチュートリアル", criteria)

    # 3. 検索実行（モック）
    mock_videos = [...]

    # 4. 検索履歴に記録
    history = history_service.add_history(criteria, len(mock_videos))

    # 5. Excelにエクスポート
    exporter.export(mock_videos, excel_path)

    # 6. 検証
    assert preset is not None
    assert history.result_count == 5
    assert os.path.exists(excel_path)
```

---

## ユーザー操作フロー

### プリセットの使用

```
1. 検索条件を入力
2. 「保存」ボタンをクリック
3. プリセット名を入力（例: "初心者向けPython動画"）
4. OK → プリセットが保存される

[次回の使用時]
5. プリセットコンボボックスから「初心者向けPython動画」を選択
6. 「読込」ボタンをクリック
7. 検索条件が自動で入力される
8. 「検索」ボタンをクリック
```

### 検索履歴からの再検索

```
1. メニューバーの「表示」→「検索履歴」をクリック
2. 検索履歴ウィンドウが開く
3. 過去の検索から再実行したいものを選択
4. 「この条件で再検索」ボタンをクリック（またはダブルクリック）
5. 履歴ウィンドウが閉じ、メインウィンドウで検索が実行される
```

### Google Sheetsへのエクスポート

```
1. 検索を実行して結果を取得
2. メニューバーの「ファイル」→「Google Sheetsにエクスポート」をクリック
3. スプレッドシート名を入力（デフォルト: "YouTube動画リスト"）
4. OK → エクスポート処理開始
5. プログレスバー表示
6. 完了ダイアログが表示され、URLがクリップボードにコピーされる
7. ブラウザでURLを開いてスプレッドシートを確認
```

---

## Phase 4で作成・更新したファイル一覧

### 更新ファイル

1. `src/ui/search_panel.py` - プリセット管理UI追加
2. `src/ui/main_window.py` - メニュー追加、履歴・Sheetsエクスポート統合
3. `src/application/preset_service.py` - `order`フィールド名修正
4. `src/application/history_service.py` - `order`フィールド名修正、`history_id`/`executed_at`修正

### 新規作成ファイル

5. `src/ui/history_panel.py` - 検索履歴パネル
6. `tests/test_integration.py` - 統合テスト

### ドキュメント

7. `research/phase4-completion-report.md` - この完了報告書

---

## テスト カバレッジ

### プリセット機能

- ✅ 保存（新規・上書き）
- ✅ 読み込み
- ✅ 削除
- ✅ 一覧取得

### 検索履歴機能

- ✅ 追加
- ✅ 最近の履歴取得
- ✅ キーワード検索
- ✅ 個別削除
- ✅ 全削除

### エクスポート機能

- ✅ Excel正常エクスポート
- ✅ Excelエラーハンドリング（空リスト）
- ⚠️ Google Sheetsは手動テストのみ（認証が必要なため）

### エンドツーエンド

- ✅ 検索→プリセット保存→履歴記録→Excelエクスポート

---

## 既知の制限事項

### 1. Google Sheetsエクスポート

- **認証情報の設定が必要**: サービスアカウントJSONファイルの準備が必要
- **自動テスト未実装**: 統合テストに含まれていない（認証が複雑なため）
- **手動テスト推奨**: 実際の環境で動作確認が必要

### 2. UI

- **プリセット/履歴の同期**: 別のプロセスでプリセットを変更した場合、手動で更新が必要
- **履歴ウィンドウの自動更新**: 検索実行後も履歴ウィンドウが開いたままの場合、手動で更新ボタンを押す必要がある

### 3. データベース

- **並行アクセス**: SQLiteは複数プロセスからの同時書き込みに弱い
- **トランザクション管理**: 現在は各操作で個別にcommit（より高度なトランザクション管理は未実装）

---

## 今後の改善案

### Phase 5 以降で実装可能な機能

1. **プリセットのインポート・エクスポート**
   - JSON形式でプリセットをファイルに保存
   - 他のユーザーとプリセットを共有

2. **履歴の統計情報**
   - よく検索されるキーワードのランキング
   - 検索頻度の時系列グラフ

3. **お気に入り動画機能**
   - 検索結果から動画をブックマーク
   - お気に入りリストの管理

4. **検索条件の詳細設定**
   - 公開日範囲の指定
   - チャンネルIDでフィルタ
   - 地域・言語の指定

5. **バッチ処理**
   - 複数のプリセットを一括実行
   - 結果を1つのExcelファイルにまとめる

---

## まとめ

Phase 4では、以下を実装しました：

✅ **プリセット管理UI**: SearchPanelに統合、保存・読込・削除機能
✅ **検索履歴パネル**: 独立したウィンドウで履歴を表示・再検索
✅ **Google Sheetsエクスポート**: メニューから直接エクスポート、URL自動コピー
✅ **統合テスト**: 12テストケース、全合格
✅ **不具合修正**: データベース初期化、フィールド名統一

これらの機能により、ユーザーは：
- よく使う検索条件を保存して効率化できる
- 過去の検索を振り返り、再実行できる
- 検索結果を複数の形式で共有できる

### 次のフェーズ

**Phase 5: 最終調整・リリース準備**
- パフォーマンス最適化
- ユーザードキュメントの整備
- インストーラー作成
- 最終的な動作確認

---

**Phase 4 完了日**: 2025年11月26日
**実装者**: Claude Code
**次のフェーズ**: Phase 5（最終調整・リリース準備）
