#!/usr/bin/env python3
"""
期限が近いタスクをチェックするスクリプト
"""

import re
import calendar
from datetime import datetime, timedelta
from pathlib import Path


def parse_date_expr(expr, base_year=None):
    """日付表現を解析してdatetimeを返す。解析できなければNone。

    対応フォーマット:
      - YYYY-MM-DD       (例: 2026-03-01)
      - M/D              (例: 2/17, 3/5)
      - M/D・D            (例: 2/14・15 → 2/15)
      - N月中             (例: 3月中 → 3/31)
      - N月末             (例: 2月末 → 2/28)
      - N月以降           (例: 4月以降 → 4/1)
    """
    if base_year is None:
        base_year = datetime.now().year

    expr = expr.strip()

    # YYYY-MM-DD
    m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', expr)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # M/D・D (日付範囲 → 後ろの日を採用)
    m = re.match(r'^(\d{1,2})/(\d{1,2})[・\-](\d{1,2})$', expr)
    if m:
        month, _, day2 = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return datetime(base_year, month, day2)

    # M/D
    m = re.match(r'^(\d{1,2})/(\d{1,2})$', expr)
    if m:
        return datetime(base_year, int(m.group(1)), int(m.group(2)))

    # N月中 / N月末 → 月末日
    m = re.match(r'^(\d{1,2})月[中末]$', expr)
    if m:
        month = int(m.group(1))
        last_day = calendar.monthrange(base_year, month)[1]
        return datetime(base_year, month, last_day)

    # N月以降 → 月初日
    m = re.match(r'^(\d{1,2})月以降$', expr)
    if m:
        return datetime(base_year, int(m.group(1)), 1)

    return None


def parse_todo_file(file_path):
    """TODO.mdファイルを解析してタスクを抽出"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    base_year = datetime.now().year

    # 括弧内の日付表現を抽出（未完了 [ ] と進行中 [-] が対象）
    # キーワード（締切/期限/予定）あり or なし の両方に対応
    pattern = r'- \[[ \-]\] (.+?)[（\(]((?:締切|期限|予定)[：:]\s*)?(.+?)[）\)]'

    tasks = []
    for line in content.split('\n'):
        # HTMLコメント内の例を無視
        if '<!--' in line:
            continue
        m = re.search(pattern, line)
        if not m:
            continue

        task_name = m.group(1).strip()
        date_raw = m.group(3).strip()

        # 日付部分の後ろにある余計なテキスト（昼、正午、企業オリジナル等）を除去
        date_clean = re.split(r'\s+', date_raw)[0]

        deadline = parse_date_expr(date_clean, base_year)
        if deadline:
            tasks.append({
                'name': task_name,
                'deadline': deadline,
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
