import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import quote


TOKEN = '7729982272:AAESTIPTnCnCgDzkR1WcvAtrNAFE-4iEic4'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum\n\nMenga biror-bir fe'lni yozing arab tilida, men sizga uni tuslab beraman. \n\n\nUyalmang :))")

# Функция для обработки введённого глагола
async def conjugate_verb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаём экземпляр cloudscraper один раз
    scraper = cloudscraper.create_scraper()
    
    # Заголовки для совместимости
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://conjugator.reverso.net/'
    }
    
    # Получаем введённый глагол
    verb = update.message.text.strip()
    encoded_verb = quote(verb)
    url = f"https://conjugator.reverso.net/conjugation-arabic-verb-{encoded_verb}.html"
    
    try:
        # Отправляем запрос через cloudscraper
        response = scraper.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Проверка на ошибки HTTP
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем все блоки спряжений
        conjugation_blocks = soup.find_all('div', class_='blue-box-wrap')
        if not conjugation_blocks:
            await update.message.reply_text("Ma'lumot topilmadi.\nIltimos fe'lni yozilishiga e'tibor bering.")
            return

        # Форматируем результат
        result = f"Fe'lni tuslanishi {verb}:\n\n"
        for block in conjugation_blocks:
            tense_title_elem = block.find('p')
            tense_title = tense_title_elem.text.strip() if tense_title_elem else "Unknown Tense"
            ar_tense = block.find('span', class_='ar-font')
            tense_ar = ar_tense.text.strip() if ar_tense else ""
            result += f"**{tense_title} {tense_ar}**\n"

            verb_items = block.find_all('li')
            for item in verb_items:
                pronoun = item.find('i', class_='graytxt')
                verb_form = item.find('i', class_='verbtxt-term')
                transliteration = item.find('div', class_='transliteration')

                pronoun_text = pronoun.text.strip() if pronoun else ""
                verb_text = verb_form.text.strip() if verb_form else ""
                
                # Проверяем транслитерацию поэтапно
                trans_text = ""
                if transliteration:
                    trans_elem = transliteration.find('i', class_='verbtxt-term')
                    trans_text = trans_elem.text.strip() if trans_elem else ""

                if verb_text:  # Добавляем только если есть форма глагола
                    result += f"{pronoun_text} — {verb_text} ({trans_text})\n"

            result += "\n"

        # Разделяем на части для Telegram
        messages = [result[i:i+4096] for i in range(0, len(result), 4096)]
        for msg in messages:
            await update.message.reply_text(msg)
        
        # Запрашиваем следующий глагол
        await update.message.reply_text("Keyingi fe'lni kiriting:")

    except cloudscraper.exceptions.CloudflareChallengeError as e:
        await update.message.reply_text("Ma'lumot topilmadi.\nIltimos fe'lni yozilishiga e'tibor bering.")
    except Exception as e:
        await update.message.reply_text("Ma'lumot topilmadi.\nIltimos fe'lni yozilishiga e'tibor bering.")

# Главная функция для запуска бота
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, conjugate_verb))
    application.run_polling()

if __name__ == '__main__':
    main()