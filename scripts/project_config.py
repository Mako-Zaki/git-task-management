"""
GitHub Projects V2 の設定と共通ユーティリティ
"""

import subprocess
import json

# プロジェクト設定
PROJECT_NUMBER = 1
STATUS_FIELD_ID = "PVTSSF_lAHOBuwUxs4BO6Rczg9eVhk"
STATUS_OPTIONS = {
    "Todo":        "f75ad846",
    "In Progress": "47fc9ee4",
    "Done":        "98236657",
}


def get_project_owner():
    """gh認証済みユーザー名を取得"""
    try:
        result = subprocess.run(
            ['gh', 'api', 'user', '--jq', '.login'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_project_items():
    """Project内の全アイテムを取得"""
    owner = get_project_owner()
    if not owner:
        return []
    try:
        result = subprocess.run(
            ['gh', 'project', 'item-list', str(PROJECT_NUMBER),
             '--owner', owner, '--format', 'json'],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        return data.get('items', [])
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Projectアイテム取得失敗: {e.stderr}")
        return []


def get_project_id():
    """Project のノードIDを取得"""
    owner = get_project_owner()
    if not owner:
        return None
    try:
        result = subprocess.run(
            ['gh', 'project', 'list', '--owner', owner, '--format', 'json'],
            capture_output=True, text=True, check=True
        )
        projects = json.loads(result.stdout).get('projects', [])
        for p in projects:
            if p.get('number') == PROJECT_NUMBER:
                return p.get('id')
    except subprocess.CalledProcessError:
        pass
    return None


def update_project_item_status(item_id, status_name):
    """Projectアイテムのステータスを変更"""
    project_id = get_project_id()
    if not project_id:
        return False

    option_id = STATUS_OPTIONS.get(status_name)
    if not option_id:
        return False

    try:
        subprocess.run(
            ['gh', 'project', 'item-edit',
             '--project-id', project_id,
             '--id', item_id,
             '--field-id', STATUS_FIELD_ID,
             '--single-select-option-id', option_id],
            capture_output=True, text=True, check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  ステータス更新失敗: {e.stderr}")
        return False


def derive_project_status(task):
    """タスクのチェック状態からProjectステータスを決定

    チェックボックスの記法:
      - [ ]  未着手 (Todo)
      - [-]  進行中 (In Progress)
      - [x]  完了 (Done)

    親タスクが [-] なら強制的に In Progress。
    サブタスクがある場合は完了数から自動判定。
    """
    # 親が完了
    if task.get('completed'):
        return "Done"

    # 親が [-] で明示的に進行中
    if task.get('in_progress'):
        return "In Progress"

    subtasks = task.get('subtasks', [])
    if not subtasks:
        return "Todo"

    done_count = sum(1 for s in subtasks if s['completed'])
    if done_count == len(subtasks):
        return "Done"
    elif done_count > 0:
        return "In Progress"
    else:
        return "Todo"


def git_commit_todo(repo_dir, message):
    """TODO.mdの変更をgit commit"""
    todo_path = str(repo_dir / 'TODO.md')

    # 変更があるか確認
    result = subprocess.run(
        ['git', 'diff', '--name-only', todo_path],
        capture_output=True, text=True, cwd=str(repo_dir)
    )
    if not result.stdout.strip():
        return False

    subprocess.run(
        ['git', 'add', todo_path],
        capture_output=True, text=True, cwd=str(repo_dir)
    )
    subprocess.run(
        ['git', 'commit', '-m', message],
        capture_output=True, text=True, cwd=str(repo_dir)
    )
    print(f"\n📦 git commit: {message}")
    return True
