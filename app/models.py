import datetime
from pydantic import BaseModel

# response models for endpoints required for docs


class Image(BaseModel):
    link: str


class TimestampedImage(BaseModel):
    url: str
    timestamp: datetime.datetime
