
USE SCHEMA bronze;
CREATE OR REFRESH STREAMING TABLE deposit_pipeline
(
  date_partition DATE COMMENT 'The computed date to use as partition on the storage',
  ts_source_stream TIMESTAMP COMMENT 'Timestamp when the change was captured by the Flink CDC pipeline',
  ts_bronze_process_started TIMESTAMP COMMENT 'Timestamp when the bronze process started',
  batch_id STRING COMMENT 'Unique identifier for the ingestion batch',
  op STRING COMMENT 'Operation type (e.g., INSERT, UPDATE, DELETE) from the source system',
  transaction STRING COMMENT 'Unique transaction identifier from the source system',
  before MAP<STRING, STRING> COMMENT 'Pre-operation state of the transaction',
  after MAP<STRING, STRING> COMMENT 'Post-operation state of the transaction',
  source MAP<STRING, STRING> COMMENT 'Metadata about the ingestion process and source system',
  CONSTRAINT is_not_null EXPECT(date_partition is not null AND ts_source_stream is not null AND op is not null) ON VIOLATION FAIL UPDATE,
  CONSTRAINT has_valid_cdc_op EXPECT(op in ('r', 'c', 'u', 'd')) ON VIOLATION FAIL UPDATE
)
TBLPROPERTIES(
  'delta.feature.variantType-preview' = 'supported',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'tag.project' = 'lab',
  'tag.layer' = 'bronze'
  )
CLUSTER BY (date_partition, op)
 AS
SELECT 
  TO_DATE(ts) AS date_partition,
  CAST(ts AS TIMESTAMP) AS ts_source_stream,
  current_timestamp() AS ts_bronze_process_started,
  uuid() AS batch_id,
  op,    
  transaction,
  FROM_JSON(before, 'MAP<STRING, STRING>') AS before,
  FROM_JSON(after, 'MAP<STRING, STRING>') AS after,
  FROM_JSON(source, 'MAP<STRING, STRING>') AS source
FROM STREAM read_files(
    'abfss://lab@dlsdmvprd.dfs.core.windows.net/landing/deposit/**',
    format => 'json',
    schema => 'op STRING, ts STRING, transaction STRING, before STRING, after STRING, source STRING'
  );
