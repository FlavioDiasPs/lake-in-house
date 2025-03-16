CREATE OR REPLACE FUNCTION lab.filters.currency_mask(currency string)
RETURN CASE WHEN current_user() = 'fake-email@fake.com' THEN currency ELSE '**** you cannot see this currency ****' END;