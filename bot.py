"""Telegram reminder and notes bot."""
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()
NOTES_FILE = Path("notes.json")


def load_notes() -> dict:
    if NOTES_FILE.exists():
        return json.loads(NOTES_FILE.read_text(encoding="utf-8"))
    return {}


def save_notes(notes: dict) -> None:
    NOTES_FILE.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi! I can keep notes and set reminders.\n"
        "/note <text> - save a note\n"
        "/notes - list your notes\n"
        "/delnote <n> - delete a note\n"
        "/remind <seconds> <text> - set a reminder"
    )


async def note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /note <text>")
        return
    notes = load_notes()
    user_notes = notes.setdefault(str(update.effective_user.id), [])
    user_notes.append({"text": text, "date": datetime.now().isoformat(timespec="minutes")})
    save_notes(notes)
    await update.message.reply_text(f"Saved note #{len(user_notes)}.")
