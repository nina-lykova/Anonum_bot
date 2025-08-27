import telebot # Основная библиотека для работы с Telegram Bot API. 
import threading #Модуль для работы с потоками. Позволяет выполнять несколько задач одновременно.
import queue #Модуль для создания очередей. Очереди позволяют безопасно передавать данные между потоками.
import logging #Модуль для логирования событий/Логирование - это процесс записи информации о работе программы в файл или другое хранилище.
from config import API_TOKEN
import time
from telebot import types

# Настройка логирования
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
"""Объяснение:
•   logging.basicConfig(...): Эта функция настраивает базовую конфигурацию логирования.
• filename='bot.log': Указывает, что логи должны записываться в файл bot.log.
• level=logging.INFO: Устанавливает минимальный уровень логирования INFO.
        •   logging.info("Сообщение информационного уровня")
        •   logging.warning("Предупреждение")
        •   logging.error("Ошибка")
        •   logging.critical("Критическая ошибка")
• format='%(asctime)s - %(levelname)s - %(message)s': Указывает формат сообщений лога:
        * %(asctime)s: Время создания записи лога.
        * %(levelname)s: Уровень логирования (например, INFO, WARNING, ERROR).
        * %(message)s: Текст сообщения лога."""

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN) 

# Очередь для поиска собеседников
waiting_queue = queue.Queue()

#кидаем жалобу на юзера(будет предоставлен выбор типов жалоб для юзера в виде кнопок)
@bot.message_handler(commands=['report'])
def handler_report(message):
    markup = types.InlineKeyboardMarkup()#Создаем переменную со встроенной кнопкой
    markup.add(types.InlineKeyboardButton('📰Реклама', callback_data='report_spam'))
    markup.add(types.InlineKeyboardButton('💰Продажа', callback_data='report_sale'))
    markup.add(types.InlineKeyboardButton('👊Насилие', callback_data='report_violence'))
    markup.add(types.InlineKeyboardButton('🤬Оскорбление', callback_data='report_insult'))
    markup.add(types.InlineKeyboardButton('🤑Мошеничество', callback_data='report_fraud'))
    bot.send_message(message.chat.id, "Выберите причину жалобы:", reply_markup=markup)
# Обработчик callback-запросов от inline-кнопок
@bot.callback_query_handler(func=lambda call: call.data.startswith('report_'))
def callback_query(call):
    # Обрабатываем нажатие на кнопку жалобы
    report_type = call.data[7:]  # Получаем тип жалобы из callback_data
    bot.answer_callback_query(call.id, f"Жалоба на {report_type} принята!")


# Словарь для хранения соответствия user_id и chat_id собеседника
user_pairs = {}
#проверяем есть ли хотя бы два пользователя в очереди
def check_queue():
    while True:
        try:
            if waiting_queue.qsize() >= 2:
                #Используется waiting_queue.get() для извлечения каждого user_id из очереди.

                user_id1 = waiting_queue.get()  # Извлекаем первого пользователя из очереди
                user_id2 = waiting_queue.get()  # Извлекаем второго пользователя из очереди
                logging.info(f"Соединяем пользователей {user_id1} и {user_id2}")

                # Сохраняем соответствие между user_id и chat_id собеседника
                user_pairs[user_id1] = user_id2
                user_pairs[user_id2] = user_id1

                # Отправляем обоим пользователям сообщение о том, что они соединены
                bot.send_message(user_id1,"""Собеседник найден
/next -- искать нового собеседника
                 
/stop -- закончить диалог""")
                bot.send_message(user_id2,"""Собеседник найден
/next -- искать нового собеседника
                 
/stop -- закончить диалог""")          
            time.sleep(1)  # Пауза в 1 секунду, чтобы не загружать процессор

        except Exception as e:
                    logging.error(f"Ошибка в функции check_queue: {e}")
                    time.sleep(10)  # Увеличиваем паузу после ошибки

#приветсвие 
@bot.message_handler(commands=['start'])
#приветствуем пользователя и добавляем в очередь ожидания
def handler_start(message):
    bot.reply_to(message, "Привет ты попал в анонимный чат, в нем нельзя ругаться, присылать фото, и передавать юзы(только платно:) - удачи в общении!!!")
    user_id = message.chat.id
    logging.info(f"Пользователь {user_id} запустил команду /start") #Записываем инфо в лог
    waiting_queue.put(user_id) #Добавляем user_id в очередь
    bot.reply_to(message,"Вы добавлены в очередь")


#стопаем юзера и даем ему выбор в виде: выбрать другого собеседника или кидануть на него жалобу(кнопки)
@bot.message_handler(commands=['stop'])
def handler_stop(message):
    #Получем юзер_айди собеседника
    user_id = message.chat.id
    try:
        if user_id in user_pairs:#проверяем, что он сеть в словаре
            sobes_id = user_pairs[user_id]#Получаем user_id собеседника из словаря
                #Сообщаем об этом юзерам
            bot.send_message(user_id, """Вы закончили связь с вашим собеседником🙄
                             
Напиши /search чтобы найти следующего, если тебе не понравился собеседник напиши /report и кидани на него жалобу
                             
Если хотите, оставьте мнение о вашем собеседнике. Это поможет находить вам подходящих собеседников""")

            bot.send_message(sobes_id, """Собеседник завершил чат😭
                           
Напиши /search чтобы найти следующего, если тебе не понравился собеседник напиши /report и кидани на него жалобу
                             
Если хотите, оставьте мнение о вашем собеседнике. Это поможет находить вам подходящих собеседников""")

                #удаляем юзерa
            del user_pairs[user_id]
            del user_pairs[sobes_id]
        else:
            bot.send_message(user_id, "Вы не соединены ни с кем:(")
    except Exception as e:
        logging.exception("Ошибка в handle_stop")

#некст юзер
@bot.message_handler(commands=['next'])
def handler_next(message):
    user_id = message.chat.id
    if user_id in user_pairs:
        sobes_id = user_pairs[user_id]

        del user_pairs[user_id]
        del user_pairs[sobes_id]

        waiting_queue.put(user_id) #Добавляем user_id в очередь
        
        bot.send_message(user_id, "Вы завершили чат и добавлены в очередь ожидания")
        bot.send_message(sobes_id, 'Собеседник завершил чат, хотите найти нового? Напишите /search')

#Ищем следующего юзера
@bot.message_handler(commands=['search'])
def handler_search(message):
    user_id = message.chat.id
    waiting_queue.put(user_id) #Добавляем user_id в очередь
    bot.send_message(user_id, 'Ищем для вас собеседника!')
    check_queue()

# пересылка соо
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    #Получем юзер_айди собеседника
    user_id = message.chat.id
    if user_id in user_pairs:#проверяем, что он сеть в словаре
        user_id = user_pairs[user_id]#Получаем user_id собеседника из словаря 
        # Пересылаем соособеседнику
        bot.send_message(user_id, message.text)


if __name__ == '__main__':
    threading.Thread(target=check_queue, daemon=True).start()
    print("Бот запущен")
    bot.infinity_polling()
