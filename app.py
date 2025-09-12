import argparse
import sqlite3
from pathlib import Path
import datetime
import shutil
from ics import Calendar, Event

DB_PATH = Path('todo.db')
STORAGE_DIR = Path('storage')


def init_db():
    """Initialize required database tables."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS tasks(\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            description TEXT,\n            expires DATE\n        )')
        c.execute('CREATE TABLE IF NOT EXISTS notes(\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            content TEXT\n        )')
        c.execute('CREATE TABLE IF NOT EXISTS events(\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            name TEXT,\n            time TEXT\n        )')
        c.execute('CREATE TABLE IF NOT EXISTS documents(\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            label TEXT,\n            path TEXT,\n            storage TEXT\n        )')
        conn.commit()


def add_task(description: str, expires: str):
    """Add a task with expiration date (YYYY-MM-DD)."""
    date = datetime.datetime.fromisoformat(expires).date()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO tasks(description, expires) VALUES (?, ?)', (description, str(date)))
        conn.commit()


def list_tasks():
    """List tasks with their expiration date."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for row in c.execute('SELECT id, description, expires FROM tasks ORDER BY expires'):
            task_id, desc, exp = row
            status = 'EXPIRED' if datetime.date.today() > datetime.date.fromisoformat(exp) else ''
            print(f"{task_id}: {desc} (due {exp}) {status}")


def add_note(content: str):
    """Store a note in the clipboard section."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO notes(content) VALUES (?)', (content,))
        conn.commit()


def list_notes():
    """List stored notes."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for row in c.execute('SELECT id, content FROM notes'):
            print(f"{row[0]}: {row[1]}")


def add_event(name: str, time: str):
    """Add an event and update calendar. Time format: YYYY-MM-DD HH:MM."""
    dt = datetime.datetime.fromisoformat(time)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO events(name, time) VALUES (?, ?)', (name, dt.isoformat()))
        conn.commit()
    generate_calendar()


def list_events():
    """List events."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for row in c.execute('SELECT id, name, time FROM events ORDER BY time'):
            print(f"{row[0]}: {row[1]} at {row[2]}")


def generate_calendar():
    """Generate calendar.ics from stored events."""
    calendar = Calendar()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for name, time in c.execute('SELECT name, time FROM events'):
            e = Event(name=name)
            e.begin = datetime.datetime.fromisoformat(time)
            calendar.events.add(e)
    with open('calendar.ics', 'w') as f:
        f.writelines(calendar)


def add_storage(name: str):
    """Create a substorage folder."""
    path = STORAGE_DIR / name
    path.mkdir(parents=True, exist_ok=True)
    print(f"Created storage: {path}")


def add_document(label: str, file_path: str, storage: str = None):
    """Add a document for quick access, optionally into a substorage."""
    storage_path = STORAGE_DIR / (storage or '')
    storage_path.mkdir(parents=True, exist_ok=True)
    src = Path(file_path)
    dest = storage_path / src.name
    shutil.copy(src, dest)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO documents(label, path, storage) VALUES (?, ?, ?)', (label, str(dest), storage))
        conn.commit()
    print(f"Stored document at {dest}")


def list_documents():
    """List documents with their stored paths."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for row in c.execute('SELECT id, label, path, storage FROM documents'):
            ident, label, path, storage = row
            print(f"{ident}: {label} -> {path} (storage: {storage or 'root'})")


def build_parser():
    parser = argparse.ArgumentParser(description='Simple todo app')
    sub = parser.add_subparsers(dest='command')

    t = sub.add_parser('add-task', help='Add a task')
    t.add_argument('description')
    t.add_argument('expires')

    sub.add_parser('list-tasks', help='List tasks')

    n = sub.add_parser('add-note', help='Add a note')
    n.add_argument('content')

    sub.add_parser('list-notes', help='List notes')

    e = sub.add_parser('add-event', help='Add an event')
    e.add_argument('name')
    e.add_argument('time')

    sub.add_parser('list-events', help='List events')

    s = sub.add_parser('add-storage', help='Create substorage')
    s.add_argument('name')

    d = sub.add_parser('add-doc', help='Store document')
    d.add_argument('label')
    d.add_argument('file_path')
    d.add_argument('--storage', default=None)

    sub.add_parser('list-docs', help='List documents')

    return parser


def main():
    init_db()
    parser = build_parser()
    args = parser.parse_args()
    if args.command == 'add-task':
        add_task(args.description, args.expires)
    elif args.command == 'list-tasks':
        list_tasks()
    elif args.command == 'add-note':
        add_note(args.content)
    elif args.command == 'list-notes':
        list_notes()
    elif args.command == 'add-event':
        add_event(args.name, args.time)
    elif args.command == 'list-events':
        list_events()
    elif args.command == 'add-storage':
        add_storage(args.name)
    elif args.command == 'add-doc':
        add_document(args.label, args.file_path, args.storage)
    elif args.command == 'list-docs':
        list_documents()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

