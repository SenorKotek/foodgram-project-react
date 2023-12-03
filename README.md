Cервис Foodgram, «Продуктовый помощник». На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Технологии:

Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL

### Как запустить проект на своем сервере:

- Клонировать репозиторий
- Установить на сервере Docker, Docker Compose
- в папке infra открыть nginx.conf и указать там свои данные сервера в строке 'server'
- Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra
- Создать Secrets в настройках клонированного репозитория для работы с Git Actions:

```
SECRET_KEY              # ключ Django проекта
DOCKER_PASSWORD         # пароль от DockerHub
DOCKER_USERNAME         # логин DockerHub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # *если ssh-ключ защищен паролем
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота

DB_ENGINE               # django.db.backends.postgresql
DB_NAME                 # postgres
POSTGRES_USER           # postgres
POSTGRES_PASSWORD       # postgres
DB_HOST                 # db
DB_PORT                 # 5432
```
- Запустить на сервере сборку контейнеров:
```
sudo docker compose up -d
```
- Запустить создание миграций и выполнить их:
```
sudo docker compose exec backend python manage.py makemigrations
```
```
sudo docker compose exec backend python manage.py migrate
```
- Собрать статику:
```
sudo docker compose exec backend python manage.py collectstatic --noinput
```
- Создать администратора:
```
sudo docker compose exec backend python manage.py createsuperuser
```
- При желании можно наполнить базу тестовыми данными:
```
sudo docker compose exec backend python manage.py loaddata ingredients.json
```
### Git Actions:

- Проверяют код на соответствие стандарту PEP8 (с помощью пакета flake8)
- Собирают и доставляют докер-образы frontend и backend на Docker Hub
- Разворачивают проект на удаленном сервере
- Отправляют сообщения в Telegram в случае успеха

### Над проектом страдал:

SenorKotek

### Данные суперюзера для ревью:

ip-адрес сервера: 158.160.68.42

Адрес сайта: http://pankotekfoodgram.ddns.net

Логин: nakxwest@yandex.ru

Пароль: ImSoTired

Телеграм-канал с котами, который ведет автор проекта, чтоб ревьювер смог пережить полученные психологические травмы: https://t.me/imacat
