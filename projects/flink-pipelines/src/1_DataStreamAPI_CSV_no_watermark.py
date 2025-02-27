from decimal import Decimal
import json
from typing import Dict
from pyflink.datastream import StreamExecutionEnvironment, DataStream
from pyflink.datastream.connectors.file_system import FileSource
from pyflink.datastream.formats.csv import CsvReaderFormat, CsvSchema
from pyflink.common import WatermarkStrategy, Types, Row
from pyflink.common.serialization import Encoder
from pyflink.datastream.connectors.file_system import FileSink

# Create a local execution environment.
# Create a StreamExecutionEnvironment, which can also be used for batch processing
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)  # Typically, for batch jobs, you'd want lower parallelism
env.disable_operator_chaining()

# Local CSV file (make sure this file exists on your local system)
file_path = "projects/sample_data/deposit_sample_data.csv"


def simulate_json_stream(row: Row):
    """
    Convert a CSV row into a JSON string.
    """
    return json.dumps(row.as_dict())


def process_json(json_string: str) -> dict:
    """
    Process the JSON string into a tuple.
    Returns (user_id, amount, currency). If amount casting fails, sets amount to 0.
    """
    json_data: Dict = json.loads(json_string)
    user_id: str = json_data.get("user_id", "unknown")  # Default if missing
    amount_str: str = json_data.get("amount")
    currency: str = json_data.get("currency", "unknown")  # Default if missing

    # Validate and cast amount to Decimal
    try:
        if amount_str is None or not amount_str.strip():  # Check for None or empty string
            amount = Decimal("0")
        else:
            amount = Decimal(amount_str.strip())  # Strip whitespace and cast
    except Exception as e:
        # Handle invalid decimal (e.g., "abc", "", None after strip)
        print(f"Warning: Failed to cast amount '{amount_str}' to Decimal: {str(e)}. Using 0.")
        amount = Decimal("0")

    return {"user_id": user_id, "amount": amount, "currency": currency}


def run_csv_job():
    csv_schema = (
        CsvSchema.builder()
        .add_string_column("id")
        .add_string_column("event_timestamp")
        .add_string_column("user_id")
        .add_string_column("amount")
        .add_string_column("currency")
        .add_string_column("tx_status")
        .set_column_separator(",")
        .set_use_header()
        .set_strict_headers()
        .build()
    )

    # Define the CSV source using CsvReaderFormat
    csv_format = CsvReaderFormat.for_schema(csv_schema)
    csv_source = FileSource.for_record_stream_format(csv_format, file_path).build()
    csv_stream: DataStream = env.from_source(
        csv_source, watermark_strategy=WatermarkStrategy.no_watermarks(), source_name="csv_deposit_sample_data"
    )

    json_stream = csv_stream.map(simulate_json_stream, output_type=Types.STRING())  # Ensure string output
    processed_stream: DataStream = json_stream.map(process_json)

    # Perform aggregation by user_id and currency (using reduce to avoid partial results)
    def reduce_fn(accumulated: dict, current: dict) -> dict:
        acc_amount: Decimal = accumulated.get("amount", Decimal("0"))
        accumulated["amount"] = acc_amount + Decimal(current["amount"])
        return accumulated

    # Use a reduce function to accumulate the values after the map
    result_stream = processed_stream.key_by(lambda x: (x["currency"])).reduce(reduce_fn)

    # Format the result to a human-readable string and write it to the sink (final output only)
    result_stream = result_stream.map(
        lambda x: f"Total Amount: {x['amount']:.2f}, Currency: {x['currency']}",
        output_type=Types.STRING(),
    )

    # # Print the result to the console.
    # result_stream.print()

    sink = FileSink.for_row_format(".", Encoder.simple_string_encoder()).build()
    result_stream.sink_to(sink)

    env.execute("sfgsdfg")


if __name__ == "__main__":
    run_csv_job()
