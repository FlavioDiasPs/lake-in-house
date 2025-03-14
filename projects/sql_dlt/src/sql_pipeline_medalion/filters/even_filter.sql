USE CATALOG LAB;
USE SCHEMA GOLD;

CREATE OR REPLACE FUNCTION even_filter(id float)
RETURN IF(current_user() = 'flavio.silva@clear.sale', true, id % 2 = 0);