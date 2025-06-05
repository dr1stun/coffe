-- Удаляем представление популярных напитков, если оно уже есть
DROP VIEW IF EXISTS most_popular_products;

-- Удаляем все таблицы (в правильном порядке, чтобы избежать конфликтов зависимостей)
DROP TABLE IF EXISTS 
    order_status_logs,       -- лог смены статусов заказов
    statistics,              -- статистика по напиткам
    reviews,                 -- отзывы пользователей
    user_preferences,        -- вкусовые предпочтения пользователей
    product_descriptors,     -- дескрипторы вкуса напитков
    order_items,             -- позиции в заказе
    sold_out,                -- список временно недоступных товаров
    stop_list,               -- временно недоступные ингредиенты
    product_ingredients,     -- состав напитков
    ingredients,             -- ингредиенты
    products,                -- напитки и еда
    orders,                  -- заказы
    users                    -- пользователи
CASCADE;                     -- автоматически удаляет зависимые объекты

CREATE TABLE users (
    id SERIAL PRIMARY KEY,                             -- Уникальный ID пользователя
    name VARCHAR(100),                                 -- Имя пользователя
    email VARCHAR(100) UNIQUE,                         -- Email (для авторизации)
    password_hash TEXT,                                -- Пароль в зашифрованном виде
    role VARCHAR(20) CHECK (role IN                    -- Роль: гость, бариста, администратор
        ('гость', 'бариста', 'администратор')) NOT NULL,
    order_count INT DEFAULT 0,                         -- Сколько заказов оформлено
    guest_discount NUMERIC(4,2) DEFAULT 0              -- Скидка (%) для гостей, зависит от количества заказов
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,                             -- Уникальный ID заказа
    user_id INT REFERENCES users(id),                  -- Кто сделал заказ (внешний ключ)
    status VARCHAR(50) DEFAULT 'Новый',                -- Статус заказа: Новый → В работе → Готов
    discount_applied BOOLEAN DEFAULT FALSE,            -- Была ли применена скидка
    total_price NUMERIC(10,2),                         -- Общая стоимость до скидки
    final_price NUMERIC(10,2),                         -- Итоговая сумма с учётом скидки
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP     -- Время оформления заказа
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,                             -- ID продукта
    name VARCHAR(100) NOT NULL,                        -- Название напитка/еды
    category VARCHAR(50),                              -- Категория (фильтр, десерт и т.д.)
    price NUMERIC(8,2) NOT NULL,                       -- Цена
    available BOOLEAN DEFAULT TRUE                     -- Флаг: доступен ли в меню
);

CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,                             -- ID ингредиента
    name VARCHAR(100) NOT NULL                         -- Название (молоко, сироп и т.п.)
);

CREATE TABLE product_ingredients (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE, -- Какому напитку принадлежит
    ingredient_id INT REFERENCES ingredients(id),             -- Какой ингредиент
    amount VARCHAR(50)                                        -- Количество (например, "30 мл")
);

CREATE TABLE stop_list (
    id SERIAL PRIMARY KEY,
    ingredient_id INT REFERENCES ingredients(id) ON DELETE CASCADE, -- Какой ингредиент временно недоступен
    created_by INT REFERENCES users(id),                            -- Кто добавил (бариста/админ)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                  -- Когда добавлен в стоп
);

CREATE TABLE sold_out (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),                     -- Какой продукт недоступен
    reason TEXT DEFAULT 'Отсутствует ингредиент',               -- Причина (например, ингредиент в стопе)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP              -- Когда помечен как раскупленный
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE,       -- Ссылка на заказ
    product_id INT REFERENCES products(id),                     -- Какой продукт
    quantity INT NOT NULL,                                      -- Количество
    unit_price NUMERIC(8,2) NOT NULL,                           -- Цена за штуку
    total_price NUMERIC(10,2) GENERATED ALWAYS                  -- Общая сумма позиции
        AS (unit_price * quantity) STORED
);

CREATE TABLE product_descriptors (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id) ON DELETE CASCADE,   -- К какому продукту относится
    descriptor VARCHAR(50)                                      -- Дескриптор вкуса (ягодный, фильтр, цитрусовый и т.п.)
);


CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),                           -- Кто пользователь
    descriptor VARCHAR(50),                                     -- Какой вкус предпочитает
    weight INT DEFAULT 1                                        -- Вес (чем выше — тем сильнее предпочтение)
);


CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),                           -- Кто оставил отзыв
    product_id INT REFERENCES products(id),                     -- На что отзыв
    rating INT CHECK (rating BETWEEN 1 AND 5),                  -- Оценка от 1 до 5
    comment TEXT,                                               -- Комментарий
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP              -- Когда оставлен
);

CREATE TABLE statistics (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),                     -- Напиток
    times_ordered INT DEFAULT 0                                 -- Сколько раз заказан
);

CREATE TABLE order_status_logs (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id) ON DELETE CASCADE,       -- Какой заказ
    old_status VARCHAR(50),                                     -- Был статус
    new_status VARCHAR(50),                                     -- Стал статус
    changed_by INT REFERENCES users(id),                        -- Кто изменил (обычно бариста)
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP              -- Когда изменили
);

CREATE VIEW most_popular_products AS
SELECT
    p.id,
    p.name,
    p.category,
    SUM(oi.quantity) AS total_ordered                          -- Сумма заказов
FROM
    products p
JOIN
    order_items oi ON p.id = oi.product_id
GROUP BY
    p.id, p.name, p.category
ORDER BY
    total_ordered DESC;

