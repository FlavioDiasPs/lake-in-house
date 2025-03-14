USE SCHEMA GOLD;

CREATE OR REFRESH MATERIALIZED VIEW vw_fct_transaction_pipeline
(
  date_partition DATE                                 COMMENT 'The computed date to use as partition on the storage',
  id FLOAT                                            COMMENT 'Unique monotonicaly increasing primary key of deposit table',
  amount DECIMAL(38,18)                               COMMENT 'The value deposited',
  user_id STRING                                      COMMENT 'The Id of the user in the app',
  currency STRING MASK lab.filters.currency_mask      COMMENT 'The currency string of the value deposited', --column mask https://docs.databricks.com/aws/en/tables/row-and-column-filters
  ts_event TIMESTAMP                                  COMMENT 'The time which the deposit happenned',
  tx_status STRING                                    COMMENT 'The status of the transaction (complete, failed)',
  interface STRING                                    COMMENT 'The place where the transaction was made',
  transaction_type STRING                             COMMENT 'The type of the transaction (deposit, withdrawal)'
)
TBLPROPERTIES('pipelines.channel' = 'PREVIEW')
WITH ROW FILTER lab.filters.even_filter on (id) --row filter https://docs.databricks.com/aws/en/tables/row-and-column-filters
AS
SELECT 
  date_partition,
  id,
  amount,
  CASE WHEN is_account_group_member('invented_group') 
        THEN user_id ELSE 'REDACTED' 
    END AS user_id, --dynamic view https://learn.microsoft.com/en-us/azure/databricks/views/dynamic
  currency,
  ts_event,
  tx_status,
  interface,
  transaction_type
FROM lab.gold.fct_transaction_pipeline



