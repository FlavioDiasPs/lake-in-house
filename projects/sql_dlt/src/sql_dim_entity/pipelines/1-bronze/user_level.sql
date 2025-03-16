USE SCHEMA bronze;
CREATE OR REFRESH STREAMING TABLE user_level_pipeline_scd
(
  _ts_bronze_started TIMESTAMP          COMMENT 'Timestamp when the bronze process started',
  _batch_id STRING                      COMMENT 'Unique identifier for the ingestion batch',
  date_partition DATE                   COMMENT 'The computed date to use as partition on the storage',
  ts_source_stream TIMESTAMP            COMMENT 'Timestamp when the change was captured by the Flink CDC pipeline',
  op STRING                             COMMENT 'Operation type (e.g., INSERT, UPDATE, DELETE) from the source system',
  transaction STRING                    COMMENT 'Unique transaction identifier from the source system',
  before MAP<STRING, STRING>            COMMENT 'Pre-operation state of the transaction',
  after MAP<STRING, STRING>             COMMENT 'Post-operation state of the transaction',
  source MAP<STRING, STRING>            COMMENT 'Metadata about the ingestion process and source system',

  CONSTRAINT is_not_null EXPECT (
        date_partition is not null 
        AND ts_source_stream is not null 
        AND op is not null
    ) ON VIOLATION FAIL UPDATE,
  CONSTRAINT has_valid_cdc_op EXPECT(op in ('r', 'c', 'u', 'd')) ON VIOLATION FAIL UPDATE
)
TBLPROPERTIES(
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'tag.project' = 'lab',
  'tag.layer' = 'bronze'
)
CLUSTER BY (date_partition, op)
 AS
SELECT 
  current_timestamp() AS _ts_bronze_started,
  uuid() AS _batch_id,
  TO_DATE(ts) AS date_partition,
  CAST(ts AS TIMESTAMP) AS ts_source_stream,
  op,    
  transaction,
  FROM_JSON(before, 'MAP<STRING, STRING>') AS before,
  FROM_JSON(after, 'MAP<STRING, STRING>') AS after,
  FROM_JSON(source, 'MAP<STRING, STRING>') AS source
FROM STREAM read_files(
    'abfss://lab@dlsdmvprd.dfs.core.windows.net/landing/user_level/**',
    format => 'json',
    schema => 'op STRING, ts STRING, transaction STRING, before STRING, after STRING, source STRING'
  );

  