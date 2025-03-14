CREATE OR REPLACE FUNCTION lab.filters.even_filter(id float)
RETURN IF(current_user() = 'fake-email@fake.com', true, id % 2 = 0);