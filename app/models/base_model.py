from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column
)

from typing import Annotated
from datetime import datetime


created_time = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
]
updated_time = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
]


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
        unique=True,
        nullable=False
    )
    created_at: Mapped[created_time] = mapped_column(
        nullable=False
    )
    updated_at: Mapped[updated_time] = mapped_column(
        nullable=False
    )
