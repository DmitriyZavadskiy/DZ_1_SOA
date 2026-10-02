# C4 — Container diagram

Уровень C4 Container: маркетплейс как система, его контейнеры (сервисы и их хранилища), внешние системы и пользователи. Нотация C4: у каждого элемента указан тип (`[Person]`, `[Container: технология]`, `[External System]`), у каждой связи — назначение и протокол. Сплошные стрелки — синхронные вызовы, пунктирная — асинхронное событие через Kafka (технология указана на стрелке).

Детали владения данными, распределения доменов и обоснование решений — в [README](../README.md).

Если диаграмма не отрендерилась — [PNG-версия](c4-container.png).

```mermaid
%%{init: {"theme": "base", "flowchart": {"curve": "linear", "nodeSpacing": 40, "rankSpacing": 70}, "themeVariables": {"lineColor": "#6b4f2a", "edgeLabelBackground": "#fffbe6", "primaryTextColor": "#3b2a14", "fontSize": "14px"}}}%%
flowchart LR
    buyer["<b>Покупатель</b><br/>[Person]<br/>Покупает товары"]
    seller["<b>Продавец</b><br/>[Person]<br/>Продаёт товары"]

    subgraph marketplace["<b>Marketplace</b> [Software System]"]
        direction LR
        web["<b>Web / Mobile App</b><br/>[Container: SPA, iOS, Android]<br/>Интерфейс"]
        gateway["<b>API Gateway</b><br/>[Container: nginx]<br/>Вход, проверка токена, маршрутизация"]

        users["<b>Users Service</b><br/>[Container: Python, FastAPI]<br/>Аккаунты, роли, вход"]
        users_db[("<b>Users DB</b><br/>[Container: PostgreSQL]")]

        catalog["<b>Catalog Service</b><br/>[Container: Python, FastAPI]<br/>Товары, цены, остатки, лента"]
        catalog_db[("<b>Catalog DB</b><br/>[Container: PostgreSQL]")]

        orders["<b>Orders Service</b><br/>[Container: Python, FastAPI]<br/>Корзина, заказы, статусы, уведомления"]
        orders_db[("<b>Orders DB</b><br/>[Container: PostgreSQL]")]

        payments["<b>Payments Service</b><br/>[Container: Python, FastAPI]<br/>Расчёт и учёт платежей"]
        payments_db[("<b>Payments DB</b><br/>[Container: PostgreSQL]")]
    end

    psp["<b>Платёжный провайдер</b><br/>[External System]"]
    messaging["<b>Email / Push провайдер</b><br/>[External System]"]

    buyer -->|"HTTPS"| web
    seller -->|"HTTPS"| web
    web -->|"API [HTTPS/JSON]"| gateway

    gateway -->|"вход, профиль [gRPC, sync]"| users
    gateway -->|"каталог, лента [gRPC, sync]"| catalog
    gateway -->|"корзина, заказы [gRPC, sync]"| orders

    orders -->|"проверка товара и цены [gRPC, sync]"| catalog
    orders -->|"создать платёж [gRPC, sync]"| payments
    payments -.->|"PaymentSucceeded / Failed [Kafka, async]"| orders

    payments -->|"провести платёж [HTTPS]"| psp
    orders -->|"уведомить о статусе [HTTPS]"| messaging

    users --- users_db
    catalog --- catalog_db
    orders --- orders_db
    payments --- payments_db

    classDef person fill:#6b4f2a,stroke:#4a3519,color:#ffffff
    classDef container fill:#fff3c4,stroke:#a67c3d,color:#3b2a14
    classDef db fill:#f7e3b0,stroke:#a67c3d,color:#3b2a14
    classDef ext fill:#e9dfcf,stroke:#8c7355,color:#3b2a14
    class buyer,seller person
    class web,gateway,users,catalog,orders,payments container
    class users_db,catalog_db,orders_db,payments_db db
    class psp,messaging ext
    style marketplace fill:#fffdf5,stroke:#8c6a3d,stroke-dasharray:6 4,color:#3b2a14
```

## Легенда

| Элемент | Что означает |
|---|---|
| Тёмно-коричневый блок, `[Person]` | Пользователь системы |
| Пунктирная рамка, `[Software System]` | Граница маркетплейса |
| Жёлтый блок, `[Container: …]` | Отдельно развёртываемая единица: сервис или приложение |
| Жёлтый цилиндр, `[Container: PostgreSQL]` | База данных, принадлежащая ровно одному сервису |
| Бежевый блок, `[External System]` | Внешняя система, которой мы не владеем |
| `→` сплошная, `[gRPC, sync]` | Синхронный запрос-ответ |
| `⇢` пунктирная, `[Kafka, async]` | Событие через Kafka |
