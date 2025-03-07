from typing import List, Dict, TypedDict, Any, Optional
import time
import duckdb
import os
import pandas as pd
from sqlalchemy import create_engine, text, Engine
from duckdb import DuckDBPyConnection, DuckDBPyRelation


class WorkloadConfig(TypedDict):
    table_name: str
    path: str
    pk: str


class Workload(WorkloadConfig):
    df: pd.DataFrame
    count: int
    current_row: int
    selected_rows: Optional[pd.DataFrame]


# Get the directory of the current script
workspace_path = os.path.abspath(os.path.dirname(__file__))
csv_folder_path = os.path.normpath(os.path.join(workspace_path, "../sample_data"))
csv_deposit = os.path.join(csv_folder_path, "deposit_sample_data.csv")
csv_event = os.path.join(csv_folder_path, "event_sample_data.csv")
csv_user_level = os.path.join(csv_folder_path, "user_level_sample_data.csv")
csv_withdrawals = os.path.join(csv_folder_path, "withdrawals_sample_data.csv")


def create_duckdb_connection() -> DuckDBPyConnection:
    return duckdb.connect(database=":memory:", read_only=False)


def create_postgres_engine() -> Engine:
    return create_engine("postgresql://postgres:postgres@host.docker.internal:5432/postgres")


def convert_schema_to_postgres(schema: DuckDBPyRelation) -> str:
    columns: List[str] = []
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


def build_table_schema(workload: WorkloadConfig) -> str:
    relation: DuckDBPyRelation = duckdb.from_csv_auto(path_or_buffer=workload["path"])
    schema: DuckDBPyRelation = relation.describe()
    postgres_schema: str = convert_schema_to_postgres(schema)
    return f"""CREATE TABLE IF NOT EXISTS crypto.{workload["table_name"]} (
                {postgres_schema}, 
                CONSTRAINT pkey_{workload["table_name"]} 
                PRIMARY KEY ({workload["pk"]})
            );"""


def setup_postgres_and_workload() -> List[Workload]:
    engine: Engine = create_postgres_engine()
    workloads: List[WorkloadConfig] = [
        {"table_name": "deposit", "path": csv_deposit, "pk": "id"},
        {"table_name": "event", "path": csv_event, "pk": "id"},
        {"table_name": "user_level", "path": csv_user_level, "pk": "user_id"},
        {"table_name": "withdrawals", "path": csv_withdrawals, "pk": "id"},
    ]

    result_workloads: List[Workload] = []

    with engine.connect() as conn:
        conn.execute(text("create schema if not exists crypto"))
        conn.commit()

        for workload in workloads:
            create_table_query: str = build_table_schema(workload)
            conn.execute(text(create_table_query))
            conn.commit()

            df: pd.DataFrame = pd.read_csv(workload["path"]).sort_values(by="event_timestamp", ascending=True)
            count: int = len(df)

            full_workload: Workload = {
                **workload,
                "df": df,
                "count": count,
                "current_row": 0,
                "selected_rows": None,
            }
            result_workloads.append(full_workload)

    return result_workloads


def merge_data(workload: Workload) -> None:
    engine: Engine = create_postgres_engine()
    df: pd.DataFrame = workload["selected_rows"]  # type: ignore

    if df is None or df.empty:
        return

    columns: List[str] = df.columns.tolist()
    columns_str: str = ", ".join(columns)
    values_str: str = ", ".join([f"%({col})s" for col in columns])
    update_str: str = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != workload["pk"]])

    insert_query = text(
        f"INSERT INTO crypto.{workload['table_name']} ({columns_str}) "
        f"VALUES ({values_str}) "
        f"ON CONFLICT ({workload['pk']}) "
        f"DO UPDATE SET {update_str};"
    )

    with engine.connect() as conn:
        data: List[Dict[str, Any]] = [row.to_dict() for _, row in df.iterrows()]
        conn.execute(insert_query, data)
        conn.commit()


def stream_all_data_workloads(workloads: List[Workload]) -> None:
    speed: int = 1

    while any(workload["current_row"] < workload["count"] for workload in workloads):
        for workload in workloads:
            if workload["current_row"] < workload["count"]:
                current_row: int = workload["current_row"]
                end_row: int = min(current_row + speed, workload["count"])
                workload["selected_rows"] = workload["df"].iloc[current_row:end_row].copy()

                print(f"Merging on {workload['table_name']}")
                merge_data(workload)
                workload["current_row"] += speed

        time.sleep(1)


def main() -> None:
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
