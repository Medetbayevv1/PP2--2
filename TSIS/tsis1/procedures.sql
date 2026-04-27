CREATE OR REPLACE PROCEDURE add_phone(p_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM contacts WHERE name = p_name;
    IF v_id IS NULL THEN RAISE EXCEPTION 'Contact % not found', p_name; END IF;
    -- Skip silently if this exact phone already exists
    IF NOT EXISTS (SELECT 1 FROM phones WHERE contact_id = v_id AND phone = p_phone) THEN
        INSERT INTO phones (contact_id, phone, type) VALUES (v_id, p_phone, p_type);
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE move_to_group(p_name VARCHAR, p_group VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE v_gid INTEGER;
BEGIN
    INSERT INTO groups (name) VALUES (p_group) ON CONFLICT (name) DO NOTHING;
    SELECT id INTO v_gid FROM groups WHERE name = p_group;
    UPDATE contacts SET group_id = v_gid WHERE name = p_name;
END;
$$;

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(name VARCHAR, email VARCHAR, phone VARCHAR, grp VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT c.name, c.email, ph.phone, g.name
    FROM contacts c
    LEFT JOIN phones ph ON ph.contact_id = c.id
    LEFT JOIN groups g  ON g.id = c.group_id
    WHERE c.name  ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR ph.phone ILIKE '%' || p_query || '%';
END;
$$;