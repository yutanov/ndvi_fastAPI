from typing import Optional

from sqlalchemy import desc, asc
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database.models.zone import Zone, ZoneCreate, ZoneUpdate


class ZonesRepository(object):
    def __init__(self, session):
        self.session = session

    async def get_all(
            self,
            search_title: Optional[str] = None) -> list[Zone]:
        query = select(Zone)

        if search_title is not None:
            if '*' in search_title or '_' in search_title:
                looking_for = search_title.replace('_', '__') \
                    .replace('*', '%') \
                    .replace('?', '_')
            else:
                looking_for = f'%{search_title}%'

            query = query.where(Zone.title.ilike(looking_for.lower()))

        execute = await self.session.execute(query)

        db_zones: list[Zone] = execute.scalars().all()
        return db_zones

    async def get_by_id(self, zone_id: int) -> Optional[Zone]:
        query = select(Zone).where(Zone.id == zone_id)
        execute = await self.session.execute(query)

        db_zone: Optional[Zone] = execute.scalar_one_or_none()
        return db_zone

    def create(self, zone_create: ZoneCreate) -> Zone:
        db_zone = Zone.from_orm(zone_create)

        self.session.add(db_zone)

        return db_zone

    def update(self, db_zone: Zone, zone_update: ZoneUpdate) -> Optional[Zone]:
        for var, value in vars(zone_update).items():
            if vars(db_zone).get(var) is None:
                continue
            setattr(db_zone, var, value) if value else None

        self.session.add(db_zone)
        return db_zone

    async def delete(self, db_zone: Zone) -> None:
        await self.session.delete(db_zone)

    async def commit(self):
        await self.session.commit()

    async def refresh(self, db_zone: Zone):
        await self.session.refresh(db_zone)
