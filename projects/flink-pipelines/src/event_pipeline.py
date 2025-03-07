from pyflink.table import EnvironmentSettings, StreamTableEnvironment
import os

os.environ["FLINK_ENV_JAVA_OPTS"] = (
    "--add-opens java.base/java.util=ALL-UNNAMED --add-opens java.base/java.lang=ALL-UNNAMED --add-opens java.base/java.io=ALL-UNNAMED"
)

flink_settings = EnvironmentSettings.in_streaming_mode()
flink_settings.get_configuration().set_string(
    "execution.checkpointing.interval", "10000"
)  # 10 seconds interval
flink_settings.get_configuration().set_string(
    "execution.checkpointing.mode", "EXACTLY_ONCE"
)
flink_settings.get_configuration().set_string(
    "execution.checkpointing.timeout", "60000"
)  # 1 minute timeout
flink_settings.get_configuration().set_string(
    "execution.checkpointing.max-concurrent", "1"
)
t_env = StreamTableEnvironment.create(environment_settings=flink_settings)

workspace_path = os.path.abspath(os.path.dirname(__file__))
fql_event_create_source_path = os.path.normpath(
    os.path.join(workspace_path, "fql/event_cdc_queries.fql")
)
fql_event_statements = []

with open(fql_event_create_source_path) as file:
    fql_event_statements = file.read().split(";")

for statement in fql_event_statements:
    t_env.execute_sql(statement).wait()
