# GitHub Projectsの設定方法

## 1. GitHub Projectsの作成

### ステップ1: Projectを作成

1. https://github.com/Mako-Zaki/git-task-management にアクセス
2. 上部メニューの **Projects** タブをクリック
3. **New project** ボタンをクリック
4. テンプレートから **Board** を選択
5. プロジェクト名を入力: `タスク管理ボード`
6. **Create project** をクリック

### ステップ2: カラム（ステータス）の設定

デフォルトで以下のカラムが作成されます：
- Todo（未着手）
- In Progress（進行中）
- Done（完了）

必要に応じてカラムを追加・編集できます。

### ステップ3: Issuesをプロジェクトに追加

1. プロジェクトボードで **Add item** をクリック
2. 既存のIssueを検索して追加
3. ドラッグ&ドロップでステータスを変更

### ステップ4: 自動化の設定（オプション）

1. プロジェクトの右上の **...** メニューをクリック
2. **Workflows** を選択
3. 以下のワークフローを有効化：
   - **Item added to project**: 新しいIssueを自動的に"Todo"に
   - **Item closed**: Issueがクローズされたら自動的に"Done"に移動

## 2. スクリプトの使い方

### 期限チェック

毎日実行して期限が近いタスクを確認：

```bash
cd ~/git-task-management
python3 scripts/check_deadlines.py
```

### TODO.mdからIssueを作成

TODO.mdにタスクを追加したら、以下のコマンドで一括でIssueを作成：

```bash
python3 scripts/sync_to_issues.py
```

**注意**: 既存のIssueは自動でスキップされます。

## 3. 日常の使い方

### パターン1: TODO.md → Issue → Projectで管理

```bash
# 1. TODO.mdにタスクを追加
vi TODO.md

# 2. Issueを作成
python3 scripts/sync_to_issues.py

# 3. GitHubのProjectボードで確認
# ブラウザで https://github.com/Mako-Zaki/git-task-management/projects を開く

# 4. TODO.mdの変更をコミット
git add TODO.md
git commit -m "タスク追加"
git push origin main
```

### パターン2: 期限チェック

```bash
# 朝、期限が近いタスクを確認
python3 scripts/check_deadlines.py
```

## 4. エイリアスの設定（推奨）

`.zshrc`または`.bashrc`に追加：

```bash
# タスク管理関連のエイリアス
alias todo="cd ~/git-task-management && git pull && open TODO.md"
alias check-deadline="cd ~/git-task-management && python3 scripts/check_deadlines.py"
alias sync-issues="cd ~/git-task-management && python3 scripts/sync_to_issues.py"
alias todo-project="open https://github.com/Mako-Zaki/git-task-management/projects"
```

使い方：

```bash
todo              # TODO.mdを開く
check-deadline    # 期限チェック
sync-issues       # Issueに同期
todo-project      # Projectボードを開く
```

## 5. スマホでの確認

### GitHub公式アプリ

1. App StoreまたはGoogle PlayからGitHubアプリをインストール
2. リポジトリを開く
3. **Projects** タブでカンバンボードを確認
4. **Issues** タブで個別タスクを確認

### Working Copy（iOS）

1. TODO.mdを直接編集できる
2. 変更をコミット&プッシュ

## 6. ワークフロー例

### 朝のルーティン

```bash
cd ~/git-task-management
git pull origin main
check-deadline                # 期限チェック
todo                          # TODO.mdを開いて今日やることを確認
```

### タスク追加時

```bash
# TODO.mdにタスクを追加
vi TODO.md

# Issueを作成
sync-issues

# GitHubにプッシュ
git add TODO.md
git commit -m "タスク追加: ○○"
git push origin main

# Projectボードで確認（ブラウザ）
todo-project
```

### タスク完了時

1. TODO.mdで完了セクションに移動
2. GitHub Projectボードで"Done"に移動
3. Issueをクローズ
4. TODO.mdの変更をコミット&プッシュ

## 7. GitHub Projectsの利点

- **視覚的な管理**: カンバンボードで一目で状態を把握
- **フィルタリング**: ラベルでフィルタ（研究、就活など）
- **期限表示**: 期限が近いタスクがハイライト
- **進捗追跡**: 完了率を自動計算
- **スマホ対応**: どこからでも確認・更新可能
- **チーム共有**: 将来的にチームメンバーと共有可能

## 8. Tips

### カスタムビュー

GitHub Projectsでは複数のビューを作成できます：

1. **期限順ビュー**: 期限でソート
2. **カテゴリ別ビュー**: 研究/就活/日常でグループ化
3. **優先度ビュー**: 緊急タスクのみ表示

### ラベルの活用

自動で付与されるラベル：
- 🔥 **緊急**: 最優先タスク
- 🎓 **研究**: 研究関連
- 💼 **就活**: 就職活動
- 📅 **日常**: 日常タスク
- 💡 **プロジェクト**: 個人プロジェクト

### GitHub Actions（将来の拡張）

将来的にGitHub Actionsを使って自動化できること：
- 毎朝期限チェックを実行してSlack通知
- TODO.mdが更新されたら自動でIssue作成
- 期限超過タスクに自動でラベル追加
