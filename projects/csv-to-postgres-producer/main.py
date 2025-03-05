from typing import List, Dict
import time
import duckdb
import os
import pandas as pd
from sqlalchemy import create_engine, text


# Get the directory of the current script
workspace_path = os.path.abspath(os.path.dirname(__file__))
csv_folder_path = os.path.normpath(os.path.join(workspace_path, "../sample_data"))
csv_deposit = os.path.join(csv_folder_path, "deposit_sample_data.csv")
csv_event = os.path.join(csv_folder_path, "event_sample_data.csv")
csv_user_level = os.path.join(csv_folder_path, "user_level_sample_data.csv")
csv_withdrawals = os.path.join(csv_folder_path, "withdrawals_sample_data.csv")


def create_duckdb_connection():
    return duckdb.connect(database=":memory:", read_only=False)


def create_postgres_engine():
    return create_engine("postgresql://postgres:postgres@host.docker.internal:5432/postgres")


def convert_schema_to_postgres(schema: duckdb.DuckDBPyRelation) -> str:
    columns = []
    for col_name, col_type in zip(schema.columns, schema.types):
        if col_name != "aggr":
            if col_type == "BOOLEAN":
                pg_type = "BOOLEAN"
            elif col_type == "INTEGER":
                pg_type = "INTEGER"
            elif col_type == "VARCHAR":
                pg_type = "TEXT"
            elif col_type == "DOUBLE":
                pg_type = "DOUBLE PRECISION"
            else:
                pg_type = "TEXT"  # Default to TEXT for simplicity
            columns.append(f"{col_name} {pg_type}")
    return ", ".join(columns)


def build_table_schema(workload: dict):
    relation = duckdb.from_csv_auto(path_or_buffer=workload["path"])
    schema = relation.describe()
    postgres_schema = convert_schema_to_postgres(schema)
    return f"""CREATE TABLE IF NOT EXISTS crypto.{workload["table_name"]} (
                {postgres_schema}, 
                CONSTRAINT pkey_{workload["table_name"]} 
                PRIMARY KEY ({workload["pk"]})
            );"""


def setup_postgres_and_workload():
    engine = create_postgres_engine()
    workloads: List[Dict] = []
    workloads.append({"table_name": "deposit", "path": csv_deposit, "pk": "id"})
    workloads.append({"table_name": "event", "path": csv_event, "pk": "id"})
    workloads.append({"table_name": "user_level", "path": csv_user_level, "pk": "user_id"})
    workloads.append({"table_name": "withdrawals", "path": csv_withdrawals, "pk": "id"})

    with engine.connect() as conn:
        conn.execute(text("create schema if not exists crypto"))
        conn.commit()

        for workload in workloads:
            create_table_query = build_table_schema(workload)
            conn.execute(text(create_table_query))
            conn.commit()

            df = pd.read_csv(workload["path"]).sort_values(by="event_timestamp", ascending=True)
            count = len(df)
            workload.update(
                {
                    "df": df,
                    "count": count,
                    "current_row": 0,
                }
            )

    return workloads


def merge_data(workload):
    engine = create_postgres_engine()
    df: pd.DataFrame = workload["selected_rows"]

    # Get columns and prepare strings for SQL query using colon style
    columns = df.columns.tolist()
    columns_str = ", ".join(columns)
    values_str = ", ".join([f":{col}" for col in columns])
    update_str = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != workload["pk"]])

    insert_query = text(
        f"INSERT INTO crypto.{workload['table_name']} ({columns_str}) "
        f"VALUES ({values_str}) "
        f"ON CONFLICT ({workload['pk']}) "
        f"DO UPDATE SET {update_str};"
    )

    with engine.connect() as conn:
        data = df.to_dict(orient="records")
        conn.execute(insert_query, data)
        conn.commit()


def stream_all_data_workloads(workloads: List[dict]):
    speed = 1

    while any(workload["current_row"] < workload["count"] for workload in workloads):
        for workload in workloads:
            if workload["current_row"] < workload["count"]:
                current_row = workload["current_row"]
                workload["selected_rows"] = workload["df"][current_row : current_row + speed]

                print(f"Merging on {workload['table_name']}")
                merge_data(workload)
                workload["current_row"] += speed

                # selected_rows.to_sql(table_name, engine, if_exists="append", index=False, method="multi")

        time.sleep(1)


def main():
    print("Starting!")

    print("Setting up postgres tables")
    workloads = setup_postgres_and_workload()

    print("Streaming data to postgres")
    stream_all_data_workloads(workloads)

    print("Finished")


if __name__ == "__main__":
    try:
        print(workspace_path)
        main()
    except Exception as e:
        print(e)
