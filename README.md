# Gitタスク管理システム

研究、就職活動、日常タスクなど、あらゆるタスクをGit + GitHub Issues + Projectsで一元管理するシステムです。

## 全体構成

```
TODO.md（ローカル） ⇄ GitHub Issues + Projects（リモート）
         ↕                      ↕
     git commit             チェックリスト / カンバン
```

**todo-push**: TODO.md → Issues / Projects / git に反映
**todo-pull**: Issues / Projects → TODO.md / git に反映

## クイックスタート

```bash
# エイリアスを反映
source ~/.zshrc

# ローカルの変更をGitHubに同期
todo-push

# GitHubの変更をローカルに同期
todo-pull

# 期限チェック
todo-deadline

# TODO.mdを開く
todo

# Projectボードをブラウザで開く
todo-board
```

## TODO.mdの書き方

### チェックボックス記法

```markdown
- [ ] 未着手 (Todo)
- [-] 進行中 (In Progress)
- [x] 完了 (Done)
```

| 記法 | 状態 | Project上 |
|------|------|-----------|
| `- [ ]` | 未着手 | Todo |
| `- [-]` | 進行中 | In Progress |
| `- [x]` | 完了 | Done（Issue自動クローズ） |

### 企業タスクの構造

企業が**親タスク（= 1 Issue）**、個別作業が**サブタスク（= Issue内チェックリスト）**になります。

```markdown
- [ ] **三菱商事**（商社）
  - [ ] ES提出（締切: 2/17）
  - [x] Webテスト（締切: 2/18）
  - [ ] AI面接（締切: 2/20）
```

サブタスクの完了状況でProjectステータスが自動判定されます：
- 全部 `[ ]` → **Todo**
- 一部 `[x]` → **In Progress**
- 全部 `[x]` → **Done**（Issueも自動クローズ）

### サブタスクなしのタスク

横断タスクなどサブタスクがないものは `[-]` で明示的に進行中にできます。

```markdown
- [-] Webテスト対策（玉手箱）: Redgelines DBC, 日本総研, ISE
```

## コマンド一覧

| エイリアス | コマンド | 動作 |
|-----------|---------|------|
| `todo-push` | `python3 scripts/sync_to_issues.py` | TODO.md → Issue + Project更新 → git commit & push |
| `todo-pull` | `python3 scripts/sync_from_issues.py` | Issue + Project → TODO.md反映 → git commit & push |
| `todo-deadline` | `python3 scripts/check_deadlines.py` | 期限が近いタスクを通知 |
| `todo` | - | git pull + TODO.mdを開く |
| `todo-board` | - | Projectボードをブラウザで開く |

## 日常のワークフロー

### ローカルで作業する場合

```bash
# 1. TODO.mdを編集（タスク追加、チェック付け、[-]に変更など）
vi TODO.md

# 2. GitHubに同期（Issue更新 + Project反映 + git commit & push）
todo-push
```

### GitHubで作業した場合

GitHub上でIssueのチェックを付けたり、Projectボードのカードを動かした場合：

```bash
# ローカルに反映（TODO.md更新 + git commit & push）
todo-pull
```

### 朝のルーティン

```bash
todo-pull       # GitHubの最新状態を取得
todo-deadline   # 今週の締切を確認
```

## カテゴリ

TODO.mdは以下のカテゴリで構成されています：

| カテゴリ | 説明 |
|---------|------|
| 🔥 緊急・重要 | 最優先タスク |
| 🎓 研究関連 | 論文、実験、文献調査 |
| 💼 就職活動 | ES、面接、説明会（企業別に管理） |
| 📅 日常・予定 | 買い物、手続き、イベント |
| 💡 個人プロジェクト | 開発、学習、趣味 |
| 📝 メモ・アイデア | まだタスク化していないメモ |

## 就職活動セクションの構成

業界ごとにサブセクション分けし、企業単位で管理します。

```
💼 就職活動
├── コンサル（シンクタンク）  → ラベル: コンサル
│   ├── Redgelines
│   ├── NRI
│   └── ...
├── 商社                     → ラベル: 商社
│   ├── 三菱商事
│   └── ...
├── 通信・IT                 → ラベル: IT
│   ├── SKY
│   └── ...
└── 横断タスク               → ラベル: 横断タスク
    ├── Webテスト対策
    └── 成績証明書の準備
```

## GitHub Issueのラベル

同期時に自動付与されます：

| ラベル | 説明 |
|--------|------|
| 就活 | 就職活動タスク |
| コンサル | コンサル・シンクタンク |
| 商社 | 商社 |
| IT | 通信・IT |
| 横断タスク | 複数企業にまたがるタスク |
| 未着手 / 進行中 | ステータス |
| 緊急 | 最優先 |

## ファイル構成

```
git-task-management/
├── TODO.md              # タスク本体（ローカルの真実）
├── README.md            # このファイル
├── scripts/
│   ├── sync_to_issues.py    # push: TODO.md → GitHub
│   ├── sync_from_issues.py  # pull: GitHub → TODO.md
│   ├── check_deadlines.py   # 期限チェック
│   └── project_config.py    # Project設定・共通関数
├── GUIDE.md
├── CHEATSHEET.md
└── PROJECT_SETUP.md
```

## スマホでの確認

- **GitHub公式アプリ**: Issues / Projectsの確認・更新
- **Working Copy（iOS）**: TODO.mdの直接編集 + commit & push
- ブラウザ: Projectカンバンボードで一覧確認
