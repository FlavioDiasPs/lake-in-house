USE SCHEMA GOLD;

CREATE OR REFRESH MATERIALIZED VIEW vw_fct_transaction_pipeline
TBLPROPERTIES(pipelines.channel = "PREVIEW")
WITH ROW FILTER lab.filters.even_filter on (id)
AS
SELECT 
  date_partition,  
  id,
  amount,
  CASE WHEN is_account_group_member('invented_group') 
        THEN user_id ELSE 'REDACTED' 
    END AS user_id,
  currency,
  ts_event,
  tx_status,
  interface,
  transaction_type
FROM lab.gold.fct_transaction_pipeline



