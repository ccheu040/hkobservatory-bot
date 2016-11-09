import json
import feedparser
import bs4
import telegram
import telegram.ext

bot_token = "243527010:AAGWz1pfH5uIKOFAH2A6M6wwIoVdhwhjxzY"
updater = telegram.ext.Updater(token=bot_token)
dispatcher = updater.dispatcher


def get_user_language(user_id):
    with open("user_language.txt") as f:
        user_language = json.load(f)
    language = user_language.get(user_id, "English")
    return language;


def get_topics():
    with open("topics.txt") as f:
        topics = json.load(f)
        topics = "The topics I can tell you about are:\n" + "\n".join(topics)
    return topics


def get_current(user_id):
    language = get_user_language(user_id)
    if language == "English":
        rss = feedparser.parse("http://rss.weather.gov.hk/rss/CurrentWeather.xml")
    elif language == "Traditional":
        rss = feedparser.parse("http://rss.weather.gov.hk/rss/CurrentWeather_uc.xml")
    elif language == "Simplified":
        rss = feedparser.parse("http://gbrss.weather.gov.hk/rss/CurrentWeather_uc.xml")

    current = bs4.BeautifulSoup(rss.entries[0].summary, "html.parser")
    for br in current.find_all("br"):
        if br.previous_element != br:
            br.previous_element.wrap(current.new_tag("p"))
        br.decompose()
    for tr in current.find_all("tr"):
        tr.decompose()
    for span in current.find_all("span"):
        span.decompose()
    for table in current.find_all("table"):
        if table.find_previous("p") != current.p:
            table.find_previous("p").decompose()
        table.decompose()

    message = []
    for string in current.stripped_strings:
        message.append(" ".join(string.split()))
    message = "\n".join(message)
    return message


def get_warning(user_id):
    language = get_user_language(user_id)
    if language == "English":
        rss = feedparser.parse("http://rss.weather.gov.hk/rss/WeatherWarningBulletin.xml")
    elif language == "Traditional":
        rss = feedparser.parse("http://rss.weather.gov.hk/rss/WeatherWarningBulletin_uc.xml")
    elif language == "Simplified":
        rss = feedparser.parse("http://gbrss.weather.gov.hk/rss/WeatherWarningBulletin_uc.xml")
    warning = bs4.BeautifulSoup(rss.entries[0].summary, "html.parser")
    message = warning.get_text()
    return message


def start(bot, update):
    message = "Hi, I'm HKObservatoryBot! I can send you information about /topics from the HK Observatory."
    bot.sendMessage(chat_id=update.message.chat_id, text=message)


def inline_query(bot, update):
    query = update.inline_query.query
    if not query:
        return

    results = []
    user_id = str(update.inline_query.from_user.id)

    if query.lower() in "english":
        results.append(
            telegram.InlineQueryResultArticle(
                id="English",
                title="English",
                input_message_content=telegram.InputTextMessageContent("OK"),
                description="Select English as topic information language"
            )
        )
    if query.lower() in "topics":
        results.append(
            telegram.InlineQueryResultArticle(
                id="Topics",
                title="Topics",
                input_message_content=telegram.InputTextMessageContent(get_topics()),
                description="List of available topics"
            )
        )
    if query.lower() in "tellme current":
        results.append(
            telegram.InlineQueryResultArticle(
                id="Current",
                title="Current Weather",
                input_message_content=telegram.InputTextMessageContent(get_current(user_id)),
                description="Current weather from the HK Observatory"
            )
        )
    if query.lower() in "tellme warning":
        results.append(
            telegram.InlineQueryResultArticle(
                id="Warning",
                title="Warning",
                input_message_content=telegram.InputTextMessageContent(get_warning(user_id)),
                description="Warnings in force"
            )
        )
    if query in "繁體中文":
        results.append(
            telegram.InlineQueryResultArticle(
                id="Traditional",
                title="繁體中文",
                input_message_content=telegram.InputTextMessageContent("知道了"),
                description="Select 繁體中文 as topic information language"
            )
        )
    if query in "简体中文":
        results.append(
            telegram.InlineQueryResultArticle(
                id="Simplified",
                title="简体中文",
                input_message_content=telegram.InputTextMessageContent("知道了"),
                description="Select 简体中文 as topic information language"
            )
        )
    bot.answerInlineQuery(update.inline_query.id, results)


def inline_result(bot, update):
    result_id = update.chosen_inline_result.result_id
    user_id = str(update.chosen_inline_result.from_user.id)

    with open("user_language.txt") as f:
        user_language = json.load(f)

    with open("user_language.txt", "w") as f:
        if result_id == "English":
            user_language[user_id] = "English"
        elif result_id == "Traditional":
            user_language[user_id] = "Traditional"
        elif result_id == "Simplified":
            user_language[user_id] = "Simplified"
        json.dump(user_language, f)


start_handler = telegram.ext.CommandHandler("start", start)
dispatcher.add_handler(start_handler)

inline_query_handler = telegram.ext.InlineQueryHandler(inline_query)
dispatcher.add_handler(inline_query_handler)

inline_result_handler = telegram.ext.ChosenInlineResultHandler(inline_result)
dispatcher.add_handler(inline_result_handler)

updater.start_polling()
updater.idle()
