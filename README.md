# Yatube

[![CI](https://github.com/8ubble8uddy/yatube-project/workflows/yatube-project/badge.svg
)](https://github.com/8ubble8uddy/yatube-project/actions/workflows/yatube_workflow.yml)

<kbd><img width="400" src="https://user-images.githubusercontent.com/83628490/171292538-896aa056-7d66-449c-93e3-1943a693ed4a.png"></kbd>
<kbd><img width="400" src="https://user-images.githubusercontent.com/83628490/171292269-365e7bc4-3886-4056-ba84-62c8d99f757f.png"></kbd>

### **Описание**

_[yatube-project](https://github.com/8ubble8uddy/yatube-project) - это социальная сеть для публикации личных дневников и API для неё. На этом сервисе пользователи могут создать свою страницу. Если на нее зайти, то можно посмотреть все записи автора. Пользователи могут заходить на чужие страницы, подписываться на авторов и комментировать их записи. Также записи можно отправить в сообщество и посмотреть там записи разных авторов._

### **Технологии**

```Python``` ```Django``` ```SQLite``` ```pytest``` ```unittest``` ```Docker``` ```Gunicorn``` ```nginx```

### **Как запустить проект:**

Клонировать репозиторий и перейти внутри него в директорию ```infra/```:
```
git clone https://github.com/8ubble8uddy/yatube-project.git
```
```sh
cd yatube-project/infra/
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
