def event(event_type: str, **data) -> dict:
    return {"type": event_type, "data": data}
