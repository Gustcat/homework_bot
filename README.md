## homework_bot

### Описание проекта
Телеграм-бот, который следит за статусом проектной работы на ревью. При изменении статуса присылает сообщение по указнному ID.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Gustcat/homework_bot.git
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 homework.py
```

### Автор
Ekaterina Gustova https://github.com/Gustcat
