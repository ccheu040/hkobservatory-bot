import json
import feedparser
import bs4
import telegram
import telegram.ext

bot_token = "243527010:AAGWz1pfH5uIKOFAH2A6M6wwIoVdhwhjxzY"
updater = telegram.ext.Updater(token=bot_token)
dispatcher = updater.dispatcher


def get_user_language(user_id):
    try:
        with open("user_language.txt") as f:
            user_language = json.load(f)
    except FileNotFoundError:
        user_language = {}
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

    results = []
    user_id = str(update.inline_query.from_user.id)

    if query:
        if query.lower() in "topics":
            results.append(
                telegram.InlineQueryResultArticle(
                    id="topics",
                    title="Topics",
                    input_message_content=telegram.InputTextMessageContent(get_topics()),
                    description="List of available topics"
                )
            )
        if query.lower() in "tellme current":
            results.append(
                telegram.InlineQueryResultArticle(
                    id="tellme_current",
                    title="Current Weather",
                    input_message_content=telegram.InputTextMessageContent(get_feed(user_id, "current")),
                    description="Current weather from the HK Observatory"
                )
            )
        if query.lower() in "tellme warning":
            results.append(
                telegram.InlineQueryResultArticle(
                    id="tellme_warning",
                    title="Warning",
                    input_message_content=telegram.InputTextMessageContent(get_feed(user_id, "warning")),
                    description="Warnings in force"
                )
            )
        if query.lower() in "subscribe current":
            results.append(
                telegram.InlineQueryResultArticle(
                    id="sub_current",
                    title="Subscribe Current",
                    input_message_content=telegram.InputTextMessageContent("You have subscribed to: Current"),
                    description="Subscribe to current to receive updates"
                )
            )
        if query.lower() in "subscribe warning":
            results.append(
                telegram.InlineQueryResultArticle(
                    id="sub_warning",
                    title="Subscribe Warning",
                    input_message_content=telegram.InputTextMessageContent("You have subscribed to: Warning"),
                    description="Subscribe to warning to receive updates"
                )
            )
        if query.lower() in "unsubscribe current":
            results.append(
                telegram.InlineQueryResultArticle(
                    id="unsub_current",
                    title="Unsubscribe Current",
                    input_message_content=telegram.InputTextMessageContent("You have unsubscribed from: Current"),
                    description="Unsubscribe from current to stop receiving updates"
                )
            )
        if query.lower() in "unsubscribe warning":
            results.append(
                telegram.InlineQueryResultArticle(
                    id="unsub_warning",
                    title="Unsubscribe Warning",
                    input_message_content=telegram.InputTextMessageContent("You have unsubscribed from: Warning"),
                    description="Unsubscribe from warning to stop receiving updates"
                )
            )
        if query.lower() in "english":
            results.append(
                telegram.InlineQueryResultArticle(
                    id="lang_en",
                    title="English",
                    input_message_content=telegram.InputTextMessageContent("OK"),
                    description="Select English as topic information language"
                )
            )
        if query in "繁體中文":
            results.append(
                telegram.InlineQueryResultArticle(
                    id="lang_trad",
                    title="繁體中文",
                    input_message_content=telegram.InputTextMessageContent("知道了"),
                    description="Select 繁體中文 as topic information language"
                )
            )
        if query in "简体中文":
            results.append(
                telegram.InlineQueryResultArticle(
                    id="lang_simp",
                    title="简体中文",
                    input_message_content=telegram.InputTextMessageContent("知道了"),
                    description="Select 简体中文 as topic information language"
                )
            )
        )
    bot.answerInlineQuery(update.inline_query.id, results)


def inline_result(bot, update):
    result_id = update.chosen_inline_result.result_id
    user_id = str(update.chosen_inline_result.from_user.id)

    if "lang" in result_id:
        try:
            with open("user_language.txt") as f:
                user_language = json.load(f)
        except FileNotFoundError:
            user_language = {}

        with open("user_language.txt", "w") as f:
            if result_id == "lang_en":
                user_language[user_id] = "English"
            elif result_id == "lang_trad":
                user_language[user_id] = "Traditional"
            elif result_id == "lang_simp":
                user_language[user_id] = "Simplified"
            json.dump(user_language, f)

    elif "sub" in result_id:
        try:
            with open("subscribers.txt") as f:
                subscribers = json.load(f)
        except FileNotFoundError:
            subscribers = {"current":[], "warning":[]}

        with open("subscribers.txt", "w") as f:
            if result_id == "sub_current":
                subscribers["current"].append(user_id)
            elif result_id == "unsub_current":
                try:
                    subscribers["current"].remove(user_id)
                except ValueError:
                    pass

            elif result_id == "sub_warning":
                subscribers["warning"].append(user_id)
            elif result_id == "unsub_warning":
                try:
                    subscribers["warning"].remove(user_id)
                except ValueError:
                    pass
            json.dump(subscribers, f)


start_handler = telegram.ext.CommandHandler("start", start)
dispatcher.add_handler(start_handler)

inline_query_handler = telegram.ext.InlineQueryHandler(inline_query)
dispatcher.add_handler(inline_query_handler)

inline_result_handler = telegram.ext.ChosenInlineResultHandler(inline_result)
dispatcher.add_handler(inline_result_handler)

updater.start_polling()
updater.idle()
