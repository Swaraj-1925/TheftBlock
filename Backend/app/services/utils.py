import datetime
import hashlib
import uuid


def generate_id(tag:str):
    unique_id = str(uuid.uuid4())
    timestamp = str(datetime.datetime.now())
    id_hash = hashlib.sha256((timestamp + unique_id).encode()).hexdigest()[:10]
    id_tag = f"{tag}_{id_hash}"
    return id_tag
