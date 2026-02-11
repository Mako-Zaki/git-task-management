#!/usr/bin/env python3
"""
TODO.md → GitHub Issues + Project への同期（push）

- 新規タスク → Issue作成
- 既存タスク → チェックリストの状態を更新
- [-] マーカーで進行中を明示可能
- Projectステータスをサブタスク進捗から自動設定
- 全サブタスク完了 → Done + Issueクローズ
- 変更後に git commit + push
"""

import re
import subprocess
import json
from pathlib import Path
from project_config import (
    get_project_items, update_project_item_status,
    derive_project_status, git_commit_todo
)


def parse_todo_file(file_path):
    """TODO.mdファイルを解析（[ ], [-], [x] 対応）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tasks = []
    current_category = None
    current_subsection = None
    current_status = "todo"
    current_parent = None

    for line in content.split('\n'):
        stripped = line.strip()

        cat_match = re.match(r'^## (.+)$', stripped)
        if cat_match:
            current_category = cat_match.group(1)
            current_subsection = None
            current_status = "todo"
            current_parent = None
            continue

        sub_match = re.match(r'^### (.+)$', stripped)
        if sub_match:
            subsection = sub_match.group(1)
            current_subsection = subsection
            if '進行中' in subsection or 'progress' in subsection.lower():
                current_status = "in_progress"
            elif '完了' in subsection or 'done' in subsection.lower():
                current_status = "done"
            else:
                current_status = "todo"
            current_parent = None
            continue

        indent = len(line) - len(line.lstrip())

        # 3種類のチェックボックスを検出: [ ], [-], [x]
        checkbox_match = re.match(r'^- \[([ \-x])\] (.+)$', stripped)
        if not checkbox_match or not current_category:
            # ヘッダー等でparentリセットしない（空行は無視）
            continue

        mark = checkbox_match.group(1)
        task_text = checkbox_match.group(2).strip()

        if indent == 0:
            # トップレベル = 親タスク（Issueになる）
            task = {
                'title': task_text,
                'category': current_category,
                'subsection': current_subsection,
                'status': current_status,
                'completed': mark == 'x',
                'in_progress': mark == '-',
                'subtasks': [],
            }
            tasks.append(task)
            current_parent = task
        elif indent >= 2 and current_parent is not None:
            # サブタスク
            current_parent['subtasks'].append({
                'text': task_text,
                'completed': mark == 'x',
                'in_progress': mark == '-',
            })

    return tasks


def get_existing_issues():
    try:
        result = subprocess.run(
            ['gh', 'issue', 'list', '--state', 'open',
             '--json', 'number,title,body', '--limit', '200'],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  既存Issueの取得に失敗: {e}")
        return []


def build_labels(task):
    labels = []
    category = task['category']

    if '🎓' in category or '研究' in category:
        labels.append('研究')
    elif '💼' in category or '就活' in category or '就職' in category:
        labels.append('就活')
    elif '📅' in category or '日常' in category:
        labels.append('日常')
    elif '💡' in category or 'プロジェクト' in category:
        labels.append('プロジェクト')

    if '🔥' in category or '緊急' in category:
        labels.append('緊急')

    subsection = task.get('subsection', '') or ''
    if 'コンサル' in subsection or 'シンクタンク' in subsection:
        labels.append('コンサル')
    elif '商社' in subsection:
        labels.append('商社')
    elif '通信' in subsection or 'IT' in subsection:
        labels.append('IT')
    elif '横断' in subsection:
        labels.append('横断タスク')

    if task['status'] == 'in_progress':
        labels.append('進行中')
    elif task['status'] == 'todo':
        labels.append('未着手')

    return labels


def build_issue_body(task):
    lines = []
    lines.append(f"**カテゴリ:** {task['category']}")
    if task.get('subsection'):
        lines.append(f"**セクション:** {task['subsection']}")
    lines.append("")

    if task['subtasks']:
        lines.append("## タスク一覧")
        lines.append("")
        for sub in task['subtasks']:
            if sub['completed']:
                lines.append(f"- [x] {sub['text']}")
            else:
                lines.append(f"- [ ] {sub['text']}")
        lines.append("")

    lines.append("---")
    lines.append("*このIssueはTODO.mdから自動生成されました*")
    return "\n".join(lines)


def create_issue(task):
    title = task['title']
    body = build_issue_body(task)
    labels = build_labels(task)

    cmd = ['gh', 'issue', 'create', '--title', title, '--body', body]
    if labels:
        cmd.extend(['--label', ','.join(labels)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        sub_count = len(task['subtasks'])
        suffix = f"（サブタスク {sub_count}件）" if sub_count > 0 else ""
        print(f"  ✅ 新規作成: {title}{suffix}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 作成失敗: {title} - {e.stderr}")
        return None


def update_issue(issue_number, task):
    new_body = build_issue_body(task)
    try:
        subprocess.run(
            ['gh', 'issue', 'edit', str(issue_number), '--body', new_body],
            capture_output=True, text=True, check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ body更新失敗: #{issue_number} - {e.stderr}")
        return False


def close_issue(issue_number, title):
    try:
        subprocess.run(
            ['gh', 'issue', 'close', str(issue_number)],
            capture_output=True, text=True, check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ クローズ失敗: #{issue_number} - {e.stderr}")
        return False


def main():
    script_dir = Path(__file__).parent
    repo_dir = script_dir.parent
    todo_file = repo_dir / 'TODO.md'

    if not todo_file.exists():
        print(f"❌ TODO.mdが見つかりません: {todo_file}")
        return

    print("⬆️  push: TODO.md → GitHub Issues + Project + git")
    print("=" * 60)

    tasks = parse_todo_file(todo_file)
    if not tasks:
        print("タスクが見つかりませんでした。")
        return

    total_subtasks = sum(len(t['subtasks']) for t in tasks)
    print(f"📝 {len(tasks)} 件（サブタスク計 {total_subtasks} 件）\n")

    existing_issues = get_existing_issues()
    existing_map = {issue['title']: issue for issue in existing_issues}

    project_items = get_project_items()
    project_map = {item['title']: item for item in project_items}

    new_count = 0
    update_count = 0
    close_count = 0

    for task in tasks:
        title = task['title']
        target_status = derive_project_status(task)

        if title in existing_map:
            issue = existing_map[title]
            issue_number = issue['number']

            all_done = (
                task['completed']
                or (task['subtasks'] and all(s['completed'] for s in task['subtasks']))
            )

            if all_done:
                update_issue(issue_number, task)
                close_issue(issue_number, title)
                if title in project_map:
                    update_project_item_status(project_map[title]['id'], "Done")
                print(f"  🎉 #{issue_number} {title} → Done")
                close_count += 1
            else:
                update_issue(issue_number, task)
                if title in project_map:
                    current = project_map[title].get('status', '')
                    if current != target_status:
                        update_project_item_status(project_map[title]['id'], target_status)
                        print(f"  📊 #{issue_number} {title}: {current} → {target_status}")
                    else:
                        print(f"  🔄 #{issue_number} {title} [{target_status}]")
                else:
                    print(f"  🔄 #{issue_number} {title}")
                update_count += 1
        else:
            create_issue(task)
            new_count += 1

    # git commit + push
    git_commit_todo(repo_dir, "タスク同期: push to GitHub")
    subprocess.run(
        ['git', 'push'],
        capture_output=True, text=True, cwd=str(repo_dir)
    )

    print("\n" + "=" * 60)
    print(f"✨ 新規: {new_count}件 | 🔄 更新: {update_count}件 | 🎉 完了: {close_count}件")


if __name__ == '__main__':
    main()
