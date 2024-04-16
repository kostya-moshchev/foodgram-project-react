# praktikum_new_diplom

https://fooodgram.3utilities.com

Почта админа: admin@admin.com
Пароль админа: admin

# FoodGram

## Описание
«Фудграм» — сервис, где каждый сможет поделиться своими любимыми рецептами, найти новые рецепты, подписаться
на рецепты понравившегося автора, чтобы следить за его обновлениями. Также рецепты можно добавлять в избранное и в 
корзину. Корзина работает таким образом: Вы добавляете рецепт или несколько рецептов в корзину и у Вас есть возможность
распечатать ингредиенты для этого рецепта.
Вот, что было сделано в ходе работы над проектом:
- настроено взаимодействие Python-приложения с внешними API-сервисами;
- создан собственный API-сервис на базе проекта Django;
- созданы образы и запущены контейнеры Docker;
- созданы, развёрнуты и запущены на сервере мультиконтейнерные приложения;
- закреплены на практике основы DevOps, включая CI&CD.

**Инструменты и стек:** #python #Djangorest_framework #Docker #Nginx #PostgreSQL #Djoser 

## Запуск приложения в контейнере на сервере
1. На сервере создайте директорию для приложения:
    ```bash
    mkdir foodgram/infra
    ```
2. В папку _infra_ скопируйте файлы `docker-compose.production.yml`, `nginx.production.conf`.
3. Там же создайте файл `.env` со следующими переменными:
   ```
   POSTGRES_USER=...
    POSTGRES_PASSWORD=...
    POSTGRES_DB=...
    DB_HOST=...
    DB_PORT=...
    SECRET_KEY=...
    ALLOWED_HOSTS=...
   ```
4. В соответствии с `ALLOWED_HOSTS` измените `nginx.production.conf`.

5. Теперь соберем и запустим контейнер:
   ```bash
   sudo docker compose up  -d --build
   ```
6. В окне терминала создадим супер пользователя:
   ```bash
   sudo docker compose exec backend python manage.py createsuperuser
   ```

## Документация
**Redoc** - https://localhost/api/docs/ \
**Главная** - https://localhost/recipes/ \
**API** - https://localhost/api/ \
**Админка** -https://localhost/admin/

Python-разработчик
>[Kostya Moshchev](https://github.com/kostya-moshchev)