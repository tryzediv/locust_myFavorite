Как запустить тест
locust -f test.py

После этого перейдите по адресу:
http://localhost:8089

Настройки в интерфейсе
Number of users to simulate : например, 100
Spawn rate (users spawned/second) : например, 10
Host: https://petstore.swagger.io
Нажмите Start swarming , чтобы начать нагрузку.

Что вы увидите после запуска
В веб-интерфейсе будут отображаться метрики:

Average Response Time — среднее время отклика
Requests per second — количество запросов в секунду
Failures — процент ошибок
Графики: latency, requests, failures, RPS и др.
Данные по каждому типу запроса отдельно
