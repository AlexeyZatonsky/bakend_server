#  Видеохостинг на FastAPI


Структура директории проекта на __*[FastAPI](https://fastapi.tiangolo.com/)*__ реализована в соответствии с  
рекомендациями **[FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)**

+ Асинхронное подключение к базе данных PostgreSQL с помощью **[SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)**.


<br/>
<br/>

__Рабочая ветка: **[skeleton](https://github.com/AlexeyZatonsky/bakend_server/tree/skeleton)**  
Стабильная ветка: **[main](https://github.com/AlexeyZatonsky/bakend_server/tree/main)**__

## Структура проекта
```

bakend_server
│
│   .gitignore
│   alembic.ini
│   LICENSE
│   README.md
│   requirements.txt
│
├───alembic
│   │   env.py
│   │   README
│   │   script.py.mako
│   │
│   └───versions
│           3b363030fdcb_.py
│
├───media
│   └───(Channel UUID)
│           (get_from_user_title).mp4
│
├───src
│   │   app.py
│   │   database.py
│   │   __main__.py
│   │
│   ├───auth
│   │       base_config.py
│   │       manager.py
│   │       models.py
│   │       schemas.py
│   │       utils.py
│   │
│   ├───channels
│   │       models.py
│   │       router.py
│   │       schemas.py
│   │       services.py
│   │
│   ├───rating_description
│   │       models.py
│   │       schemas.py
│   │       services.py
│   │
│   ├───settings
│   │       .env
│   │       config.py
│   │
│   └───videos
│           models.py
│           router.py
│           schemas.py
│           services.py
│
├───temlates
└───tests
```


## Запуск сервера
1. _Установка виртуального окружения_  
	1. python -m venv .venv  
	2. pip install -r requirements.txt  
	- Или через IDE  
2.  _Создание базы данных PostgreSQL_
3.   _Создание файла *env.py* в файле */src/settings.py*_
4.   _Заполнить env.py данными:_  
	+    DB_HOST  
	+    DB_NAME  
	+    DB_PASS  
	+    DB_PORT  
	+    DB_USER  
	+    SERVER_HOST  
	+    SERVER_PORT  
	+    SECRET_AUTH.  
1.   _Выполнение ревизии и генерации таблиц в БД_  
	1.  alembic revision --autogenerate  
	2.  alembic upgrade head  

