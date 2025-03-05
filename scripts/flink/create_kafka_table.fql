CREATE TABLE deposit_sample_data (
    id INT,
    event_timestamp TIMESTAMP(3),
    user_id STRING,
    amount DOUBLE,
    currency STRING,
    tx_status STRING,
    op STRING,  -- Operation type (insert, update, delete)
    before_id INT,  -- ID before the change (for update or delete)
    before_event_timestamp TIMESTAMP(3),  -- Before state timestamp
    before_user_id STRING,  -- Before state user_id
    before_amount DOUBLE,  -- Before state amount
    before_currency STRING,  -- Before state currency
    before_tx_status STRING  -- Before state transaction status
) WITH (
    'connector' = 'kafka',  -- Kafka connector for reading CDC data
    'topic' = 'dbserver1.public.deposit_sample_data',  -- Kafka topic where Debezium publishes data
    'properties.bootstrap.servers' = 'kafka:9092',  -- Kafka broker address
    'format' = 'json',  -- Assuming JSON format for Debezium messages
    'scan.startup.mode' = 'earliest-offset'  -- Start reading from the earliest available offset
);
