from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class ZoneBase(SQLModel):
    __tablename__ = "zones"

    title: str = Field(max_length=256, nullable=False, default="NoName")
    comment: str = Field(max_length=2048, nullable=True, default="")


class Zone(ZoneBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(nullable=False, default=datetime.utcnow())

    ndviFilename: str = Field(max_length=256, nullable=True, default="")
    photoFilename: str = Field(max_length=256, nullable=True, default="")
    geoJsonFilename: str = Field(max_length=256, nullable=True, default="")


class ZoneGet(ZoneBase):
    id: int
    created_at: datetime

    ndviFilename: str
    photoFilename: str
    geoJsonFilename: str


class ZoneCreate(ZoneBase):
    ndviFilename: Optional[str]
    photoFilename: Optional[str]
    geoJsonFilename: Optional[str]


class ZoneUpdate(ZoneBase):
    ndviFilename: Optional[str]
    photoFilename: Optional[str]
    geoJsonFilename: Optional[str]
