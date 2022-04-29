# Yatube

[![CI](https://github.com/8ubble8uddy/yatube_project/workflows/yatube-project/badge.svg
)](https://github.com/8ubble8uddy/yatube_project/actions/workflows/yatube_workflow.yml)

### **Описание**

_[yatube-project](https://github.com/8ubble8uddy/yatube_project) - это социальная сеть для публикации личных дневников и API для неё. На этом сервисе пользователи могут создать свою страницу. Если на нее зайти, то можно посмотреть все записи автора. Пользователи могут заходить на чужие страницы, подписываться на авторов и комментировать их записи. Также записи можно отправить в сообщество и посмотреть там записи разных авторов._

### **Технологии**

```Python``` ```Django``` ```SQLite``` ```pytest``` ```unittest``` ```Docker``` ```Gunicorn``` ```nginx```

### **Как запустить проект:**

Клонировать репозиторий и перейти внутри него в директорию ```infra/```:
```
git clone https://github.com/8ubble8uddy/yatube_project.git
```
```sh
cd yatube_project/infra/
```

Развернуть и запустить проект в контейнерах:
```
docker-compose up -d --build
```

Внутри контейнера ```web```:

- _Выполнить миграции_
  ```
  docker-compose exec web python manage.py migrate
  ```
- _Собрать статику_
  ```
  docker-compose exec web python manage.py collectstatic --no-input
  ```
- _Выполните команды для переноса данных_
  ```
  docker-compose exec web python manage.py delete_contenttypes
  ```
  ```
  docker-compose exec web python manage.py loaddata static/dump.json
  ```

**Проект будет доступен по адресу http://127.0.0.1/**

### Автор: Герман Сизов