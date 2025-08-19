"""Allergy management routes and CRUD operations.

This module provides API endpoints for managing allergy information including
creation, updates, and deletion. It extends the base CRUD class with
allergy-specific functionality.

Classes
-------
CRUD : BaseCRUD
    Extended CRUD class with allergy-specific operations

Functions
---------
get_allergies : list[Allergy]
    Retrieve all allergies
create_allergy : Allergy
    Create a new allergy
update_allergy : Allergy
    Update allergy description
delete_allergy : Allergy
    Delete an existing allergy
"""

from typing import Annotated
from fastapi import HTTPException, APIRouter, Body, Depends
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from src.db.models import Allergy
from src.routes.base_crud import BaseCRUD
from src.db.db import get_session


class CRUD(BaseCRUD):
    """Extended CRUD class for allergy-specific operations.

    Provides allergy management functionality including name-based lookups
    and specialized update operations.

    Methods
    -------
    update : Allergy
        Update allergy information by name
    delete : Allergy
        Delete allergy by name
    """

    def update(  # pylint: disable=W0237
        self, session: Session, allergy_name: str, data: dict
    ) -> Allergy:
        """Update/Put an allergy in a table.

        Only updates fields which have a value in the data dictionary.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        allergy_name : str
            Name of the allergy to update
        data : dict
            Dictionary containing field names and values to update

        Returns
        -------
        Allergy
            The updated allergy object

        Raises
        ------
        HTTPException
            If no allergy is found or there's an integrity error
        """
        try:
            statement = select(self.model).where(self.model.name == allergy_name)
            result = session.exec(statement).first()
            if not result:
                raise HTTPException(status_code=404, detail="Record not found")
            for key, value in data.items():
                if value is not None:
                    setattr(result, key, value)
            session.add(result)
            session.commit()
            session.refresh(result)
            return result
        except IntegrityError as e:
            raise HTTPException(status_code=422, detail=f"Integrity error: {e}") from e

    def delete(  # pylint: disable=W0237
        self, session: Session, allergy_name: str
    ) -> Allergy:
        """Delete a record from a table.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        allergy_name : str
            Name of the allergy to delete

        Returns
        -------
        Allergy
            The deleted allergy object

        Raises
        ------
        HTTPException
            If no allergy is found with the given name
        """
        statement = select(self.model).where(self.model.name == allergy_name)
        result = session.exec(statement).first()
        if not result:
            raise HTTPException(status_code=404, detail="Record not found")
        session.delete(result)
        session.commit()
        return result


allergy_CRUD = CRUD(Allergy)

router = APIRouter(prefix="/allergy", tags=["Allergy"])


@router.get("/", response_model=list[Allergy])
async def get_allergies(session: Session = Depends(get_session)) -> list[Allergy]:
    """Get all allergies.

    Parameters
    ----------
    session : Session
        Database session dependency

    Returns
    -------
    list[Allergy]
        List of all allergy objects in the system
    """
    return allergy_CRUD.get_multiple(session)


@router.post("/", response_model=Allergy)
async def create_allergy(
    allergy_data: Allergy, session: Session = Depends(get_session)
) -> Allergy:
    """Create a new allergy.

    Parameters
    ----------
    allergy_data : Allergy
        Allergy data for creation
    session : Session
        Database session dependency

    Returns
    -------
    Allergy
        The created allergy object
    """
    return allergy_CRUD.create(session, allergy_data)


@router.put("/{allergy_name}", response_model=Allergy)
async def update_allergy(
    allergy_name: str,
    allergy_data: Annotated[
        dict,
        Body(
            emeded=True,
            examples={"description": "Allergic reaction to milk and dairy products"},
        ),
    ],
    session: Session = Depends(get_session),
) -> Allergy:
    """Updates the allergy description.

    Parameters
    ----------
    allergy_name : str
        Name of the allergy to update
    allergy_data : dict
        Dictionary containing fields to update
    session : Session
        Database session dependency

    Returns
    -------
    Allergy
        The updated allergy object
    """
    return allergy_CRUD.update(session, allergy_name, allergy_data)


@router.delete("/{allergy_name}", response_model=Allergy)
async def delete_allergy(
    allergy_name: str, session: Session = Depends(get_session)
) -> Allergy:
    """Delete an existing allergy.

    Parameters
    ----------
    allergy_name : str
        Name of the allergy to delete
    session : Session
        Database session dependency

    Returns
    -------
    Allergy
        The deleted allergy object
    """
    return allergy_CRUD.delete(session, allergy_name)
