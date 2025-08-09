-- Индексы для таблицы бронирований
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings (date);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings (status);
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings (user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_date_status ON bookings (date, status);

-- Индекс для поиска свободных слотов
CREATE INDEX IF NOT EXISTS idx_bookings_date_time ON bookings (date, start_time, end_time);

-- Индексы для таблицы пользователей
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);

-- Индексы для таблицы настроек
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings (key);

-- Индексы для поиска по галерее
CREATE INDEX IF NOT EXISTS idx_gallery_category ON gallery_items (category);
CREATE INDEX IF NOT EXISTS idx_gallery_tags ON gallery_items USING GIN (tags);

-- Индекс для полнотекстового поиска
CREATE INDEX IF NOT EXISTS idx_bookings_search ON bookings 
USING GIN (to_tsvector('russian', coalesce(name, '') || ' ' || coalesce(phone, '') || ' ' || coalesce(notes, '')));

-- Индекс для временных диапазонов
CREATE INDEX IF NOT EXISTS idx_bookings_time_range ON bookings 
USING GIST (tsrange(start_time, end_time));
