-- 3.4.1 Add phone to contact
CREATE OR REPLACE PROCEDURE add_phone(p_name VARCHAR, p_phone VARCHAR, p_type VARCHAR DEFAULT 'mobile')
LANGUAGE plpgsql AS $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM contacts WHERE name ILIKE p_name LIMIT 1;
    IF NOT FOUND THEN RAISE EXCEPTION 'Contact "%" not found', p_name; END IF;
    INSERT INTO phones(contact_id, phone, type) VALUES (v_id, p_phone, p_type);
END; $$;


-- 3.4.2 Move contact to group (creates group if missing)
CREATE OR REPLACE PROCEDURE move_to_group(p_name VARCHAR, p_group VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE v_cid INTEGER; v_gid INTEGER;
BEGIN
    SELECT id INTO v_cid FROM contacts WHERE name ILIKE p_name LIMIT 1;
    IF NOT FOUND THEN RAISE EXCEPTION 'Contact "%" not found', p_name; END IF;
    INSERT INTO groups(name) VALUES (p_group) ON CONFLICT (name) DO NOTHING;
    SELECT id INTO v_gid FROM groups WHERE name ILIKE p_group;
    UPDATE contacts SET group_id = v_gid WHERE id = v_cid;
END; $$;


-- 3.4.3 Search by name, email, or any phone
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(id INT, name VARCHAR, email VARCHAR, birthday DATE, group_name TEXT, phones TEXT)
LANGUAGE sql AS $$
    SELECT
        c.id, c.name, c.email, c.birthday,
        g.name,
        STRING_AGG(p.phone || ' (' || p.type || ')', ', ')
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.name  ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR EXISTS (SELECT 1 FROM phones WHERE contact_id = c.id AND phone ILIKE '%' || p_query || '%')
    GROUP BY c.id, c.name, c.email, c.birthday, g.name
    ORDER BY c.name;
$$;
