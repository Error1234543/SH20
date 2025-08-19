import os
import re
import telebot
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")  # Render me ENV var set karoge
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📂 File Handler
@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        text = downloaded_file.decode("utf-8", errors="ignore")

        output_lines = []

        # 🎥 Video extractor (mp4 + m3u8)
        video_pattern = r'"(.+?\.mp4)"\s+"(https?://[^\s"]+)"'
        for name, url in re.findall(video_pattern, text):
            clean_name = name.replace(".mp4", "")
            output_lines.append(f"📹 {clean_name} : {url}")

        # 📄 PDF extractor
        pdf_pattern = r'"(.+?\.pdf)"\s+"(https?://[^\s"]+)"'
        for name, url in re.findall(pdf_pattern, text):
            clean_name = name.replace(".pdf", "")
            output_lines.append(f"📄 {clean_name} : {url}")

        if output_lines:
            output_text = "\n".join(output_lines)
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(output_text)
            with open("output.txt", "rb") as f:
                bot.send_document(message.chat.id, f)
        else:
            bot.reply_to(message, "⚠️ File me koi video/pdf link nahi mila.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# Webhook route
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.stream.read().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("RENDER_EXTERNAL_URL") + "/" + TOKEN)
    return "Webhook set", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
