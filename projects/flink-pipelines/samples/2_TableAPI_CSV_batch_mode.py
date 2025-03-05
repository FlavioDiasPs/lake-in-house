from pyflink.table import EnvironmentSettings, TableEnvironment

# Set up the execution environment for Batch processing using the Table API
env_settings = EnvironmentSettings.in_batch_mode()
t_env = TableEnvironment.create(env_settings)

# Define the path to the CSV file
file_path = r"projects\sample_data\deposit_sample_data.csv"

# Register the CSV file as a temporary table
t_env.execute_sql(f"""
    CREATE TEMPORARY TABLE transactions (
        id STRING,
        event_timestamp STRING,
        user_id STRING,
        amount DOUBLE,
        currency STRING,
        tx_status STRING
    ) WITH (
        'connector' = 'filesystem',
        'path' = '{file_path}',
        'format' = 'csv',
        'csv.ignore-parse-errors' = 'true',
        'csv.field-delimiter' = ','
    )
""")

# Create a SQL query to calculate the total amount per user
result_table = t_env.sql_query("""
    SELECT user_id, SUM(amount) AS total_amount
    FROM transactions
    GROUP BY user_id
    LIMIT 10
""")

# Execute and print the result
result_table.execute().print()
