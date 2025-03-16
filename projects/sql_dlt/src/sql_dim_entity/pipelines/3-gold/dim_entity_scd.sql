USE SCHEMA gold;

CREATE OR REFRESH STREAMING TABLE dim_entity_scd;
APPLY CHANGES INTO dim_entity_scd
FROM stream(lab.silver.user_level_pipeline_scd)
KEYS (user_id, jurisdiction)
APPLY AS DELETE WHEN _cdc_operation = "DELETE"
SEQUENCE BY _sequence
COLUMNS * EXCEPT (_ts_silver_started, _batch_id, _cdc_operation, _sequence)
STORED AS SCD TYPE 2;
