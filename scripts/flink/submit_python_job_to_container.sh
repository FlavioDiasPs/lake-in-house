docker cp projects\\flink-pipelines\\src\\deposit_pipeline.py flink-jobmanager:opt/flink/deposit_pipeline.py
docker cp projects\\flink-pipelines\\src\\fql\\deposit_cdc_queries.fql flink-jobmanager:opt/flink/fql/deposit_cdc_queries.fql
docker cp projects\flink-pipelines\src\jars\flink-sql-connector-kafka-1.17.2.jar flink-jobmanager:opt/flink/lib/
docker cp projects\flink-pipelines\src\jars\flink-sql-connector-kafka-1.17.2.jar flink-taskmanager:opt/flink/lib/
docker restart flink-jobmanager flink-taskmanager
docker exec flink-jobmanager flink run -py app/deposit_pipeline.py