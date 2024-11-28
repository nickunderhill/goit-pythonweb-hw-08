from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactUpdate, ContactCreate


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int) -> List[Contact]:
        stmt = select(Contact).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return list(contacts.scalars().all())

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True))
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        contact = await self.get_contact_by_id(contact.id)
        if contact is None:
            raise ValueError("Contact not found")
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate
    ) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id)
        result = await self.db.execute(stmt)
        contact = result.scalar_one_or_none()
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact
