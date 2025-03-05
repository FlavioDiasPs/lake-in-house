CREATE TABLE IF NOT EXISTS flink_aggregated_deposits (
    window_end TIMESTAMP(3),
    currency TEXT,
    avg_amount NUMERIC(38,18)
);