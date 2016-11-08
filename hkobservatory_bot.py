import json
import feedparser
import bs4
import telegram
import telegram.ext

bot_token = "243527010:AAGWz1pfH5uIKOFAH2A6M6wwIoVdhwhjxzY"
updater = telegram.ext.Updater(token=bot_token)
dispatcher = updater.dispatcher


# Sets default language for new chats to English
def start(bot, update):
    with open("user_language.txt") as f:
        user_language = json.load(f)

    with open("user_language.txt", "w") as f:
        key = str(update.message.chat_id)
        if key not in user_language:
            user_language[key] = "English"
        json.dump(user_language, f)

    message = "Hi, I'm HKObservatoryBot! I can send you information about /topics from the HK Observatory."
    bot.sendMessage(chat_id=update.message.chat_id, text=message)


# Lets users change the language using inline mode
def inline_languages(bot, update):
    query = update.inline_query.query
    if not query:
        return

    results = []
    if query.lower() in "english":
        results.append(
            telegram.InlineQueryResultArticle(
                id="English",
                title="English",
                input_message_content=telegram.InputTextMessageContent("OK"),
                description="Change topic update language to English"
            )
        )
    if query in "繁體中文":
        results.append(
            telegram.InlineQueryResultArticle(
                id="Traditional",
                title="繁體中文",
                input_message_content=telegram.InputTextMessageContent("知道了"),
                description="Change topic update language to 繁體中文"
            )
        )
    if query in "简体中文":
        results.append(
            telegram.InlineQueryResultArticle(
                id="Simplified",
                title="简体中文",
                input_message_content=telegram.InputTextMessageContent("知道了"),
                description="Change topic update language to 简体中文"
            )
        )
    bot.answerInlineQuery(update.inline_query.id, results)


def inline_result(bot, update):
    result_id = update.chosen_inline_result.result_id
    user_id = str(update.chosen_inline_result.from_user.id)

    with open("user_language.txt") as f:
        user_language = json.load(f)

    if result_id == "English":
        with open("user_language.txt", "w") as f:
            user_language[user_id] = "English"
            json.dump(user_language, f)

    elif result_id == "Traditional":
        with open("user_language.txt", "w") as f:
            user_language[user_id] = "Traditional"
            json.dump(user_language, f)

    elif result_id == "Simplified":
        with open("user_language.txt", "w") as f:
            user_language[user_id] = "Simplified"
            json.dump(user_language, f)


# Sends the list of available topics
def topics(bot, update):
    TOPICS = ["current", "warning"]
    message = "The topics I can tell you about are:\n" + "\n".join(TOPICS)
    bot.sendMessage(chat_id=update.message.chat_id, text=message)


# Sends information from HK Observatory about specified topic
def tellme(bot, update, args):
    topic = " ".join(args)

    if not args:
        message = "I need a topic to tell you about! See /topics for a list of available topics."

    # Sends information about the current weather from RSS feed
    elif topic == "current":
        rss = feedparser.parse("http://rss.weather.gov.hk/rss/CurrentWeather.xml")
        current = bs4.BeautifulSoup(rss.entries[0].summary, "html.parser")

        current.table.decompose()
        current.p.p.next_sibling.replace_with("")
        # soup.find("font", size="-1").previous_sibling.previous_sibling.previous_sibling.replace_with("")
        message = []
        for string in current.stripped_strings:
            message.append(" ".join(string.split()))
        message = "\n".join(message)

    # Sends information about current warnings from RSS feed
    elif topic == "warning":
        rss = feedparser.parse("http://rss.weather.gov.hk/rss/WeatherWarningBulletin.xml")
        warning = bs4.BeautifulSoup(rss.entries[0].summary, "html.parser")
        message = warning.get_text()

    else:
        message = "I don't know anything about that. I can only tell you about /topics."

    bot.sendMessage(chat_id=update.message.chat_id, text=message)


start_handler = telegram.ext.CommandHandler("start", start)
dispatcher.add_handler(start_handler)

inline_languages_handler = telegram.ext.InlineQueryHandler(inline_languages)
dispatcher.add_handler(inline_languages_handler)

topics_handler = telegram.ext.CommandHandler("topics", topics)
dispatcher.add_handler(topics_handler)

tellme_handler = telegram.ext.CommandHandler("tellme", tellme, pass_args=True)
dispatcher.add_handler(tellme_handler)

updater.start_polling()
updater.idle()
