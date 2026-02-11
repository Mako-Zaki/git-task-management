# Gitタスク管理チートシート

## 基本的なワークフロー

### 1. タスクを追加する
TODO.mdファイルを編集して、新しいタスクを追加。

### 2. 変更をコミットする
```bash
git add TODO.md
git commit -m "タスク追加: ○○を追加"
```

### 3. タスクを完了する
TODO.mdでタスクを完了セクションに移動し、コミット。
```bash
git add TODO.md
git commit -m "タスク完了: ○○を完了"
```

## よく使うGitコマンド

### 履歴を確認
```bash
# 簡潔な履歴表示
git log --oneline

# 特定ファイルの履歴
git log --oneline TODO.md

# 詳細な変更内容
git show <コミットID>
```

### ブランチ管理
```bash
# 新しいブランチを作成して切り替え
git checkout -b feature/機能名

# ブランチ一覧
git branch -v

# ブランチの切り替え
git checkout main
```

### 変更の確認
```bash
# 変更されたファイルを確認
git status

# 変更内容を確認
git diff TODO.md
```

### ブランチのマージ
```bash
# mainブランチに切り替え
git checkout main

# 機能ブランチをマージ
git merge feature/機能名
```

## 応用的な使い方

### 機能ごとにタスクを管理
1. 新しい機能のためのブランチを作成
2. そのブランチでTODO.mdに機能固有のタスクを追加
3. タスクを進めながらコミット
4. 完了したらmainにマージ

### タスクの検索
```bash
# 過去のタスクを検索
git log --all --grep="ログイン"

# 特定の単語が含まれる変更を検索
git log -p --all -S "ログイン機能"
```

### タスクの統計
```bash
# コミット数を確認
git log --oneline | wc -l

# 期間を指定してコミットを確認
git log --since="1 week ago" --oneline
```
