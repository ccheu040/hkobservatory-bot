import feedparser
import bs4
import telegram.ext

bot_token = "228404369:AAF_vs8a2cDGiaAVrrLy8eDRzcAWobkX8qg"
updater = telegram.ext.Updater(token=bot_token)
dispatcher = updater.dispatcher

def tellme(bot, update, args):
    topic = " ".join(args)

    if not args:
        bot.sendMessage(chat_id=update.message.chat_id, text="I need a topic to tell you about! See /topic for a list of available topics.")
    elif topic == "current":
        rss = feedparser.parse("http://rss.weather.gov.hk/rss/CurrentWeather.xml")
        soup = bs4.BeautifulSoup(rss.entries[0].summary,"html.parser")

        soup.table.decompose()
        soup.p.p.next_sibling.replace_with("")
        # soup.find("font", size="-1").previous_sibling.previous_sibling.previous_sibling.replace_with("")
        current = []
        for string in soup.stripped_strings:
            current.append(" ".join(string.split()))
        current = "\n".join(current)
        bot.sendMessage(chat_id=update.message.chat_id, text=current)

tellme_handler = telegram.ext.CommandHandler("tellme", tellme, pass_args=True)
dispatcher.add_handler(tellme_handler)

updater.start_polling()
updater.idle()
