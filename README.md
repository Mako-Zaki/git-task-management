# Gitタスク管理システム

このリポジトリは、Gitを使ったシンプルなタスク管理の例です。

## 基本的な使い方

### 1. タスクを追加する

`TODO.md`ファイルの「未着手 (TODO)」セクションに新しいタスクを追加します。

```markdown
- [ ] 新しいタスク
```

### 2. タスクを開始する

タスクを開始するときは、「未着手」から「進行中」に移動します。

### 3. タスクを完了する

完了したら、チェックボックスをチェックし、「完了」セクションに移動します。

```markdown
- [x] 完了したタスク
```

### 4. 変更をコミットする

タスクの状態を変更したら、Gitでコミットします。

```bash
git add TODO.md
git commit -m "タスクを更新: ○○を完了"
```

## GitHub上での管理

このリポジトリはGitHub上で公開されています: https://github.com/Mako-Zaki/git-task-management

### GitHub経由での変更をプッシュする

```bash
# 変更をコミット
git add TODO.md
git commit -m "タスク更新: ○○を完了"

# GitHubにプッシュ
git push origin main
```

### 他の端末から最新の変更を取得する

```bash
# 最新の変更を取得
git pull origin main
```

### 新しい機能ブランチをGitHubにプッシュ

```bash
# 新しいブランチを作成
git checkout -b feature/新機能

# タスクを追加してコミット
git add TODO.md
git commit -m "タスク追加: 新機能のタスクを追加"

# GitHubにプッシュ
git push -u origin feature/新機能
```

## メリット

- タスクの履歴がGitで管理される
- いつ、どのタスクが完了したかが分かる
- ブランチを使って、機能ごとにタスクを管理できる
- チームで共有しやすい
- GitHub上でリモート管理できる
- 複数の端末から同じタスクリストにアクセスできる
