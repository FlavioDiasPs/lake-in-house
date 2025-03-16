USE SCHEMA silver;
CREATE OR REFRESH STREAMING TABLE user_level_pipeline_scd
(
  _ts_silver_started TIMESTAMP        COMMENT 'Timestamp when the bronze process started',
  _batch_id STRING                    COMMENT 'Unique identifier for the ingestion batch',
  _cdc_operation STRING               COMMENT 'Operation type (e.g., INSERT, UPDATE, DELETE) from the source system',
  _sequence BIGINT                    COMMENT 'Sequence number from Postgres Wal to give us event ordering',
  date_partition DATE                 COMMENT 'The computed date to use as partition on the storage',
  user_id STRING                      COMMENT 'The Id of the user in the app',
  level INT                           COMMENT 'The currency string of the value deposited',
  jurisdiction STRING                 COMMENT 'The jurisdiction in which this level of permission applies',
  ts_event TIMESTAMP                  COMMENT 'The time which the level was granted',
  
  CONSTRAINT is_not_null EXPECT(
      _ts_silver_started is not null
      AND _batch_id is not null
      AND _cdc_operation is not null
      AND _sequence is not null
      AND date_partition is not null 
      AND user_id is not null
      AND level is not null      
      AND jurisdiction is not null
      AND ts_event is not null
  ) ON VIOLATION FAIL UPDATE,
  
  CONSTRAINT has_valid_cdc_operation_type EXPECT(_cdc_operation in ('INSERT', 'UPDATE', 'DELETE')) ON VIOLATION FAIL UPDATE
)
TBLPROPERTIES(
  'delta.feature.variantType-preview' = 'supported',
  'delta.enableChangeDataFeed' = 'true',  
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'tag.project' = 'lab',
  'tag.layer' = 'silver'
)
CLUSTER BY (date_partition, _cdc_operation) 
AS
SELECT 
    current_timestamp() AS _ts_silver_started,
    uuid() AS _batch_id,
    *
FROM 
(
  SELECT DISTINCT
      CASE 
          WHEN op IN ('c', 'r') THEN 'INSERT'
          WHEN op IN ('d') THEN 'DELETE'
          WHEN op IN ('u') THEN 'UPDATE' 
          ELSE op END AS _cdc_operation,
      CAST(source['lsn'] AS BIGINT) AS _sequence,
      date_partition,      
      CAST(after['user_id'] AS STRING) AS user_id,
      CAST(after['level'] AS INT) AS level,
      CAST(after['jurisdiction'] AS STRING) AS jurisdiction,
      CAST(after['event_timestamp'] AS TIMESTAMP) AS ts_event
  FROM STREAM(lab.bronze.user_level_pipeline_scd)
);