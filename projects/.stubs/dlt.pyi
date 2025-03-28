# dlt.pyi
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar
import pyspark.sql
import pyspark.sql.types

T = TypeVar("T", bound=Callable[..., Any])

# Core table and view decorators
def table(
    name: Optional[str] = None,
    comment: Optional[str] = None,
    schema: Optional[Union[str, Dict[str, Any], pyspark.sql.types.StructType]] = None,
    partition_cols: Optional[List[str]] = None,
    table_properties: Optional[Dict[str, str]] = None,
    temporary: bool = False,
    path: Optional[str] = None,
    pipeline_name: Optional[str] = None,
) -> Callable[[T], T]: ...
def view(
    name: Optional[str] = None, comment: Optional[str] = None, pipeline_name: Optional[str] = None
) -> Callable[[T], T]: ...

# Data quality expectations
def expect_all(expectations: Dict[str, str]) -> Callable[[T], T]: ...
def expect_all_or_drop(expectations: Dict[str, str]) -> Callable[[T], T]: ...
def expect_all_or_fail(expectations: Dict[str, str]) -> Callable[[T], T]: ...
def expect(name: str, condition: str) -> Callable[[T], T]: ...
def expect_or_drop(name: str, condition: str) -> Callable[[T], T]: ...
def expect_or_fail(name: str, condition: str) -> Callable[[T], T]: ...
def expect_column(column_name: str, condition: Optional[str] = None) -> Callable[[T], T]: ...
def expect_column_or_drop(column_name: str, condition: Optional[str] = None) -> Callable[[T], T]: ...
def expect_column_or_fail(column_name: str, condition: Optional[str] = None) -> Callable[[T], T]: ...

# Helper functions
def read(name: str, pipeline_name: Optional[str] = None) -> pyspark.sql.DataFrame: ...
def read_stream(name: str, pipeline_name: Optional[str] = None) -> pyspark.sql.DataFrame: ...

# Metadata functions
def current_pipeline_name() -> str: ...
def get_pipeline_config(key: str, default: Optional[Any] = None) -> Any: ...
def apply_changes(
    target: str,
    source: str,
    keys: List[str],
    sequence_by: Optional[str] = None,
    ignore_null_updates: bool = False,
    apply_as_deletes: Optional[str] = None,
    column_list: Optional[List[str]] = None,
    except_column_list: Optional[List[str]] = None,
) -> pyspark.sql.DataFrame: ...

# Streaming functions
def create_streaming_live_table(name: str, source: pyspark.sql.DataFrame, comment: Optional[str] = None) -> None: ...
def create_streaming_table(name: str, source: pyspark.sql.DataFrame, comment: Optional[str] = None) -> None: ...

# DLT logging
class Logs:
    def info(self, message: str) -> None: ...
    def warn(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...

logs = Logs()
