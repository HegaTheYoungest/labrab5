#мой код для телеграм бота @OIBTERMSBOT
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN

def load_terms():
    try:
        with open('terms.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except:
        return {}

TERMS = load_terms()
TERMS_LIST = sorted(TERMS.keys())
TERMS_PER_PAGE = 10

# создание словаря терминов по буквам для удобста
TERMS_BY_LETTER = {}
for term in TERMS_LIST:
    first_letter = term[0].upper()
    if first_letter not in TERMS_BY_LETTER:
        TERMS_BY_LETTER[first_letter] = []
    TERMS_BY_LETTER[first_letter].append(term)

# сортируем буквы для удобства
LETTERS = sorted(TERMS_BY_LETTER.keys())

print(f"✅ Загружено терминов: {len(TERMS)}")
print(f"✅ Букв: {len(LETTERS)}")


# клавиатура над(если телефон) или под( если пк) сообщением с кнопками для совершения разных действий спсиок терминов и тд
def get_bottom_keyboard():
    keyboard = [
        [KeyboardButton("📋 Список терминов")],
        [KeyboardButton("🔤 Поиск по букве"), KeyboardButton("❓ Помощь")],
        [KeyboardButton("✏️ Или просто напишите название интересующего вас термина")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


#клавиатура с буквами для удобног поиска терминов п обуквам
def get_letters_keyboard():
    keyboard = []
    row = []
    for i, letter in enumerate(LETTERS):
        row.append(InlineKeyboardButton(letter, callback_data=f"letter_{letter}"))
        if len(row) == 7:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("❌ Закрыть", callback_data="close_letters")])
    return InlineKeyboardMarkup(keyboard)


# клавиатура со всеми терминами, но отсортироваными и по цифрам
def get_terms_keyboard(page):
    start = page * TERMS_PER_PAGE
    end = min(start + TERMS_PER_PAGE, len(TERMS_LIST))

    keyboard = []
    for i in range(start, end):
        term = TERMS_LIST[i]
        number = i + 1
        display_term = f"{number}. {term}"
        if len(display_term) > 40:
            display_term = display_term[:37] + "..."
        keyboard.append([InlineKeyboardButton(display_term, callback_data=f"term_{i}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ НАЗАД", callback_data=f"page_{page - 1}"))
    if end < len(TERMS_LIST):
        nav.append(InlineKeyboardButton("ВПЕРЕД ▶️", callback_data=f"page_{page + 1}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("❌ Закрыть", callback_data="close_list")])
    return InlineKeyboardMarkup(keyboard)


# клавиатура для терминов по выбраной букве типо если и то будут термины информация, инф безопасность итд
def get_terms_by_letter_keyboard(letter, page=0):
    terms = TERMS_BY_LETTER.get(letter, [])
    per_page = 10
    start = page * per_page
    end = min(start + per_page, len(terms))

    keyboard = []
    for i in range(start, end):
        term = terms[i]
        idx = TERMS_LIST.index(term)
        number = idx + 1
        display_term = f"{number}. {term}"
        if len(display_term) > 40:
            display_term = display_term[:37] + "..."
        keyboard.append([InlineKeyboardButton(display_term, callback_data=f"term_{idx}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ НАЗАД", callback_data=f"letter_page_{letter}_{page - 1}"))
    if end < len(terms):
        nav.append(InlineKeyboardButton("ВПЕРЕД ▶️", callback_data=f"letter_page_{letter}_{page + 1}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("🔤 Другие буквы", callback_data="show_letters")])
    keyboard.append([InlineKeyboardButton("❌ Закрыть", callback_data="close_letters")])

    return InlineKeyboardMarkup(keyboard)


# основные команды которые бот отправляет при старте
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Бот по ОИБ (Основы информационной безопасности)*\n\n"
        f"📝 *Всего терминов в базе:* {len(TERMS)}\n\n"
        "• Нажмите *«📋 Список терминов»* - все термины с номерами\n"
        "• Нажмите *«🔤 Поиск по букве»* - выберите букву\n\n"
        "👇 Используйте кнопки внизу экрана",
        parse_mode='Markdown',
        reply_markup=get_bottom_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Справка*\n\n"
        f"📝 *Всего терминов в базе:* {len(TERMS)}\n\n"
        "*Как пользоваться:*\n"
        "• Нажмите *«📋 Список терминов»* - увидите все термины\n"
        "• Нажмите *«🔤 Поиск по букве»* - выберите букву\n"
        "• Или просто *напишите название интересующего вас термина*\n\n"
        "*Примеры терминов:*\n"
        "• информационная безопасность\n"
        "• банковская тайна\n"
        "• персональные данные",
        parse_mode='Markdown',
        reply_markup=get_bottom_keyboard()
    )


async def list_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
# отображение всего списка терминов
    if not TERMS:
        await update.message.reply_text("❌ Нет терминов")
        return

    await update.message.reply_text(
        f"📋 *Список терминов ОИБ* (всего: {len(TERMS_LIST)})\n\n"
        f"👇 Нажмите на любой термин:",
        parse_mode='Markdown',
        reply_markup=get_terms_keyboard(0)
    )


async def search_by_letter(update: Update, context: ContextTypes.DEFAULT_TYPE):
# показывает окно с буквами
    await update.message.reply_text(
        f"🔤 *Поиск по буквам*\n\n"
        f"Всего букв: {len(LETTERS)}\n"
        f"Терминов: {len(TERMS_LIST)}\n\n"
        f"🔤 *Выберите букву:*",
        parse_mode='Markdown',
        reply_markup=get_letters_keyboard()
    )


# обрабатывание нажатий по кнопкам
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    print(f"👇 Нажато: '{data}'")
    try:
        # обрабатывание закрытия общего списка
        if data == "close_list":
            print("🔴 Закрываем общий список")
            await query.edit_message_text(
                "Список терминов закрыт.\n\n👇 Используйте кнопки внизу экрана"
            )
            await query.message.reply_text(
                "👇 Используйте кнопки внизу экрана:",
                reply_markup=get_bottom_keyboard()
            )

        # обрабатывание закрытия поиска по буквам
        elif data == "close_letters":
            print("🔴 Закрываем поиск по буквам")
            await query.edit_message_text(
                "Поиск по буквам закрыт.\n\n👇 Используйте кнопки внизу экрана"
            )
            await query.message.reply_text(
                "👇 Используйте кнопки внизу экрана:",
                reply_markup=get_bottom_keyboard()
            )

        # общий спсисок
        elif data.startswith("page_"):
            page = int(data.split("_")[1])
            await query.edit_message_text(
                f"📋 *Список терминов ОИБ* (всего: {len(TERMS_LIST)})\n\n👇 Нажмите на любой термин:",
                parse_mode='Markdown',
                reply_markup=get_terms_keyboard(page)
            )

        elif data.startswith("term_"):
            index = int(data.split("_")[1])
            term = TERMS_LIST[index]
            definition = TERMS.get(term, "❌ Определение не найдено")
            number = index + 1
            await query.message.reply_text(
                f"⭐ *{number}. {term}*\n\n{definition}",
                parse_mode='Markdown',
                reply_markup=get_bottom_keyboard()
            )

        # поиск по буквам!
        elif data == "show_letters":
            await query.edit_message_text(
                f"🔤 *Поиск по буквам*\n\n"
                f"Всего букв: {len(LETTERS)}\n"
                f"Терминов: {len(TERMS_LIST)}\n\n"
                f"👇 *Выберите букву:*",
                parse_mode='Markdown',
                reply_markup=get_letters_keyboard()
            )

        elif data.startswith("letter_"):
            letter = data.split("_")[1]
            terms_count = len(TERMS_BY_LETTER.get(letter, []))
            await query.edit_message_text(
                f"🔤 *Буква '{letter.upper()}'* (всего: {terms_count} терминов)\n\n👇 Выберите термин:",
                parse_mode='Markdown',
                reply_markup=get_terms_by_letter_keyboard(letter, 0)
            )

        elif data.startswith("letter_page_"):
            parts = data.split("_")
            letter = parts[2]
            page = int(parts[3])
            terms_count = len(TERMS_BY_LETTER.get(letter, []))
            await query.edit_message_text(
                f"🔤 *Буква '{letter.upper()}'* (всего: {terms_count} терминов)\n\n👇 Выберите термин:",
                parse_mode='Markdown',
                reply_markup=get_terms_by_letter_keyboard(letter, page)
            )

        else:
            print(f"❌ Неизвестный callback: {data}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        await query.message.reply_text(f"⚠️ Ошибка: {str(e)[:100]}")


# обрабатывание текста на кнопках внизу
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    print(f"📝 Получен текст: {text}")

    # обрабатвание кнопок внизу
    if text == "📋 Список терминов":
        await list_terms(update, context)
    elif text == "🔤 Поиск по букве":
        await search_by_letter(update, context)
    elif text == "❓ Помощь":
        await help_command(update, context)
    elif text == "✏️ Или просто напишите название интересующего вас термина":
        await update.message.reply_text(
            "💡💡 *Подсказка:* 💡💡\n\n"
            "Просто напишите в чат название любого термина,\n"
            "например: *информационная безопасность* или *банковская тайна*\n\n"
            "🙋🏻‍♂️ Бот сам найдёт определение!!",
            parse_mode='Markdown',
            reply_markup=get_bottom_keyboard()
        )
    else:
        # поиск термина по тексту
        lower_text = text.lower()
        if lower_text in TERMS:
            index = TERMS_LIST.index(lower_text)
            number = index + 1
            await update.message.reply_text(
                f"⭐ *{number}. {lower_text}*\n\n{TERMS[lower_text]}",
                parse_mode='Markdown',
                reply_markup=get_bottom_keyboard()
            )
        else:
            matches = [t for t in TERMS_LIST if lower_text in t.lower()]
            if len(matches) == 1:
                idx = TERMS_LIST.index(matches[0])
                num = idx + 1
                await update.message.reply_text(
                    f"⭐ *{num}. {matches[0]}*\n\n{TERMS[matches[0]]}",
                    parse_mode='Markdown',
                    reply_markup=get_bottom_keyboard()
                )
            elif len(matches) > 1:
                kb = []
                for t in matches[:10]:
                    idx = TERMS_LIST.index(t)
                    num = idx + 1
                    kb.append([InlineKeyboardButton(f"{num}. {t[:35]}", callback_data=f"term_{idx}")])
                kb.append([InlineKeyboardButton("❌ Закрыть", callback_data="close_list")])
                await update.message.reply_text(
                    "🔍 *Найдено несколько терминов. Выберите:*",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(kb)
                )
            else:
                await update.message.reply_text(
                    f"❌ Термин *'{text}'* не найден. ❌\n\n"
                    f"Нажмите «📋 Список терминов»  или «🔤 Поиск по букве».",
                    parse_mode='Markdown',
                    reply_markup=get_bottom_keyboard()
                )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"❌ Ошибка: {context.error}")


def main():
    if not TERMS:
        print("❌ НЕТ ТЕРМИНОВ! Проверьте файл terms.json")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list", list_terms))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)

    print("🎉 Бот запущен 🎉")
    print(f"💫 Загружено терминов: {len(TERMS)} 💫")
    print(f"🔤 Букв в алфавите: {len(LETTERS)} 🔤")
    app.run_polling()


if __name__ == "__main__":
    main()