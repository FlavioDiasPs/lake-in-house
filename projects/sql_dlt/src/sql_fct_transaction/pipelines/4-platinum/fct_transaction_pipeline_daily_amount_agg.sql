USE SCHEMA GOLD;

CREATE OR REPLACE MATERIALIZED VIEW fct_transaction_pipeline_monthly_amount_agg
(
  date_partition DATE                                 COMMENT 'The computed date to use as partition on the storage',
  amount_sum DECIMAL(38,18)                           COMMENT 'The value deposited',
  user_id STRING                                      COMMENT 'The Id of the user in the app',
  currency STRING MASK lab.filters.currency_mask      COMMENT 'The currency string of the value deposited',  
  transaction_type STRING                             COMMENT 'The type of the transaction (deposit, withdrawal)'
)
AS
SELECT 
  date_partition,
  sum(amount) AS amount_sum,
  user_id,
  currency,
  transaction_type
FROM lab.gold.fct_transaction_pipeline
WHERE tx_status = 'complete' --and date_add(date_partition, -1) removed because this is a simulation and I don't have yesterday data
GROUP BY date_partition, user_id, currency, transaction_type
