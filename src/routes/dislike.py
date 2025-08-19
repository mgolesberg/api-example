"""Dislike management routes and CRUD operations.

This module provides API endpoints for managing user dislike information
including creation, updates, deletion, and retrieval. It extends the base
CRUD class with dislike-specific functionality.

Classes
-------
CRUD : BaseCRUD
    Extended CRUD class with dislike-specific operations

Functions
---------
as_dict : dict
    Convert dislike model to dictionary
get_dislikes : list[Dislike]
    Retrieve all dislikes for a user
create_dislike : Dislike
    Create a new dislike
update_dislike : Dislike
    Update dislike information
delete_dislike : Dislike
    Delete an existing dislike
"""

from typing import Annotated
from fastapi import HTTPException, APIRouter, Depends
from sqlmodel import Session, select

from src.db.models import Dislike
from src.routes.base_crud import BaseCRUD
from src.db.db import get_session


class CRUD(BaseCRUD):
    """Extended CRUD class for dislike-specific operations.

    Provides dislike management functionality including user-specific
    lookups and specialized retrieval operations.

    Methods
    -------
    get_multiple : list[Dislike]
        Get all dislikes for a specific user
    """

    def get_multiple(  # pylint: disable=W0221
        self, session: Session, user_id: int
    ) -> list[Dislike]:
        """Get all dislikes for a user.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        user_id : int
            ID of the user to retrieve dislikes for

        Returns
        -------
        list[Dislike]
            List of dislike objects for the user

        Raises
        ------
        HTTPException
            If no dislikes are found for the user
        """
        statement = select(Dislike).where(Dislike.user_id == user_id)
        result = session.exec(statement).all()
        if not result:
            raise HTTPException(
                status_code=404, detail=f"No dislikes found for user {user_id}."
            )
        return result


dislike_CRUD = CRUD(Dislike)

router = APIRouter(prefix="/dislike", tags=["Dislike"])


def as_dict(dislike: Dislike) -> dict:
    """Convert dislike model to dictionary.

    Parameters
    ----------
    dislike : Dislike
        Dislike model instance to convert

    Returns
    -------
    dict
        Dictionary representation of the dislike
    """
    return dislike.model_dump()


@router.get("/{user_id}", response_model=list[Dislike])
async def get_dislikes(
    user_id: int, session: Session = Depends(get_session)
) -> list[Dislike]:
    """Get all dislikes for a user.

    Parameters
    ----------
    user_id : int
        ID of the user to retrieve dislikes for
    session : Session
        Database session dependency

    Returns
    -------
    list[Dislike]
        List of dislike objects for the user
    """
    return dislike_CRUD.get_multiple(session, user_id)


@router.post("/", response_model=Dislike)
async def create_dislike(
    dislike_data: Dislike, session: Session = Depends(get_session)
) -> Dislike:
    """Create a new dislike.

    Parameters
    ----------
    dislike_data : Dislike
        Dislike data for creation
    session : Session
        Database session dependency

    Returns
    -------
    Dislike
        The created dislike object
    """
    return dislike_CRUD.create(session, dislike_data)


@router.put("/{dislike_id}", response_model=Dislike)
async def update_dislike(
    dislike_id: int,
    dislike_data: Annotated[dict, Depends(as_dict)],
    session: Session = Depends(get_session),
) -> Dislike:
    """Update an existing dislike with fields passed in the request body.

    The user can pass as few as one field to update.
    Others fields retain their existing values.

    Parameters
    ----------
    dislike_id : int
        ID of the dislike to update
    dislike_data : dict
        Dictionary containing fields to update
    session : Session
        Database session dependency

    Returns
    -------
    Dislike
        The updated dislike object
    """
    return dislike_CRUD.update(session, dislike_id, dislike_data)


@router.delete("/{dislike_id}", response_model=Dislike)
async def delete_dislike(
    dislike_id: int, session: Session = Depends(get_session)
) -> Dislike:
    """Delete an existing dislike.

    Parameters
    ----------
    dislike_id : int
        ID of the dislike to delete
    session : Session
        Database session dependency

    Returns
    -------
    Dislike
        The deleted dislike object
    """
    return dislike_CRUD.delete(session, dislike_id)
