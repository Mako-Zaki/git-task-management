#!/usr/bin/env python3
"""
期限が近いタスクをチェックするスクリプト
"""

import re
from datetime import datetime, timedelta
from pathlib import Path

def parse_todo_file(file_path):
    """TODO.mdファイルを解析してタスクを抽出"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 期限付きタスクを抽出（未完了のみ）
    # 全角括弧（）と半角括弧()の両方に対応
    pattern = r'- \[ \] (.+?)(?:[（\(]期限[：:]?\s*(\d{4}-\d{2}-\d{2})[）\)])'
    matches = re.findall(pattern, content)

    tasks = []
    for task_name, deadline in matches:
        tasks.append({
            'name': task_name.strip(),
            'deadline': datetime.strptime(deadline, '%Y-%m-%d')
        })

    return tasks

def check_deadlines(tasks, days_threshold=7):
    """期限が近いタスクをチェック"""
    now = datetime.now()
    urgent_tasks = []

    for task in tasks:
        days_until = (task['deadline'] - now).days

        if days_until < 0:
            status = f"⚠️  期限超過 ({abs(days_until)}日前)"
            urgent_tasks.append((task, status, days_until))
        elif days_until == 0:
            status = "🔥 今日が期限"
            urgent_tasks.append((task, status, days_until))
        elif days_until <= days_threshold:
            status = f"⏰ あと{days_until}日"
            urgent_tasks.append((task, status, days_until))

    return sorted(urgent_tasks, key=lambda x: x[2])

def main():
    # TODO.mdのパスを取得
    script_dir = Path(__file__).parent
    repo_dir = script_dir.parent
    todo_file = repo_dir / 'TODO.md'

    if not todo_file.exists():
        print(f"❌ TODO.mdが見つかりません: {todo_file}")
        return

    print("📅 期限チェック")
    print("=" * 60)

    tasks = parse_todo_file(todo_file)

    if not tasks:
        print("期限付きのタスクが見つかりませんでした。")
        return

    urgent = check_deadlines(tasks, days_threshold=7)

    if not urgent:
        print("✅ 今後7日以内に期限が迫っているタスクはありません。")
        return

    print(f"\n⚡ 期限が近いタスク ({len(urgent)}件):\n")

    for task, status, _ in urgent:
        deadline_str = task['deadline'].strftime('%Y-%m-%d (%a)')
        print(f"{status}")
        print(f"  📝 {task['name']}")
        print(f"  📆 期限: {deadline_str}")
        print()

if __name__ == '__main__':
    main()
