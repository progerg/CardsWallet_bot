<h1 align="center">CardsWallet</h1>

<p>CardsWallet - бот, где ты можешь хранить все свои дисконтные карточки и пользоваться ими в любое время и с любого устройства</p>

<h2>Основные преимущества</h2>

<ul>
    <li>Все фотографии хранятся на серверах телеграма, у нас лишь file_id</li>
    <li>Не нужно скачивать дополнительные приложения</li>
    <li>Доступно на всех устройствах, где есть телеграм</li>
</ul>


<h2>Запуск бота</h2>

Необходимо создать файл configs.ini, по следующей структуре

```
[DB]
login = your_db_user
password = your_users_password
host = localhost
port = 3306
db_name = your_db_name

[Bot]
token = BOT_TOKEN
admin = 111111;22222
```

Для запуска

```
pip3 install -r requirements.txt

python3 bot.py
```

