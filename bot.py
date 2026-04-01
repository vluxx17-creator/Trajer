import telebot
import subprocess
import os
import threading

# Конфигурация
TOKEN = '8496265267:AAHPesjlLYB8SBDfDHBdQsQ7X1wTEk0XWvU'
bot = telebot.TeleBot(TOKEN)
WORKDIR = "preceon_results"

if not os.path.exists(WORKDIR):
    os.makedirs(WORKDIR)

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True)
    except Exception as e:
        return f"Error: {str(e)}"

def send_result(chat_id, file_path, caption):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'rb') as f:
            bot.send_document(chat_id, f, caption=caption)
    else:
        bot.send_message(chat_id, f"❌ {caption}: Результатов не найдено.")

@bot.message_handler(commands=['start', 'help'])
def help_cmd(message):
    help_text = """
🚀 **Preceon Bot v1.0** 🚀
(Основан на базе PreRecon)

/sub <domain> - Сбор поддоменов (Subfinder + Assetfinder)
/alive <domain> - Проверка живых хостов (HTTPX)
/wayback <domain> - Ссылки из Wayback Machine
/nuclei <domain> - Сканирование на уязвимости (Nuclei)
/port <domain> - Сканирование портов (Naabu)
/js <domain> - Поиск JS файлов
/full <domain> - Полный цикл разведки
    """
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['sub'])
def sub_scan(message):
    try:
        domain = message.text.split()[1]
        msg = bot.send_message(message.chat.id, f"🔍 [Preceon] Ищу поддомены: {domain}...")
        outfile = f"{WORKDIR}/subs_{domain}.txt"
        
        def task():
            cmd = f"subfinder -d {domain} -silent > {outfile}; assetfinder --subs-only {domain} >> {outfile}; sort -u {outfile} -o {outfile}"
            run_cmd(cmd)
            send_result(message.chat.id, outfile, f"Subdomains: {domain}")
            bot.delete_message(message.chat.id, msg.message_id)
        
        threading.Thread(target=task).start()
    except IndexError:
        bot.reply_to(message, "Использование: /sub target.com")

@bot.message_handler(commands=['alive'])
def alive_scan(message):
    try:
        domain = message.text.split()[1]
        msg = bot.send_message(message.chat.id, f"🌐 [Preceon] Проверка живых хостов: {domain}...")
        outfile = f"{WORKDIR}/alive_{domain}.txt"
        
        def task():
            cmd = f"subfinder -d {domain} -silent | httpx -silent -mc 200,301,302,403 > {outfile}"
            run_cmd(cmd)
            send_result(message.chat.id, outfile, f"Alive Hosts: {domain}")
            bot.delete_message(message.chat.id, msg.message_id)
            
        threading.Thread(target=task).start()
    except IndexError:
        bot.reply_to(message, "Использование: /alive target.com")

@bot.message_handler(commands=['wayback'])
def wayback_scan(message):
    try:
        domain = message.text.split()[1]
        msg = bot.send_message(message.chat.id, "⏳ [Preceon] Извлечение Wayback URLs...")
        outfile = f"{WORKDIR}/wayback_{domain}.txt"
        
        def task():
            cmd = f"echo {domain} | waybackurls > {outfile}"
            run_cmd(cmd)
            send_result(message.chat.id, outfile, f"Wayback: {domain}")
            bot.delete_message(message.chat.id, msg.message_id)
            
        threading.Thread(target=task).start()
    except IndexError:
        bot.reply_to(message, "Использование: /wayback target.com")

@bot.message_handler(commands=['nuclei'])
def nuclei_scan(message):
    try:
        domain = message.text.split()[1]
        msg = bot.send_message(message.chat.id, "🛡️ [Preceon] Запуск Nuclei...")
        outfile = f"{WORKDIR}/nuclei_{domain}.txt"
        
        def task():
            cmd = f"subfinder -d {domain} -silent | httpx -silent | nuclei -t nuclei-templates -severity low,medium,high,critical -o {outfile}"
            run_cmd(cmd)
            send_result(message.chat.id, outfile, f"Nuclei Scan: {domain}")
            bot.delete_message(message.chat.id, msg.message_id)
            
        threading.Thread(target=task).start()
    except IndexError:
        bot.reply_to(message, "Использование: /nuclei target.com")

@bot.message_handler(commands=['port'])
def port_scan(message):
    try:
        domain = message.text.split()[1]
        msg = bot.send_message(message.chat.id, "🔌 [Preceon] Сканирование портов...")
        outfile = f"{WORKDIR}/ports_{domain}.txt"
        
        def task():
            cmd = f"naabu -host {domain} -top-100 -silent > {outfile}"
            run_cmd(cmd)
            send_result(message.chat.id, outfile, f"Ports: {domain}")
            bot.delete_message(message.chat.id, msg.message_id)
            
        threading.Thread(target=task).start()
    except IndexError:
        bot.reply_to(message, "Использование: /port target.com")

@bot.message_handler(commands=['js'])
def js_scan(message):
    try:
        domain = message.text.split()[1]
        msg = bot.send_message(message.chat.id, "📜 [Preceon] Поиск JS файлов...")
        outfile = f"{WORKDIR}/js_{domain}.txt"
        
        def task():
            cmd = f"subfinder -d {domain} -silent | httpx -silent | subjs > {outfile}"
            run_cmd(cmd)
            send_result(message.chat.id, outfile, f"JS Files: {domain}")
            bot.delete_message(message.chat.id, msg.message_id)
            
        threading.Thread(target=task).start()
    except IndexError:
        bot.reply_to(message, "Использование: /js target.com")

@bot.message_handler(commands=['full'])
def full_recon(message):
    try:
        domain = message.text.split()[1]
        msg = bot.send_message(message.chat.id, f"🏁 [Preceon] Полный цикл разведки для {domain} начат...")
        
        def task():
            final_file = f"{WORKDIR}/full_{domain}.txt"
            cmd = f"subfinder -d {domain} -silent > {final_file}; assetfinder --subs-only {domain} >> {final_file}; sort -u {final_file} -o {final_file}"
            run_cmd(cmd)
            send_result(message.chat.id, final_file, f"Full Recon: {domain}")
            bot.send_message(message.chat.id, "✅ Полная разведка завершена.")
            
        threading.Thread(target=task).start()
    except IndexError:
        bot.reply_to(message, "Использование: /full target.com")

if __name__ == '__main__':
    print("Бот Preceon запущен...")
    bot.infinity_polling()
