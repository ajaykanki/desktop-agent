from app.config import config
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name=config.api.key_header, auto_error=True)


def verify_api_key(api_key: str = Security(api_key_header)):
    # TODO: Implement API key verification
    if api_key == "mykey":
        return api_key
    raise HTTPException(status_code=401, detail="Missing or incorrect API key")
