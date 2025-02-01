# Калькулятор сумм

Веб-приложение для подсчета сумм по категориям с ограничением на количество сообщений.

## Функционал

- Ввод данных в формате "Название - число"
- Поддержка многострочного ввода
- Автоматическое суммирование значений по категориям
- Ограничение в 6 сообщений на одну сессию
- Возможность очистки данных
- Начало нового подсчета

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ваш-username/calculator-sum.git
cd calculator-sum
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск

```bash
python app.py
```

Приложение будет доступно по адресу http://localhost:5000

## Технологии

- Python
- Flask
- SQLAlchemy
- Bootstrap
- JavaScript 
