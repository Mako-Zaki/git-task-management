#!/usr/bin/env python3
"""
GitHub Issues + Project → TODO.md への同期（pull）

- GitHub Issue本文のチェックリスト状態をtodo.mdに反映
- Projectステータスが In Progress → todo.mdで [-] に変更
- クローズ済みIssue → todo.mdで [x] に変更
- 変更後に git commit + push
"""

import re
import subprocess
import json
from pathlib import Path
from project_config import get_project_items, git_commit_todo


def get_issues():
    """GitHub Issuesを全件取得（open + closed）"""
    try:
        result = subprocess.run(
            ['gh', 'issue', 'list', '--state', 'all',
             '--json', 'number,title,body,state', '--limit', '200'],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Issueの取得に失敗: {e}")
        return []


def parse_issue_checkboxes(body):
    """Issue本文からチェックリストを解析"""
    subtasks = {}
    if not body:
        return subtasks

    for line in body.split('\n'):
        match = re.match(r'^- \[([ x])\] (.+)$', line.strip())
        if match:
            completed = match.group(1) == 'x'
            text = match.group(2).strip()
            subtasks[text] = completed

    return subtasks


def update_todo_file(todo_path, issues, project_status_map):
    """todo.mdをGitHub Issue + Projectの状態で更新"""
    with open(todo_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    issue_map = {}
    for issue in issues:
        issue_map[issue['title']] = {
            'state': issue['state'],
            'subtasks': parse_issue_checkboxes(issue.get('body', '')),
        }

    new_lines = []
    current_parent_title = None
    current_parent_issue = None
    changes = []

    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())

        # トップレベルのタスク行 ( [ ], [-], [x] )
        top_match = re.match(r'^- \[([ \-x])\] (.+)$', stripped)
        if top_match and indent == 0:
            old_mark = top_match.group(1)
            title = top_match.group(2).strip()
            current_parent_title = title
            current_parent_issue = issue_map.get(title)

            # 新しいマークを決定
            new_mark = old_mark
            if current_parent_issue:
                is_closed = current_parent_issue['state'] == 'CLOSED'
                if is_closed:
                    new_mark = 'x'
                else:
                    # Projectステータスを反映
                    proj_status = project_status_map.get(title, '')
                    if proj_status == 'In Progress':
                        new_mark = '-'
                    elif proj_status == 'Todo' and old_mark == '-':
                        # Projectが Todo に戻された場合
                        new_mark = ' '
                    # それ以外は現状維持

            if old_mark != new_mark:
                line = line.replace(f'- [{old_mark}]', f'- [{new_mark}]', 1)
                status_labels = {' ': 'Todo', '-': 'In Progress', 'x': 'Done'}
                changes.append(f"  {title}: {status_labels.get(old_mark, '?')} → {status_labels.get(new_mark, '?')}")

            new_lines.append(line)
            continue

        # サブタスク行
        sub_match = re.match(r'^- \[([ \-x])\] (.+)$', stripped)
        if sub_match and indent >= 2 and current_parent_issue:
            old_mark = sub_match.group(1)
            text = sub_match.group(2).strip()
            issue_subtasks = current_parent_issue['subtasks']

            if text in issue_subtasks:
                is_done = issue_subtasks[text]
                new_mark = 'x' if is_done else ' '

                if old_mark != new_mark:
                    line = line.replace(f'- [{old_mark}]', f'- [{new_mark}]', 1)
                    state_str = "done" if is_done else "todo"
                    changes.append(f"  [{state_str}] {text}（{current_parent_title}）")

            new_lines.append(line)
            continue

        if re.match(r'^##', stripped):
            current_parent_title = None
            current_parent_issue = None
        elif re.match(r'^###', stripped):
            current_parent_title = None
            current_parent_issue = None

        new_lines.append(line)

    with open(todo_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    return changes


def show_project_dashboard(project_items):
    """ターミナルにProjectダッシュボードを表示"""
    todo = []
    in_progress = []
    done = []

    for item in project_items:
        status = item.get('status', 'Todo')
        title = item.get('title', '?')
        if status == 'Done':
            done.append(title)
        elif status == 'In Progress':
            in_progress.append(title)
        else:
            todo.append(title)

    print("\n📋 Project ダッシュボード")
    print("=" * 60)

    print(f"\n🔵 Todo ({len(todo)})")
    for t in todo:
        print(f"  - {t}")

    print(f"\n🟡 In Progress ({len(in_progress)})")
    for t in in_progress:
        print(f"  - {t}")

    print(f"\n🟢 Done ({len(done)})")
    for t in done:
        print(f"  - {t}")

    if not done and not in_progress and not todo:
        print("  (アイテムなし)")

    print()


def main():
    script_dir = Path(__file__).parent
    repo_dir = script_dir.parent
    todo_file = repo_dir / 'TODO.md'

    if not todo_file.exists():
        print(f"❌ TODO.mdが見つかりません: {todo_file}")
        return

    print("⬇️  pull: GitHub Issues + Project → TODO.md + git")
    print("=" * 60)

    issues = get_issues()
    if not issues:
        print("Issueが見つかりませんでした。")
        return

    open_count = sum(1 for i in issues if i['state'] == 'OPEN')
    closed_count = sum(1 for i in issues if i['state'] == 'CLOSED')
    print(f"📥 Issues: {len(issues)} 件（open: {open_count}, closed: {closed_count}）")

    # Projectステータスを取得
    project_items = get_project_items()
    project_status_map = {item['title']: item.get('status', 'Todo') for item in project_items}

    changes = update_todo_file(todo_file, issues, project_status_map)

    if changes:
        print("\n変更内容:")
        for c in changes:
            print(c)
        print(f"\n✨ {len(changes)} 箇所を更新")

        # git commit + push
        git_commit_todo(repo_dir, "タスク同期: pull from GitHub")
        subprocess.run(
            ['git', 'push'],
            capture_output=True, text=True, cwd=str(repo_dir)
        )
    else:
        print("\n✅ TODO.mdは最新（変更なし）")

    show_project_dashboard(project_items)


if __name__ == '__main__':
    main()
