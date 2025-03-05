from pyflink.table import EnvironmentSettings, TableEnvironment
from sqlalchemy import create_engine, text
import os

os.environ["FLINK_ENV_JAVA_OPTS"] = (
    "--add-opens java.base/java.util=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/java.io=ALL-UNNAMED"
)


engine = create_engine("postgresql://postgres:postgres@host.docker.internal:5432/postgres")
with engine.connect() as conn:
    conn.execute(
        text("""
            CREATE TABLE IF NOT EXISTS flink_aggregated_deposits (
                window_end TIMESTAMP(3),
                currency TEXT,
                avg_amount NUMERIC(38,18)
            );
        """)
    )
    conn.commit()


# Create Table Environment (pure Table API, no DataStream API)
env_settings = EnvironmentSettings.in_streaming_mode()
table_env = TableEnvironment.create(env_settings)
table_env.get_config().get_configuration().set_string("table.exec.source.idle-timeout", "1000")

print("Starting")

# Define source table (Kafka)
table_env.execute_sql("""
    CREATE TABLE kafka_source_raw (
        before MAP<STRING, STRING>,
        after ROW<
                id INT,
                event_timestamp STRING,
                user_id STRING,
                currency STRING,
                amount DECIMAL(38, 18)>,
        source MAP<STRING, STRING>,
        op STRING,
        ts_ms BIGINT,
        transaction MAP<STRING, STRING>,
        computed_event_timestamp AS TO_TIMESTAMP(REGEXP_REPLACE(after.event_timestamp, '\\+00$', ''), 'yyyy-MM-dd HH:mm:ss.SSS'),
        WATERMARK FOR computed_event_timestamp AS computed_event_timestamp - INTERVAL '0.1' SECONDS
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'dbserver1.public.deposit_sample_data',
        'properties.bootstrap.servers' = 'localhost:9092',
        'format' = 'json',
        'scan.startup.mode' = 'earliest-offset'
    );
""")
print("kafka_source_raw")

table_env.execute_sql("""
        CREATE TABLE kafka_source_halfway (
            window_end TIMESTAMP(3),
            currency STRING,
            avg_amount DECIMAL(38, 18)
        ) WITH (
            'connector' = 'print'
        );
""")
print("kafka_source_halfway")


table_env.execute_sql("""
    CREATE TABLE postgres_sink (
        window_end TIMESTAMP(3),
        currency STRING,
        avg_amount DECIMAL(38, 18)
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://localhost:5432/postgres',
        'table-name' = 'flink_aggregated_deposits',
        'username' = 'postgres',
        'password' = 'postgres',
        'driver' = 'org.postgresql.Driver'
    );
""")
print("postgres_sink")

table_env.execute_sql("""
    INSERT INTO postgres_sink
    SELECT
        TUMBLE_END(computed_event_timestamp, INTERVAL '10' SECONDS) AS window_end,
        after.currency AS currency,
        AVG(after.amount) AS avg_amount
    FROM kafka_source_raw
    GROUP BY TUMBLE(computed_event_timestamp, INTERVAL '10' SECONDS), after.currency
""")

print("ended")
