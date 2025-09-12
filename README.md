# Todo CLI App

This simple command line app lets you keep track of tasks, notes, events and documents.

## Features
- Add tasks with an expiration date.
- A copy/paste notes section for snippets you don't want to forget.
- Add events which generate a `calendar.ics` file that can be imported into calendar apps.
- Store important documents for quick access and organize them with substorages.

## Setup
```
pip install -r requirements.txt
```

## Usage
```
python app.py add-task "Buy milk" 2024-06-30
python app.py list-tasks

python app.py add-note "Don't forget to call mom"
python app.py list-notes

python app.py add-event "Meeting" "2024-07-01 09:00"
python app.py list-events

python app.py add-storage receipts
python app.py add-doc "Tax Form" path/to/file.pdf --storage receipts
python app.py list-docs
```
The generated `calendar.ics` file can be imported into your calendar application.
