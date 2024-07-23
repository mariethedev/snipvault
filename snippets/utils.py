import uuid

def generate_short_uuid (length=4):
    return str(uuid.uuid4())[:length]

def generate_prefixed_uuid(prefix, length=5):
    return f"{prefix}_{str(uuid.uuid4())[:length]}"
