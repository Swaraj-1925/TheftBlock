from sqlmodel.ext.asyncio.session import AsyncSession

from typing import Dict, Type,Any
from sqlmodel import SQLModel, select

class DatabaseManagement:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def insert(self, model: SQLModel,auto_commit:bool=True):
        try:
            self.session.add(model)
            if auto_commit:
                await self.session.commit()
                await self.session.refresh(model)
            return model
        except Exception as e:
            print(f"Database insert error: {str(e)}")
            await self.session.rollback()
            raise Exception("Failed to insert record.")

    async def upsert(self, model: SQLModel):
        try:
            merged_model = await self.session.merge(model)
            await self.session.commit()
            await self.session.refresh(merged_model)
            return merged_model
        except Exception as e:
            print(f"Database upsert error: {str(e)}")
            await self.session.rollback()
            raise Exception("Failed to upsert record.")

    async def search(self, model: Type[SQLModel], all_results: bool = True, **kwargs):
        try:
            query = select(model)
            for key, value in kwargs.items():
                if hasattr(model, key):
                    query = query.where(getattr(model, key) == value)

            if all_results:
                results = (await self.session.exec(query)).all()
            else:
                results = (await self.session.exec(query)).first()
            return results
        except Exception as e:
            print(f"Database search error: {e}")
            raise Exception("Failed to search records.")
    async def update_row(self,model: Type[SQLModel],search_criteria: Dict[str, Any],update_data: Dict[str, Any],insert_if_not_exist: bool = True) -> SQLModel:
        try:
            existing_record = await self.search(
                model=model,
                all_results=False,
                **search_criteria
                )
            if not existing_record:
                    if insert_if_not_exist:
                        new_record = model(**update_data)
                        return await self.insert(new_record)
                    else:
                        raise Exception(f"Record not found with criteria: {search_criteria}")
            else:
                if hasattr(existing_record, 'id'):
                    update_data['id'] = existing_record.id
            updated_record = model(**update_data)
            return await self.upsert(updated_record)
        except Exception as e:
            print(f"Database update_row error: {str(e)}")
            await self.session.rollback()
            raise Exception(f"Failed to update record: {str(e)}")