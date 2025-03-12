-- Define the bronze layer table for raw transaction data
CREATE OR REPLACE MATERIALIZED VIEW fct_transaction
(
  date_partition DATE                 COMMENT 'The computed date to use as partition on the storage',
  id FLOAT                           COMMENT 'Unique monotonicaly increasing primary key of deposit table',
  amount DECIMAL(38,18)               COMMENT 'The value deposited',
  user_id STRING                      COMMENT 'The Id of the user in the app',
  currency STRING                     COMMENT 'The currency string of the value deposited',
  ts_event TIMESTAMP                  COMMENT 'The time which the deposit happenned',
  tx_status STRING                    COMMENT 'The status of the transaction (complete, failed)',
  interface STRING                    COMMENT 'The place where the transaction was made',
  transaction_type STRING             COMMENT 'The type of the transaction (deposit, withdrawal)',
  
  CONSTRAINT is_not_null EXPECT(
      date_partition is not null 
      AND id is not null
      AND amount is not null
      AND user_id is not null
      AND currency is not null      
      AND ts_event is not null
      AND tx_status is not null
      AND transaction_type is not null
  ) ON VIOLATION FAIL UPDATE,
  CONSTRAINT has_valid_amount EXPECT(amount >= 0),
  CONSTRAINT has_valid_tx_status EXPECT (tx_status IN ('complete', 'failed'))
)
TBLPROPERTIES(
  'delta.feature.variantType-preview' = 'supported',
  'delta.enableChangeDataFeed' = 'true'
)
CLUSTER BY (date_partition, currency, transaction_type) 
AS
SELECT 
  date_partition,  
  id,
  amount,
  user_id,
  currency,
  ts_event,
  tx_status,
  NULL AS interface,
  'deposit' AS transaction_type
FROM lab.silver.deposit_pipeline
UNION ALL
SELECT 
  date_partition,  
  id,
  amount,
  user_id,
  currency,
  ts_event,
  tx_status,
  interface,
  'withdrawal' AS transaction_type
FROM lab.silver.withdrawal_pipeline
