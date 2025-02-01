from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import re

# Инициализация бота без прокси
bot = Bot(token="7813948080:AAGH0qdzgzJdWYl80wYiSp5omPcm95zIOYo")
dp = Dispatcher()

# Словарь для хранения сообщений и значений для каждого пользователя
user_data = {}

# Создаем клавиатуру
def get_keyboard():
    buttons = [
        [KeyboardButton(text="📝 Новый подсчет")],
        [KeyboardButton(text="🔄 Очистить")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Я бот для подсчета сумм. Используйте кнопки ниже для управления:\n\n"
        "📝 Новый подсчет - начать новый цикл подсчета\n"
        "🔄 Очистить - очистить текущие данные\n\n"
        "Отправляйте мне сообщения в формате:\nНазвание - число",
        reply_markup=get_keyboard()
    )

@dp.message(lambda message: message.text == "🔄 Очистить")
async def clear_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data:
        user_data[user_id] = {
            'count': 0,
            'values': {}
        }
    await message.reply("История очищена! Можете начать заново.", reply_markup=get_keyboard())

@dp.message(lambda message: message.text == "📝 Новый подсчет")
async def new_count(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {
        'count': 0,
        'values': {}
    }
    await message.reply(
        "Начат новый подсчет!\nОтправьте мне данные в формате:\nНазвание - число",
        reply_markup=get_keyboard()
    )

def parse_line(line):
    # Разделяем строку по тире и очищаем от пробелов
    parts = line.split('-')
    if len(parts) >= 2:
        name = parts[0].strip()
        # Объединяем все части после первого тире (если их несколько)
        value_part = '-'.join(parts[1:]).strip()
        # Ищем число в оставшейся части
        try:
            value = int(value_part)
            return name, value
        except ValueError:
            # Если не удалось преобразовать в число, ищем число через регулярное выражение
            numbers = re.findall(r'-?\d+', value_part)
            if numbers:
                return name, int(numbers[-1])
    return None, None

@dp.message()
async def process_message(message: types.Message):
    user_id = message.from_user.id
    
    # Инициализация данных пользователя, если их нет
    if user_id not in user_data:
        user_data[user_id] = {
            'count': 0,
            'values': {}
        }
    
    # Увеличиваем счетчик сообщений
    user_data[user_id]['count'] += 1
    
    # Разбиваем сообщение на строки
    lines = message.text.split('\n')
    
    # Обрабатываем каждую строку
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Используем улучшенную функцию парсинга строки
        name, value = parse_line(line)
        if name and value is not None:
            # Добавляем или обновляем значение в словаре
            if name in user_data[user_id]['values']:
                user_data[user_id]['values'][name] += value
            else:
                user_data[user_id]['values'][name] = value
    
    # Формируем ответное сообщение
    response = "Значения по категориям:\n"
    
    # Выводим все значения в порядке их появления
    for name, value in user_data[user_id]['values'].items():
        response += f"{name}: {value}\n"
    
    # Добавляем информацию о количестве сообщений
    msg_count = user_data[user_id]['count']
    if msg_count <= 6:
        response += f"\nОтправлено {msg_count} из 6 сообщений"
        
        if msg_count == 6:
            response += "\nДостигнут лимит в 6 сообщений. Следующее сообщение начнет новый отсчет."
    
    if msg_count > 6:
        # Сбрасываем все данные и начинаем новый цикл
        user_data[user_id] = {
            'count': 1,
            'values': {}
        }
        
        # Обрабатываем текущее сообщение для нового цикла
        for line in lines:
            line = line.strip()
            if not line:
                continue
            name, value = parse_line(line)
            if name and value is not None:
                user_data[user_id]['values'][name] = value
        
        response = "Начат новый отсчет.\n\nЗначения по категориям:\n"
        for name, value in user_data[user_id]['values'].items():
            response += f"{name}: {value}\n"
        response += f"\nОтправлено 1 из 6 сообщений"
    
    await message.reply(response, reply_markup=get_keyboard())

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main()) 