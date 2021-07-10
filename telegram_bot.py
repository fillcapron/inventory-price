import telebot
from api.telebot_api import Telebot

bot = telebot.TeleBot('1889446734:AAE_74_036g0xCNmQNwLrtO9C3MNeC0i_tk')

@bot.message_handler(commands=['inventory', 'help'])
def start_bot(message):
    bot.reply_to(message, f'Привет, введите свой Steam_id')

@bot.message_handler(content_types=['text'])
def send_inventory(message):
    res = Telebot(message.text)
    items=res.get()
    if items:
        bot.send_message(message.from_user.id, '\n'.join(items))
    else:
        bot.send_message(message.from_user.id, 'Вы ввели неправильный Steam_id')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)