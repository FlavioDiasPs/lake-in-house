-- Define the bronze layer table for raw transaction data
CREATE OR REPLACE STREAMING TABLE lab.silver.deposit
(
  date_partition DATE                 COMMENT 'The computed date to use as partition on the storage',
  ts_silver_process_started TIMESTAMP COMMENT 'Timestamp when the bronze process started',
  batch_id STRING                     COMMENT 'Unique identifier for the ingestion batch',
  operation_type STRING               COMMENT 'Operation type (e.g., INSERT, UPDATE, DELETE) from the source system',
  id  FLOAT                           COMMENT 'Unique monotonicaly increasing primary key of deposit table',
  amount DECIMAL(38,18)               COMMENT 'The value deposited',
  user_id STRING                      COMMENT 'The Id of the user in the app',
  currency STRING                     COMMENT 'The currency string of the value deposited',
  ts_event TIMESTAMP                  COMMENT 'The time which the deposit happenned',
  tx_status STRING                    COMMENT 'The status of the transaction (complete, failed)',
  
  CONSTRAINT is_not_null EXPECT(
      date_partition is not null 
      AND ts_silver_process_started is not null
      AND batch_id is not null
      AND operation_type is not null
      AND id is not null
      AND amount is not null
      AND user_id is not null
      AND currency is not null      
      AND event_timestamp is not null
      AND tx_status is not null
  ) ON VIOLATION FAIL UPDATE,
  CONSTRAINT has_valid_amount EXPECT(amount >= 0),
  CONSTRAINT has_valid_cdc_operation_type EXPECT(operation_type in ('INSERT', 'UPDATE', 'DELETE')),
  CONSTRAINT has_valid_tx_status EXPECT (tx_status IN ('complete', 'failed'))
)
TBLPROPERTIES(
  'delta.feature.variantType-preview' = 'supported',
  'delta.enableChangeDataFeed' = 'true'
)
CLUSTER BY (date_partition, op) 
AS
SELECT 
  date_partition,  
  current_timestamp() AS ts_silver_process_started,
  uuid() AS batch_id,
  CASE 
    WHEN op IN ('c', 'r') THEN 'INSERT'
    WHEN op IN ('d') THEN 'DELETE'
    WHEN op IN ('u') THEN 'UPDATE' 
    ELSE op END AS operation_type,
  after:id::float AS id,
  after:amount::DECIMAL(38, 18) AS amount,
  after:user_id::STRING AS user_id,
  after:currency::STRING AS currency,
  after:event_timestamp::TIMESTAMP AS ts_event,
  after:tx_status::STRING AS tx_status
FROM lab.bronze.deposit
