-- =============================================
-- PROCEDURES
-- =============================================
 
-- Вспомогательная функция: проверка формата телефона
-- Принимает: +7XXXXXXXXXX или 8XXXXXXXXXX
CREATE OR REPLACE FUNCTION is_valid_phone(phone TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN phone ~ '^\+7[0-9]{10}$'
        OR phone ~ '^8[0-9]{10}$';
END;
$$ LANGUAGE plpgsql;
 
 
-- 1. Вставить или обновить одного пользователя
CREATE OR REPLACE PROCEDURE upsert_user(
    p_name  VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
        UPDATE phonebook SET phone = p_phone WHERE name = p_name;
        RAISE NOTICE 'Обновлён телефон для "%"', p_name;
    ELSE
        INSERT INTO phonebook(name, phone) VALUES (p_name, p_phone);
        RAISE NOTICE 'Добавлен новый пользователь "%"', p_name;
    END IF;
END;
$$;
 
 
-- 2. Массовая вставка с валидацией телефонов
CREATE OR REPLACE PROCEDURE upsert_many_users(
    p_names  VARCHAR[],
    p_phones VARCHAR[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i       INT;
    v_name  VARCHAR;
    v_phone VARCHAR;
BEGIN
    -- Временная таблица для хранения некорректных записей
    CREATE TEMP TABLE IF NOT EXISTS invalid_entries(
        name   VARCHAR,
        phone  VARCHAR,
        reason TEXT
    ) ON COMMIT DELETE ROWS;
 
    DELETE FROM invalid_entries;
 
    FOR i IN 1 .. array_length(p_names, 1) LOOP
        v_name  := TRIM(p_names[i]);
        v_phone := TRIM(p_phones[i]);
 
        -- Проверка имени
        IF v_name IS NULL OR v_name = '' THEN
            INSERT INTO invalid_entries VALUES (v_name, v_phone, 'Пустое имя');
            CONTINUE;
        END IF;
 
        -- Проверка телефона
        IF NOT is_valid_phone(v_phone) THEN
            INSERT INTO invalid_entries VALUES (v_name, v_phone, 'Неверный формат телефона');
            CONTINUE;
        END IF;
 
        -- Вставка или обновление
        IF EXISTS (SELECT 1 FROM phonebook WHERE name = v_name) THEN
            UPDATE phonebook SET phone = v_phone WHERE name = v_name;
        ELSE
            INSERT INTO phonebook(name, phone) VALUES (v_name, v_phone);
        END IF;
 
    END LOOP;
END;
$$;
 
 
-- 3. Удаление по имени или телефону
CREATE OR REPLACE PROCEDURE delete_user(
    p_name  VARCHAR DEFAULT NULL,
    p_phone VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    rows_deleted INT;
BEGIN
    IF p_name IS NULL AND p_phone IS NULL THEN
        RAISE EXCEPTION 'Нужно указать хотя бы имя или телефон';
    END IF;
 
    DELETE FROM phonebook
    WHERE (p_name  IS NOT NULL AND name  = p_name)
       OR (p_phone IS NOT NULL AND phone = p_phone);
 
    GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    RAISE NOTICE 'Удалено строк: %', rows_deleted;
END;
$$;