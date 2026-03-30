"""
Live Chat Bridge: Website ↔ Telegram
Enables real-time conversation between student and support agent
"""
import os
from dotenv import load_dotenv
import asyncio
from typing import Dict, Optional
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import uuid

load_dotenv()

# Active chat sessions: {session_id: {student_messages: [], agent_messages: [], active: bool}}
active_sessions: Dict[str, dict] = {}

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_AGENT_ID_STR = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_AGENT_ID = int(TELEGRAM_AGENT_ID_STR) if TELEGRAM_AGENT_ID_STR else None

# Global bot instance
telegram_app: Optional[Application] = None

async def init_telegram_bot():
    """Initialize Telegram bot with message handler"""
    global telegram_app
    
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram bot token not configured")
        return None
    
    telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Handler for /end command
    async def handle_end_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /end_sessionid command to close a session"""
        if update.message.from_user.id != TELEGRAM_AGENT_ID:
            return
        
        command_text = update.message.text
        if command_text.startswith('/end_'):
            session_id = command_text.replace('/end_', '').strip()
            
            if session_id in active_sessions:
                end_session(session_id)
                await update.message.reply_text(f"✅ Session {session_id} has been ended. The student can now use the chatbot normally.")
            else:
                await update.message.reply_text(f"❌ Session {session_id} not found or already ended.")
    
    # Handler for agent replies
    async def handle_agent_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """When agent replies on Telegram, store it for the website"""
        if update.message.from_user.id != TELEGRAM_AGENT_ID:
            return  # Ignore messages from other users
        
        # Find which session this reply belongs to
        message_text = update.message.text
        
        # Check if agent is replying to a specific session
        for session_id, session in active_sessions.items():
            if session.get('active'):
                # Add agent's message to the session
                session['agent_messages'].append({
                    'text': message_text,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✅ Agent replied to session {session_id}: {message_text[:50]}...")
                break
    
    from telegram.ext import CommandHandler
    telegram_app.add_handler(CommandHandler("end", handle_end_command))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_agent_message))
    
    # Start polling in background
    await telegram_app.initialize()
    await telegram_app.start()
    asyncio.create_task(telegram_app.updater.start_polling())
    
    print("✅ Telegram bot initialized and listening for agent replies")
    return telegram_app

async def create_crisis_session(student_message: str) -> str:
    """Create a new crisis chat session and notify agent on Telegram"""
    session_id = str(uuid.uuid4())[:8]
    
    active_sessions[session_id] = {
        'student_messages': [{'text': student_message, 'timestamp': datetime.now().isoformat()}],
        'agent_messages': [],
        'active': True,
        'started_at': datetime.now().isoformat()
    }
    
    # Send alert to agent on Telegram
    if telegram_app:
        bot = telegram_app.bot
        alert_message = f"""
🚨 CRISIS ALERT - Session {session_id}

A student needs immediate support.

Student's message:
"{student_message}"

Time: {datetime.now().strftime('%H:%M:%S')}

Reply to this message to chat with the student in real-time.
Type /end_{session_id} to close this session and return the student to normal chatbot mode.
        """
        try:
            await bot.send_message(chat_id=TELEGRAM_AGENT_ID, text=alert_message)
            print(f"✅ Crisis session {session_id} created and agent notified")
        except Exception as e:
            print(f"❌ Failed to notify agent: {e}")
    
    return session_id

async def send_student_message(session_id: str, message: str):
    """Forward student's message to agent on Telegram"""
    if session_id not in active_sessions:
        return
    
    active_sessions[session_id]['student_messages'].append({
        'text': message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Send to agent on Telegram
    if telegram_app:
        bot = telegram_app.bot
        try:
            await bot.send_message(
                chat_id=TELEGRAM_AGENT_ID,
                text=f"💬 Student (Session {session_id}):\n{message}"
            )
        except Exception as e:
            print(f"❌ Failed to send message to agent: {e}")

def get_agent_messages(session_id: str) -> list:
    """Get new messages from agent for this session"""
    if session_id not in active_sessions:
        return []
    
    messages = active_sessions[session_id]['agent_messages'].copy()
    # Clear the messages after retrieving (so they're only sent once)
    active_sessions[session_id]['agent_messages'] = []
    
    return messages

def is_session_active(session_id: str) -> bool:
    """Check if a crisis session is still active"""
    return session_id in active_sessions and active_sessions[session_id].get('active', False)

def end_session(session_id: str):
    """End a crisis chat session"""
    if session_id in active_sessions:
        active_sessions[session_id]['active'] = False
        print(f"✅ Session {session_id} ended")
