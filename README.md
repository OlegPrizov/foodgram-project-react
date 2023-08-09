![Main Foodgram Workflow](https://github.com/OlegPrizov/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Проект «Продуктовый помощник» – Foodgram. Используя этот сервис, пользователи могут публиковать рецепты, подписываться на других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Технологический стек:
1. Python
2. Django
3. Django REST framework
4. PostgreSQL
5. NGINX
6. Gunicorn
7. Docker
8. Docker hub
9. GitHub Actions

## Как развернуть проект на сервере 

1. Устанавливаем Docker Compose на сервер: поочерёдно выполните следующие команды 

``` 
sudo apt update 
sudo apt install curl 
curl -fSL https://get.docker.com -o get-docker.sh 
sudo sh ./get-docker.sh 
sudo apt-get install docker-compose-plugin 
``` 

2. Запускаем Docker Compose на сервере 

Cоздайте на сервере пустой файл docker-compose.production.yml в нужной директории и с помощью редактора nano добавьте в него содержимое из docker-compose.production.yml () 

Создайте и заполните .env файл в той же директории (смотрите ниже, как правильно заполнить env)

Выполните следующую команду из директории с файлом docker-compose.production.yml 

``` 
docker-compose.production.yml 
``` 

Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/ 

``` 
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate 
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic 
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/ 
``` 

На сервере установите Nginx 
```
sudo apt install nginx
``` 

Далее в редакторе nano откройте конфиг Nginx: sudo nano /etc/nginx/sites-enabled/default. Измените настройки location в секции server на следуюшие: 

``` 
# Всё до этой строки оставляем как было. 
    location / { 
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:9000; 

    } 
# Ниже ничего менять не нужно. 
``` 

Перезагрузите конфиг Nginx

``` 
sudo service nginx reload 
``` 

## Как заполнить файл env:

POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
SECRET_KEY = <ваш SECRET_KEY>
ALLOWED_HOSTS = 127.0.0.1,localhost,<ваш IP>
DEBUG = True/False #выберите нужное
Development = True #если переменная отсутсвует, будет использоваться MySQL, а не PostgreSQL

## Развернутый проект:

https://foodgram-naprimerrr.ddns.net/

## Документация API Foodgram:

https://foodgram-naprimerrr.ddns.net/api/docs/

## Об авторе:

[Олег Призов](https://github.com/OlegPrizov)
dockerhub_username: olegprizov
