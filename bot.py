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


