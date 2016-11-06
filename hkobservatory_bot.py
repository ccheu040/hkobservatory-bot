import feedparser
import bs4
import telegram.ext

bot_token = "228404369:AAF_vs8a2cDGiaAVrrLy8eDRzcAWobkX8qg"
updater = telegram.ext.Updater(token=bot_token)
dispatcher = updater.dispatcher


# Sends information from HK Observatory about specified topic
def tellme(bot, update, args):
    topic = " ".join(args)

    if not args:
        message = "I need a topic to tell you about! See /topic for a list of available topics."

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

    bot.sendMessage(chat_id=update.message.chat_id, text=message)


tellme_handler = telegram.ext.CommandHandler("tellme", tellme, pass_args=True)
dispatcher.add_handler(tellme_handler)

updater.start_polling()
updater.idle()
