import dlt  # type: ignore


@dlt.on_event_hook  # type: ignore
def my_hook_function(event: dict[str, str]) -> None:
    print(f"Received event: {event}")
