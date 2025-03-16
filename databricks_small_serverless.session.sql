


select * from information_schema.tables order by table_schema;

describe extended lab.gold.dim_entity_scd;
describe history lab.silver.withdrawal_pipeline


select * from LAB.silver.withdrawal_pipeline limit 100;

update LAB.silver.withdrawal_pipeline
set amount = 77
where id in (102230, 58591, 46262, 49973, 33135);

SELECT * FROM table_changes('LAB.silver.withdrawal_pipeline', 0);



describe history LAB.silver.withdrawal_pipeline limit 1


restore table LAB.silver.withdrawal_pipeline to version as of 5;


MERGE INTO LAB.silver.withdrawal_pipeline target
  USING LAB.silver.withdrawal_pipeline VERSION AS OF 5 source
  ON source.id = target.id AND 
  WHEN MATCHED THEN UPDATE SET *;



select * from LAB.silver.withdrawal_pipeline  where id = 16563

  select id, count(1) 
  from LAB.silver.withdrawal_pipeline 
  group by id
  having count(1) > 1
  order by count(1) desc
  



  select spark.databricks.delta.lastCommitVersionInSession

  describe TABLE EXTENDED LAB.silver.withdrawal_pipeline 