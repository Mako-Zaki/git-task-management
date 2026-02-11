#!/usr/bin/env python3
"""
TODO.mdからGitHub Issuesを作成・同期するスクリプト
"""

import re
import subprocess
import json
from pathlib import Path
from datetime import datetime

def parse_todo_file(file_path):
    """TODO.mdファイルを解析してタスクを抽出"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tasks = []
    current_category = None
    current_status = "todo"

    # カテゴリを検出
    category_pattern = r'^## (.+)$'
    # サブセクションを検出
    subsection_pattern = r'^### (.+)$'
    # タスクを検出（未完了）
    task_pattern = r'^- \[ \] (.+)$'
    # 完了済みタスク
    completed_pattern = r'^- \[x\] (.+)$'

    for line in content.split('\n'):
        # カテゴリ検出
        cat_match = re.match(category_pattern, line.strip())
        if cat_match:
            current_category = cat_match.group(1)
            current_status = "todo"
            continue

        # サブセクション検出
        sub_match = re.match(subsection_pattern, line.strip())
        if sub_match:
            subsection = sub_match.group(1).lower()
            if '進行中' in subsection or 'progress' in subsection:
                current_status = "in_progress"
            elif '完了' in subsection or 'done' in subsection:
                current_status = "done"
            else:
                current_status = "todo"
            continue

        # 未完了タスク検出
        task_match = re.match(task_pattern, line.strip())
        if task_match and current_category:
            task_text = task_match.group(1)

            # 期限を抽出
            deadline_match = re.search(r'[（\(]期限[：:]?\s*(\d{4}-\d{2}-\d{2})[）\)]', task_text)
            deadline = deadline_match.group(1) if deadline_match else None

            # 期限情報を除いたタスク名
            task_name = re.sub(r'\s*[（\(]期限[：:]?\s*\d{4}-\d{2}-\d{2}[）\)]', '', task_text)

            tasks.append({
                'title': task_name.strip(),
                'category': current_category,
                'status': current_status,
                'deadline': deadline,
                'completed': False
            })

    return tasks

def get_existing_issues():
    """既存のGitHub Issuesを取得"""
    try:
        result = subprocess.run(
            ['gh', 'issue', 'list', '--json', 'number,title,state,labels'],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  既存Issueの取得に失敗: {e}")
        return []

def create_issue(task):
    """GitHub Issueを作成"""
    title = task['title']

    # ラベルを設定
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

    # ステータスラベル
    if task['status'] == 'in_progress':
        labels.append('進行中')
    elif task['status'] == 'todo':
        labels.append('未着手')

    # 本文を作成
    body = f"**カテゴリ:** {task['category']}\n\n"
    if task['deadline']:
        body += f"**期限:** {task['deadline']}\n\n"
    body += "---\n*このIssueはTODO.mdから自動生成されました*"

    # Issueを作成
    cmd = ['gh', 'issue', 'create', '--title', title, '--body', body]

    if labels:
        cmd.extend(['--label', ','.join(labels)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Issue作成: {title}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Issue作成失敗: {title}")
        print(f"   エラー: {e.stderr}")
        return None

def main():
    # TODO.mdのパスを取得
    script_dir = Path(__file__).parent
    repo_dir = script_dir.parent
    todo_file = repo_dir / 'TODO.md'

    if not todo_file.exists():
        print(f"❌ TODO.mdが見つかりません: {todo_file}")
        return

    print("🔄 GitHub Issuesへの同期")
    print("=" * 60)

    # TODO.mdを解析
    tasks = parse_todo_file(todo_file)

    if not tasks:
        print("タスクが見つかりませんでした。")
        return

    print(f"📝 TODO.mdから {len(tasks)} 個のタスクを抽出しました。\n")

    # 既存のIssuesを取得
    existing_issues = get_existing_issues()
    existing_titles = {issue['title'] for issue in existing_issues}

    # 新しいタスクのみIssueを作成
    new_count = 0
    skip_count = 0

    for task in tasks:
        if task['title'] in existing_titles:
            print(f"⏭️  スキップ（既存）: {task['title']}")
            skip_count += 1
        else:
            create_issue(task)
            new_count += 1

    print("\n" + "=" * 60)
    print(f"✨ 完了: {new_count}個の新しいIssueを作成しました")
    print(f"⏭️  スキップ: {skip_count}個（既に存在）")

if __name__ == '__main__':
    main()
