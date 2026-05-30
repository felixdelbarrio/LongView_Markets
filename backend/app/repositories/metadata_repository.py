from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sqlmodel import Field, Session, SQLModel, create_engine, select


class Metadata(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str
    updated_at: str


class MetadataRepository:
    def __init__(self, db_path: Path) -> None:
        self.engine = create_engine(f"sqlite:///{db_path}")
        SQLModel.metadata.create_all(self.engine)

    def set(self, key: str, value: str) -> None:
        with Session(self.engine) as session:
            existing = session.get(Metadata, key)
            if existing:
                existing.value = value
                existing.updated_at = datetime.now(UTC).isoformat()
            else:
                session.add(Metadata(key=key, value=value, updated_at=datetime.now(UTC).isoformat()))
            session.commit()

    def get(self, key: str) -> str | None:
        with Session(self.engine) as session:
            row = session.exec(select(Metadata).where(Metadata.key == key)).first()
            return row.value if row else None
