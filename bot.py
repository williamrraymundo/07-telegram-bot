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


async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_notes = load_notes().get(str(update.effective_user.id), [])
    if not user_notes:
        await update.message.reply_text("You have no notes yet.")
        return
    lines = [f"{i}. {n['text']} ({n['date']})" for i, n in enumerate(user_notes, 1)]
    await update.message.reply_text("\n".join(lines))


async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notes = load_notes()
    user_notes = notes.get(str(update.effective_user.id), [])
    try:
        removed = user_notes.pop(int(context.args[0]) - 1)
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /delnote <number>")
        return
    save_notes(notes)
    await update.message.reply_text(f"Deleted: {removed['text']}")


async def reminder_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(context.job.chat_id, f"⏰ Reminder: {context.job.data}")


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        seconds = int(context.args[0])
        text = " ".join(context.args[1:]) or "Time's up!"
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /remind <seconds> <text>")
        return
    context.job_queue.run_once(reminder_callback, seconds, chat_id=update.effective_chat.id, data=text)
    await update.message.reply_text(f"I will remind you in {seconds}s.")

