"""
Base class for CRUD operations.

This module provides a base CRUD class that can be inherited and extended
to provide standard database operations for any SQLModel-based model.
"""

from sqlmodel import SQLModel, Session, select
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class BaseCRUD:
    """Base class for CRUD operations.

    Provides standard Create, Read, Update, Delete operations for any
    SQLModel-based model. Inherit and override methods as needed.

    Attributes
    ----------
    model : SQLModel
        The SQLModel class to perform CRUD operations on

    Methods
    -------
    get_multiple : list[SQLModel]
        Retrieve all records from the table
    get : SQLModel
        Retrieve a single record by primary key
    create : SQLModel
        Create a new record in the table
    update : SQLModel
        Update an existing record
    delete : SQLModel
        Delete a record from the table
    """

    def __init__(self, model: SQLModel):
        """Initialize the BaseCRUD instance.

        Parameters
        ----------
        model : SQLModel
            The SQLModel class to perform CRUD operations on
        """
        self.model = model

    def get_multiple(self, session: Session) -> list[SQLModel]:
        """Read/Get all records in a table.

        Returns
        -------
        list[SQLModel]
            List of all records from the table

        Raises
        ------
        HTTPException
            If there's an error retrieving the records
        """
        return session.exec(select(self.model)).all()

    def get(self, session: Session, field_value: int | str) -> SQLModel:
        """Read/Get a record by its primary key.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        field_value : int | str
            The primary key value to search for

        Returns
        -------
        SQLModel
            The found record

        Raises
        ------
        HTTPException
            If no record is found with the given primary key
        """
        statement = select(self.model).where(self.model.id == field_value)
        result = session.exec(statement).first()
        if not result:
            raise HTTPException(status_code=404, detail="Record not found")
        return result

    def create(self, session: Session, record: SQLModel) -> SQLModel:
        """Create/Post a new record in a table.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        record : SQLModel
            The record to create

        Returns
        -------
        SQLModel
            The created record with updated ID

        Raises
        ------
        HTTPException
            If there's an integrity error during creation
        """
        try:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record
        except IntegrityError as e:
            raise HTTPException(status_code=422, detail=f"Integrity error: {e}") from e

    def update(self, session: Session, record_id: int | str, data: dict) -> SQLModel:
        """Update/Put a record in a table.

        Only updates fields which have a value in the data dictionary.
        Currently uses manual field-by-field updates, but there's a TODO
        to implement sqlmodel_update() for more efficient updates.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        record_id : int | str
            The primary key of the record to update
        data : dict
            Dictionary containing field names and values to update

        Returns
        -------
        SQLModel
            The updated record

        Raises
        ------
        HTTPException
            If no record is found or there's an integrity error

        Notes
        -----
        TODO: Consider using result.sqlmodel_update(data) instead of the
        manual for loop for more efficient and maintainable updates.
        """
        try:
            statement = select(self.model).where(self.model.id == record_id)
            result = session.exec(statement).first()
            if not result:
                raise HTTPException(status_code=404, detail="Record not found")
            for key, value in data.items():
                if value is not None:
                    setattr(result, key, value)
            # TODO: try using result.sqlmodel_update(data) instead of the for loop
            session.add(result)
            session.commit()
            session.refresh(result)
            return result
        except IntegrityError as e:
            raise HTTPException(status_code=422, detail=f"Integrity error: {e}") from e

    def delete(self, session: Session, record_id: int | str) -> SQLModel:
        """Delete a record from a table.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        record_id : int | str
            The primary key of the record to delete

        Returns
        -------
        SQLModel
            The deleted record

        Raises
        ------
        HTTPException
            If no record is found or there's an integrity error
        """
        statement = select(self.model).where(self.model.id == record_id)
        result = session.exec(statement).first()
        if not result:
            raise HTTPException(status_code=404, detail="Record not found")
        try:
            session.delete(result)
            session.commit()
            return result
        except IntegrityError as e:
            # Handle foreign key constraint violations
            if "foreign key constraint" in str(e).lower():
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Cannot delete this record as it is referenced "
                        f"by other records: {e}"
                    ),
                ) from e
            # Handle other integrity errors
            raise HTTPException(status_code=422, detail=f"Integrity error: {e}") from e
