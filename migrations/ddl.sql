-- Таблица пользователей
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE users IS 'Таблица для хранения информации о пользователях';
COMMENT ON COLUMN users.user_id IS 'Уникальный идентификатор пользователя';
COMMENT ON COLUMN users.name IS 'Имя пользователя';
COMMENT ON COLUMN users.email IS 'Электронная почта пользователя';
COMMENT ON COLUMN users.first_seen IS 'Дата и время первой регистрации';

-- Таблица для авторизации сотрудников
CREATE TABLE workers_pass (
    worker_id SERIAL PRIMARY KEY,
    login VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

COMMENT ON TABLE workers_pass IS 'Данные для авторизации сотрудников';
COMMENT ON COLUMN workers_pass.worker_id IS 'Уникальный идентификатор сотрудника';
COMMENT ON COLUMN workers_pass.login IS 'Логин сотрудника';
COMMENT ON COLUMN workers_pass.password IS 'Пароль сотрудника';

-- Таблица сотрудников
CREATE TABLE workers (
    worker_id INT PRIMARY KEY REFERENCES workers_pass(worker_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(50) NOT NULL,
    hired_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE workers IS 'Данные о сотрудниках';
COMMENT ON COLUMN workers.worker_id IS 'Уникальный идентификатор сотрудника';
COMMENT ON COLUMN workers.name IS 'Имя сотрудника';
COMMENT ON COLUMN workers.position IS 'Должность сотрудника';
COMMENT ON COLUMN workers.hired_date IS 'Дата найма';

-- Таблица комнат
CREATE TABLE rooms (
    room_id SERIAL PRIMARY KEY,
    room_number INT UNIQUE NOT NULL,
    type VARCHAR(20) CHECK (status IN ('single', 'double', 'family')) DEFAULT 'single',
    price_per_night INT NOT NULL,
    status VARCHAR(20) CHECK (status IN ('available', 'maintenance')) DEFAULT 'available',
    description TEXT
);

COMMENT ON TABLE rooms IS 'Информация о комнатах';
COMMENT ON COLUMN rooms.room_id IS 'Уникальный идентификатор комнаты';
COMMENT ON COLUMN rooms.room_number IS 'Номер комнаты';
COMMENT ON COLUMN rooms.type IS 'Тип комнаты';
COMMENT ON COLUMN rooms.price_per_night IS 'Цена за ночь';
COMMENT ON COLUMN rooms.status IS 'Статус комнаты';
COMMENT ON COLUMN rooms.description IS 'Описание комнаты';

-- Таблица бронирований
CREATE TABLE bookings (
    booking_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    room_id INT REFERENCES rooms(room_id) ON DELETE SET NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status VARCHAR(20) CHECK (status IN ('confirmed', 'canceled', 'completed')) DEFAULT 'confirmed'
);

COMMENT ON TABLE bookings IS 'Данные о бронированиях';
COMMENT ON COLUMN bookings.booking_id IS 'Уникальный идентификатор бронирования';
COMMENT ON COLUMN bookings.user_id IS 'Идентификатор пользователя';
COMMENT ON COLUMN bookings.room_id IS 'Идентификатор комнаты';
COMMENT ON COLUMN bookings.check_in IS 'Дата заезда';
COMMENT ON COLUMN bookings.check_out IS 'Дата выезда';
COMMENT ON COLUMN bookings.status IS 'Статус бронирования';

-- Таблица логов
CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    worker_id INT REFERENCES workers(worker_id),
    action VARCHAR(100) NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE logs IS 'Логи изменений в системе';
COMMENT ON COLUMN logs.log_id IS 'Уникальный идентификатор лога';
COMMENT ON COLUMN logs.user_id IS 'Идентификатор пользователя';
COMMENT ON COLUMN logs.worker_id IS 'Идентификатор сотрудника';
COMMENT ON COLUMN logs.action IS 'Описание действия';
COMMENT ON COLUMN logs.date IS 'Дата и время действия';


--хранимая процедура для добавления нового сотрудника
CREATE OR REPLACE PROCEDURE add_new_user(
    name VARCHAR(100),
    login VARCHAR(100),
    "position" VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
DECLARE
    new_worker_id INT;
BEGIN
    INSERT INTO workers_pass (login, password)
    VALUES (login, '')
    RETURNING worker_id INTO new_worker_id;

    INSERT INTO workers (worker_id, name, "position")
    VALUES (new_worker_id, name, "position");
END;
$$;

--представление для вывода бронирования и данных о пользователе, который бронирует
CREATE OR REPLACE VIEW detailed_bookings AS
SELECT
    b.booking_id,
    b.user_id,
    u.name AS user_name,
    u.email AS user_email,
    b.room_id,
    b.check_in,
    b.check_out,
    b.status,
    (b.check_out - b.check_in) AS days_booked,
    COUNT(*) OVER (PARTITION BY b.user_id) AS total_bookings_per_user --оконная функция
FROM bookings b
LEFT JOIN users u ON b.user_id = u.user_id;




--LOGGING
-- Функция для записи в лог
CREATE OR REPLACE FUNCTION log_action()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, worker_id, action, date)
    VALUES (NEW.user_id, NULL, TG_ARGV[0], CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Функция для записи в лог с указанием действия работника
CREATE OR REPLACE FUNCTION log_action_worker()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs (user_id, worker_id, action, date)
    VALUES (NEW.user_id, NEW.worker_id, TG_ARGV[0], CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для добавления нового пользователя
CREATE or replace TRIGGER log_user_insert
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION log_action('New user added');

-- Триггер для обновления информации о пользователе
CREATE or replace TRIGGER log_user_update
AFTER UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION log_action('User info update');

-- Триггер для удаления пользователя
CREATE or replace TRIGGER log_user_delete
AFTER DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION log_action('User deleted');

-- Триггер для добавления нового бронирования
CREATE or replace TRIGGER log_booking_insert
AFTER INSERT ON bookings
FOR EACH ROW
EXECUTE FUNCTION log_action('New booking added');

-- Триггер для обновления статуса бронирования
CREATE or replace TRIGGER log_booking_update
AFTER UPDATE OF status ON bookings
FOR EACH ROW
EXECUTE FUNCTION log_action('Booking update');

-- Триггер для удаления бронирования
CREATE or replace TRIGGER log_booking_delete
AFTER DELETE ON bookings
FOR EACH ROW
EXECUTE FUNCTION log_action('Update deleted');
