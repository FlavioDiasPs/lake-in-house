from pyflink.table import EnvironmentSettings, StreamTableEnvironment
import os

os.environ["FLINK_ENV_JAVA_OPTS"] = (
    "--add-opens java.base/java.util=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/java.io=ALL-UNNAMED"
)

flink_settings = EnvironmentSettings.in_streaming_mode()
flink_settings.get_configuration().set_string("execution.checkpointing.interval", "10000")  # 10 seconds interval
flink_settings.get_configuration().set_string("execution.checkpointing.mode", "EXACTLY_ONCE")
flink_settings.get_configuration().set_string("execution.checkpointing.timeout", "10000")  # 10 seconds timeout
flink_settings.get_configuration().set_string("execution.checkpointing.max-concurrent", "1")
flink_settings.get_configuration().set_string("parallelism.default", "1")  # Set parallelism to 1
t_env = StreamTableEnvironment.create(environment_settings=flink_settings)

workspace_path = os.path.abspath(os.path.dirname(__file__))
fql_withdrawals_create_source_path = os.path.normpath(
    os.path.join(workspace_path, "fql/hourly_transaction_amount_sum_queries.fql")
)
fql_withdrawals_statements = []

with open(fql_withdrawals_create_source_path) as file:
    fql_withdrawals_statements = file.read().split(";")

for statement in fql_withdrawals_statements:
    if statement.find("CREATE"):
        t_env.execute_sql(statement).wait()
    else:
        print("Starting streaming job")
        t_env.execute_sql(statement)  # Don’t wait on streaming INSERT because it hangs
