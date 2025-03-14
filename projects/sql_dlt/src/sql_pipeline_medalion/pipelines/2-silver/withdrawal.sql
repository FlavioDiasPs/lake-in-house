USE SCHEMA silver;
CREATE OR REFRESH STREAMING TABLE withdrawal_pipeline
(
  date_partition DATE                     COMMENT 'The computed date to use as partition on the storage',
  ts_silver_process_started TIMESTAMP     COMMENT 'Timestamp when the bronze process started',
  batch_id STRING                         COMMENT 'Unique identifier for the silver ingestion batch',
  operation_type STRING                   COMMENT 'Operation type (e.g., INSERT, UPDATE, DELETE) from the source system',
  id FLOAT                                COMMENT 'Unique monotonicaly increasing primary key of withdrawal table',
  amount DECIMAL(38, 18)                  COMMENT 'The value withdrawn',
  user_id STRING                          COMMENT 'The Id of the user in the app',
  interface STRING                        COMMENT 'The place where the transaction was made',
  currency STRING                         COMMENT 'The currency string of the value deposited',
  ts_event TIMESTAMP                      COMMENT 'The time which the deposit happenned',
  tx_status STRING                        COMMENT 'The status of the transaction (complete, failed)',

  CONSTRAINT is_not_null EXPECT(
    date_partition is not null 
    AND ts_silver_process_started is not null 
    AND batch_id is not null
    AND operation_type is not null
    AND id is not null
    AND amount is not null
    AND user_id is not null
    AND interface is not null
    AND currency is not null
    AND ts_event is not null
    AND tx_status is not null
  ) ON VIOLATION FAIL UPDATE,
  CONSTRAINT has_valid_amount EXPECT(amount >= 0) ON VIOLATION DROP ROW,
  CONSTRAINT has_valid_cdc_operation_type EXPECT(operation_type in ('INSERT', 'UPDATE', 'DELETE')) ON VIOLATION FAIL UPDATE,
  CONSTRAINT has_valid_interface EXPECT (interface IN ('app', 'web')) ON VIOLATION FAIL UPDATE,
  CONSTRAINT has_valid_tx_status EXPECT (tx_status IN ('complete', 'failed')) ON VIOLATION FAIL UPDATE
)
TBLPROPERTIES(
  'delta.feature.variantType-preview' = 'supported',
  'delta.enableChangeDataFeed' = 'true',  
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'tag.project' = 'lab',
  'tag.layer' = 'silver'
)
CLUSTER BY (date_partition, operation_type)
AS
SELECT 
  current_timestamp() AS ts_silver_process_started,
  uuid() AS batch_id,
  *
FROM (
  SELECT DISTINCT
    date_partition,    
    CASE 
      WHEN op IN ('c', 'r') THEN 'INSERT'
      WHEN op IN ('d') THEN 'DELETE'
      WHEN op IN ('u') THEN 'UPDATE' 
      ELSE op END AS operation_type,
    CAST(after['id'] AS float) AS id,    
    CAST(after['amount'] AS DECIMAL(38, 18)) AS amount,
    CAST(after['user_id'] AS STRING) AS user_id,
    CAST(after['interface'] AS STRING) AS interface,
    CAST(after['currency'] AS STRING) AS currency,
    CAST(after['event_timestamp'] AS TIMESTAMP) AS ts_event,
    CAST(after['tx_status'] AS STRING) AS tx_status
  FROM STREAM(lab.bronze.withdrawal_pipeline)
);
