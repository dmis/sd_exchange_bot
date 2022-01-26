from django.core.management.base import BaseCommand
from django.conf import settings
import telebot
from polygon import RESTClient
from ...models import User, Portfolio
import datetime
from datetime import date
from telebot import types
import locale

bot = telebot.TeleBot(settings.TOKEN)


class Command(BaseCommand):
    help = 'Stock exchange bot'

    def handle(self, *args, **options):
        bot.infinity_polling()


@bot.message_handler(commands=["start"])
def start(m):
    u = User.objects.filter(id=m.chat.id)
    if not u:
        u = User(id=m.chat.id)
        u.firstname = m.chat.first_name
        u.secondname = m.chat.last_name
        u.username = m.chat.username
        try:
            u.save()
        except:
            print(f'An error occurred while saving the user to the database: id {u.id}, username {u.username}')
    else:
        u = u[0]
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(m.chat.id,
                     f"Hello {u.firstname if u.firstname is not None else u.username}! \nYou can type any ticker and I will give you info",
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def text_message(message: str):
    text = message.text.upper()
    resp = request_ticker(text)
    if resp:
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup.add(telebot.types.InlineKeyboardButton(text='1 day', callback_data=f'{text}|day'))
        markup.add(telebot.types.InlineKeyboardButton(text='1 week', callback_data=f'{text}|week'))
        markup.add(telebot.types.InlineKeyboardButton(text='1 month', callback_data=f'{text}|month'))
        markup.add(telebot.types.InlineKeyboardButton(text='1 year', callback_data=f'{text}|year'))
        desc = "".join(["*%s*, " % i for i in resp.similar])
        bot.send_message(message.chat.id, text=f"*{resp.name}* | {resp.exchange} | {resp.sector} \n"
                                               f"_{resp.description}_ \n\n"
                                               f"Peers {desc} \n\n"
                                               f"*For what period would you like to receive information:*\n",
                         reply_markup=markup, parse_mode='Markdown')

    else:
        bot.send_message(message.chat.id, 'Sorry, but the ticker was not found')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, text='Wait a moment, please...')
    data = call.data.split('|')
    today = date.today()  # date(2022, 1, 1)
    if data[1] == 'day':
        today = today - datetime.timedelta(days=1)
        answer = request_agg(data[0], data[1], today, date.today())
    elif data[1] == 'week':
        today = today - datetime.timedelta(weeks=1)
        answer = request_agg(data[0], data[1], today, date.today())
    elif data[1] == 'month':
        today = today - datetime.timedelta(days=30)
        answer = request_agg(data[0], data[1], today, date.today())
    elif data[1] == 'year':
        today = today - datetime.timedelta(days=365)
        answer = request_agg(data[0], data[1], today, date.today())
    else:
        answer = 'wrong code :('
    markup = set_keyboard(call.message.chat.id, data[0])
    bot.send_message(call.message.chat.id, answer, reply_markup=markup, parse_mode='Markdown')


def set_keyboard(chat_id: int, ticker: str) -> types.ReplyKeyboardMarkup:
    u = User(id=chat_id)
    u.portfolio_set.create(ticker=ticker)

    pfs = Portfolio.objects.filter(user=chat_id).order_by('-id')[:5]
    markup = types.ReplyKeyboardMarkup(row_width=1)
    res = []
    for i in pfs:
        res.append(i.ticker)
    markup.row(*res)
    return markup


def request_agg(text: str, timespan: str, date_from: str, date_to: str) -> str:
    with RESTClient(settings.POLYGON_KEY) as client:
        try:
            resp = client.stocks_equities_aggregates(
                ticker=text,
                multiplier=1,
                timespan=timespan,
                from_=date_from,
                to=date_to)
            if resp and resp.resultsCount > 0:
                d = resp.results[-1]
                answer = f"*{resp.ticker}* for 1 {timespan}:\n" \
                         f"*Open price:*  {d['o']}\n" \
                         f"*Close price:*  {d['c']}\n" \
                         f"*High price:*   {d['h']}\n" \
                         f"*Low price:*    {d['l']}\n" \
                         f"*The number of transactions:*            {d['n']}\n" \
                         f"*The trading volume:*                       {d['v']}\n" \
                         f"*The volume weighted average price:* {d['vw']}"
            return answer
        except:
            return "An error occurred while processing "


def request_ticker(text: str) -> bool:
    with RESTClient(settings.POLYGON_KEY) as client:
        try:
            resp = client.reference_ticker_details(symbol=text)
            print(f"")
            return resp
        except:
            return False
