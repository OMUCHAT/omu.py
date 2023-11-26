from pydantic import BaseModel, validator


class Address(BaseModel):
    host: str
    port: int
    secure: bool = False

    @validator("port")
    def port_range(cls, v):
        if not 0 <= v <= 65535:
            raise ValueError("port must be in range 0-65535")
        return v

    def __str__(self):
        return f"{self.host}:{self.port}"
