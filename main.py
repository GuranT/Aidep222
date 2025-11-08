import os
import logging
import telebot
import requests
import json

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

print("🔧 Проверка переменных...")
print(f"BOT_TOKEN: {'✅' if BOT_TOKEN else '❌'}")
print(f"DEEPSEEK_API_KEY: {'✅' if DEEPSEEK_API_KEY else '❌'}")

if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не установлен!")
    exit(1)

if not DEEPSEEK_API_KEY:
    print("❌ ОШИБКА: DEEPSEEK_API_KEY не установлен!")
    exit(1)

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

def ask_deepseek(question):
    """Функция для запроса к DeepSeek API"""
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": question}
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API Request error: {e}")
        return "❌ Ошибка соединения с API"
    except KeyError as e:
        logging.error(f"API Response error: {e}")
        return "❌ Ошибка в ответе API"
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "❌ Неожиданная ошибка"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
🤖 *DeepSeek AI Assistant* 

Я ваш персональный AI-помощник! Задавайте любые вопросы:

• 💻 Программирование и код
• 📚 Обучение и объяснения  
• 🌐 Переводы текстов
• 💡 Идеи и решения
• 📝 Написание текстов

Просто напишите ваш вопрос!
    """
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['info'])
def send_info(message):
    info_text = """
📊 *Информация о боте*

• 🤖 AI: DeepSeek API
• 🚀 Хостинг: Render.com
• 💬 Версия: 2.0
• 📞 Стабильная версия

Бот работает 24/7!
    """
    bot.reply_to(message, info_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_text = message.text
        
        # Показываем индикатор набора
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Используем DeepSeek API
        answer = ask_deepseek(user_text)
        
        # Разбиваем длинные сообщения
        if len(answer) > 4000:
            chunks = [answer[i:i+4000] for i in range(0, len(answer), 4000)]
            for chunk in chunks:
                bot.reply_to(message, chunk)
        else:
            bot.reply_to(message, answer)
                
    except Exception as e:
        logging.error(f"Error: {e}")
        bot.reply_to(message, "❌ Произошла ошибка. Попробуйте еще раз через минуту.")

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    print("🚀 Запуск бота...")
    print("🤖 Бот запущен и готов к работе!")
    bot.infinity_polling()
