"""Interest management routes and CRUD operations.

This module provides API endpoints for managing user interest information
including creation, updates, deletion, and retrieval. It extends the base
CRUD class with interest-specific functionality.

Classes
-------
CRUD : BaseCRUD
    Extended CRUD class with interest-specific operations

Functions
---------
as_dict : dict
    Convert interest model to dictionary
get_interests : list[Interest]
    Retrieve all interests for a user
create_interest : Interest
    Create a new interest
update_interest : Interest
    Update interest information
delete_interest : Interest
    Delete an existing interest
"""

from typing import Annotated
from fastapi import HTTPException, APIRouter, Depends
from sqlmodel import Session, select

from src.db.models import Interest
from src.routes.base_crud import BaseCRUD
from src.db.db import get_session


class CRUD(BaseCRUD):
    """Extended CRUD class for interest-specific operations.

    Provides interest management functionality including user-specific
    lookups and specialized retrieval operations.

    Methods
    -------
    get_multiple : list[Interest]
        Get all interests for a specific user
    """

    def get_multiple(  # pylint: disable=W0221
        self, session: Session, user_id: int
    ) -> list[Interest]:
        """Get all interests for a user.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        user_id : int
            ID of the user to retrieve interests for

        Returns
        -------
        list[Interest]
            List of interest objects for the user

        Raises
        ------
        HTTPException
            If no interests are found for the user
        """
        statement = select(Interest).where(Interest.user_id == user_id)
        result = session.exec(statement).all()
        if not result:
            raise HTTPException(
                status_code=404, detail=f"No interests found for user {user_id}."
            )
        return result


interest_CRUD = CRUD(Interest)

router = APIRouter(prefix="/interest", tags=["Interest"])


def as_dict(interest: Interest) -> dict:
    """Convert interest model to dictionary.

    Parameters
    ----------
    interest : Interest
        Interest model instance to convert

    Returns
    -------
    dict
        Dictionary representation of the interest
    """
    return interest.model_dump()


@router.get("/{user_id}", response_model=list[Interest])
async def get_interests(
    user_id: int, session: Session = Depends(get_session)
) -> list[Interest]:
    """Get all interests for a user.

    Parameters
    ----------
    user_id : int
        ID of the user to retrieve interests for
    session : Session
        Database session dependency

    Returns
    -------
    list[Interest]
        List of interest objects for the user
    """
    return interest_CRUD.get_multiple(session, user_id)


@router.post("/", response_model=Interest)
async def create_interest(
    interest_data: Interest, session: Session = Depends(get_session)
) -> Interest:
    """Create a new interest.

    Parameters
    ----------
    interest_data : Interest
        Interest data for creation
    session : Session
        Database session dependency

    Returns
    -------
    Interest
        The created interest object
    """
    return interest_CRUD.create(session, interest_data)


@router.put("/{interest_id}", response_model=Interest)
async def update_interest(
    interest_id: int,
    interest_data: Annotated[dict, Depends(as_dict)],
    session: Session = Depends(get_session),
) -> Interest:
    """Update an existing interest with fields passed in the request body.

    The user can pass as few as one field to update.
    Others fields retain their existing values.

    Parameters
    ----------
    interest_id : int
        ID of the interest to update
    interest_data : dict
        Dictionary containing fields to update
    session : Session
        Database session dependency

    Returns
    -------
    Interest
        The updated interest object
    """
    return interest_CRUD.update(session, interest_id, interest_data)


@router.delete("/{interest_id}", response_model=Interest)
async def delete_interest(
    interest_id: int, session: Session = Depends(get_session)
) -> Interest:
    """Delete an existing interest.

    Parameters
    ----------
    interest_id : int
        ID of the interest to delete
    session : Session
        Database session dependency

    Returns
    -------
    Interest
        The deleted interest object
    """
    return interest_CRUD.delete(session, interest_id)
