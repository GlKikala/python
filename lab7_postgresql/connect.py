CREATE OR REPLACE FUNCTION search_phonebook(pattern TEXT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT pb.id, pb.name, pb.phone
        FROM phonebook pb
        WHERE pb.name  ILIKE '%' || pattern || '%'
           OR pb.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION get_phonebook_page(
    page_size   INT DEFAULT 5,
    page_number INT DEFAULT 1
)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT pb.id, pb.name, pb.phone
        FROM phonebook pb
        ORDER BY pb.id
        LIMIT  page_size
        OFFSET (page_number - 1) * page_size;
END;
$$ LANGUAGE plpgsql;
