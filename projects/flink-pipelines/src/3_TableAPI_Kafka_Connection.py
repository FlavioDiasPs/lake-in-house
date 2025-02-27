from pyflink.table import EnvironmentSettings, TableEnvironment

# Set up the Table API environment
env_settings = EnvironmentSettings.in_streaming_mode()
table_env = TableEnvironment.create(env_settings)


# Define source table (Kafka)
table_env.execute_sql("""
    CREATE TABLE kafka_source (
        id INT,
        event_timestamp TIMESTAMP(3),
        user_id STRING,1
        currency STRING,
        tx_status STRING
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'transactions',
        'properties.bootstrap.servers' = 'kafka:9092',
        'format' = 'json',
        'scan.startup.mode' = 'earliest-offset'
    )
""")

# Define sink table (Print to console for debugging)
table_env.execute_sql("""
    CREATE TABLE print_sink (
        id INT,
        user_id STRING,
        amount DOUBLE
    ) WITH (
        'connector' = 'print'
    )
""")

# Insert data into sink
table_env.execute_sql("""
    INSERT INTO print_sink
    SELECT id, user_id, amount FROM kafka_source
""")

# Execute the Flink job
# env.execute("Flink SQL Kafka Job")
