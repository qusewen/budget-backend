from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect
from sqlalchemy import select
from fastapi import HTTPException

from app.database.base import Base


async def validate_foreign_keys(db: AsyncSession, model_instance, update_data: dict):
    """
    Проверяет, что все внешние ключи в update_data существуют в связанных таблицах.
    """
    errors = []
    mapper = inspect(model_instance.__class__)

    for column in mapper.columns:
        if column.foreign_keys and column.key in update_data:
            field_value = update_data[column.key]

            if field_value is None:
                continue

            fk = next(iter(column.foreign_keys))
            target_table = fk.column.table

            target_model = None
            for model in Base.__subclasses__():
                if hasattr(model, '__tablename__') and model.__tablename__ == target_table.name:
                    target_model = model
                    break

            if target_model:
                query = select(target_model).where(target_model.id == field_value)
                result = await db.execute(query)
                exists = result.scalar_one_or_none()

                if not exists:
                    field_name = column.key.replace('_id', '').replace('_', ' ').capitalize()
                    errors.append(f"{field_name} с id {field_value} не существует")

    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))