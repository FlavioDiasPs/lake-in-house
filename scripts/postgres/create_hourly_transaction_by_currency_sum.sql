CREATE TABLE crypto.hourly_transaction_by_currency_sum (
 	window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    currency TEXT, 
    transaction_type TEXT,
    hour_sum_amount DECIMAL(38, 18),
	CONSTRAINT pkey_hourly_transaction_by_currency_sum PRIMARY KEY(window_start, window_end, transaction_type, currency)
)