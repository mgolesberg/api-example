"""User management routes and CRUD operations.

This module provides API endpoints for user management including creation,
updates, deactivation, and allergy management. It extends the base CRUD
class with user-specific functionality.

Classes
-------
CRUD : BaseCRUD
    Extended CRUD class with user-specific operations

Functions
---------
as_dict : dict
    Convert user model to dictionary
get_user : User
    Retrieve a user by email or ID
update_user : User
    Update user profile information
deactivate_user : User
    Deactivate a user account
mark_user_for_deletion : User
    Mark a user for deletion
create_user : User
    Create a new user or reactivate deactivated user
get_user_allergies : list[Allergy]
    Retrieve all allergies for a user
add_allergy : list[Allergy]
    Add an allergy to a user
delete_allergy : list[Allergy]
    Remove an allergy from a user
"""

import re
from datetime import date
from typing import Annotated
from fastapi import HTTPException, APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError, DataError


from src.db.models import User, ConditionEnum, Allergy
from src.routes.base_crud import BaseCRUD
from src.db.db import get_session


class CRUD(BaseCRUD):
    """Extended CRUD class for user-specific operations.

    Provides user management functionality including phone number validation,
    email-based lookups, and allergy management.

    Methods
    -------
    _validate_phone_number : None
        Validate phone number format according to E.164 standard
    get : User
        Retrieve user by email or ID
    get_existing_email : User | None
        Check if user exists by email without raising exception
    update : User
        Update user information
    create : User
        Create new user with phone validation
    get_allergies : list[Allergy]
        Retrieve all allergies for a user
    add_allergy : list[Allergy]
        Add allergy to user
    delete_allergy : list[Allergy]
        Remove allergy from user
    """

    def _validate_phone_number(self, phone_number: str | None) -> None:
        """Validate phone number format according to E.164 standard.

        Parameters
        ----------
        phone_number : str | None
            Phone number to validate, None is allowed

        Raises
        ------
        HTTPException
            If phone number format is invalid
        """
        if phone_number is None:
            return  # Allow None phone numbers

        # E.164 format: +[country code][national number] (max 15 digits total)
        phone_pattern = r"^\+?[1-9]\d{1,14}$"
        if not re.match(phone_pattern, phone_number):
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Invalid phone number format: {phone_number}. "
                    "Phone number must follow E.164 format "
                    "(e.g., +1234567890 or 1234567890)"
                ),
            )

    def get(  # pylint: disable=W0237
        self, session: Session, email_or_id: str | int
    ) -> User:
        """Read/Get a user by email or ID.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        email_or_id : str | int
            Email address or user ID to search for

        Returns
        -------
        User
            The found user object

        Raises
        ------
        HTTPException
            If no user is found with the given email or ID
        """
        try:
            user_id = int(email_or_id)
            statement = select(self.model).where(self.model.id == user_id)
        except ValueError:
            statement = select(self.model).where(self.model.email == email_or_id)
        result = session.exec(statement).first()
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No user found with email or id {email_or_id}",
            )
        return result

    def get_existing_email(self, session: Session, email: str) -> User:
        """Read/Get a user by email, without raising an exception.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        email : str
            Email address to search for

        Returns
        -------
        User | None
            The found user object or None if not found
        """
        statement = select(self.model).where(self.model.email == email)
        result = session.exec(statement).first()
        if not result:
            return None  # Only used for checking is user exists in the post route
        return result

    def update(  # pylint: disable=W0237
        self, session: Session, email_or_id: str | int, data: dict
    ) -> User:
        """Update/Put a record in a table.

        Only updates fields which have a value in the data dictionary.
        Currently handles IntegrityError exceptions, with DataError handling
        commented out pending further investigation.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        email_or_id : str | int
            Email address or user ID of the user to update
        data : dict
            Dictionary containing field names and values to update

        Returns
        -------
        User
            The updated user object

        Raises
        ------
        HTTPException
            If no user is found or there's an integrity error

        Notes
        -----
        DataError handling is currently commented out as it may not be needed
        in the current implementation. Review if this exception handling
        should be re-enabled.
        """
        try:
            try:
                user_id = int(email_or_id)
                statement = select(self.model).where(self.model.id == user_id)
            except ValueError:
                statement = select(self.model).where(self.model.email == email_or_id)
            result = session.exec(statement).first()
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"User not found with email or id {email_or_id}",
                )
            for key, value in data.items():
                if value is not None:
                    setattr(result, key, value)
            session.add(result)
            session.commit()
            session.refresh(result)
            return result
        except IntegrityError as e:
            raise HTTPException(status_code=422, detail=f"Integrity error: {e}") from e
        except DataError as e:
            # This error triggers when the update tries to change the condition
            # in the data dict. Conditions should only be changed by the
            # create, deactivate, and mark_for_deletion routes
            raise HTTPException(
                status_code=422,
                detail="Data validation error: Do not pass the condition field here",
            ) from e

    def create(self, session: Session, record: User) -> User:
        """Create/Post a new record in a table.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        record : User
            The user record to create

        Returns
        -------
        User
            The created user object with updated ID

        Raises
        ------
        HTTPException
            If there's an integrity error during creation
        """
        # Validate phone number before creation
        self._validate_phone_number(record.phone_number)

        try:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record
        except IntegrityError as e:
            raise HTTPException(status_code=422, detail=f"Integrity error: {e}") from e

    def get_allergies(self, session: Session, email_or_id: str | int) -> list[Allergy]:
        """Get all allergies for a user.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        email_or_id : str | int
            Email address or user ID of the user

        Returns
        -------
        list[Allergy]
            List of allergy objects associated with the user

        Raises
        ------
        HTTPException
            If no user is found with the given email or ID
        """
        try:
            user_id = int(email_or_id)
            statement = select(self.model).where(self.model.id == user_id)
        except ValueError:
            statement = select(self.model).where(self.model.email == email_or_id)
        result = session.exec(statement).first()
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No user found with email or id {email_or_id}",
            )
        allergies = result.allergies
        return allergies

    def add_allergy(
        self, session: Session, user_id: int, allergy_name: str
    ) -> list[Allergy]:
        """Add an allergy to a user.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        user_id : int
            ID of the user to add allergy to
        allergy_name : str
            Name of the allergy to add

        Returns
        -------
        list[Allergy]
            Updated list of allergies for the user

        Raises
        ------
        HTTPException
            If allergy or user is not found, or allergy already exists
        """
        allergy = session.exec(
            select(Allergy).where(Allergy.name == allergy_name)
        ).first()
        if not allergy:
            raise HTTPException(
                status_code=404, detail=f"Allergy {allergy_name} not found"
            )

        user = session.exec(select(self.model).where(self.model.id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with id {user_id} not found"
            )
        user_allergy = user.allergies
        if allergy in user_allergy:
            raise HTTPException(
                status_code=409,
                detail=f"Allergy {allergy_name} already exists for user",
            )

        user.allergies.append(allergy)
        session.add(user)
        session.commit()
        return user.allergies

    def delete_allergy(
        self, session: Session, user_id: int, allergy_name: str
    ) -> list[Allergy]:
        """Delete an allergy from a user.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        user_id : int
            ID of the user to remove allergy from
        allergy_name : str
            Name of the allergy to remove

        Returns
        -------
        list[Allergy]
            Updated list of allergies for the user

        Raises
        ------
        HTTPException
            If allergy or user is not found, or allergy doesn't exist for user
        """
        allergy = session.exec(
            select(Allergy).where(Allergy.name == allergy_name)
        ).first()
        if not allergy:
            raise HTTPException(
                status_code=404, detail=f"Allergy {allergy_name} not found"
            )
        user = session.exec(select(self.model).where(self.model.id == user_id)).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with id {user_id} not found"
            )
        user_allergy = user.allergies
        if allergy not in user_allergy:
            raise HTTPException(
                status_code=404, detail=f"Allergy {allergy_name} not found for user"
            )
        user_allergy.remove(allergy)
        session.add(user)
        session.commit()
        return user.allergies


user_CRUD = CRUD(User)

router = APIRouter(prefix="/user", tags=["User"])


def as_dict(user: User) -> dict:
    """Convert user model to dictionary.

    Parameters
    ----------
    user : User
        User model instance to convert

    Returns
    -------
    dict
        Dictionary representation of the user
    """
    return user.model_dump()


@router.get("/{email_or_id}", response_model=User)
async def get_user(
    email_or_id: str | int, session: Session = Depends(get_session)
) -> User:
    """Get a specific user by email or id.

    Parameters
    ----------
    email_or_id : str | int
        Email address or user ID to search for
    session : Session
        Database session dependency

    Returns
    -------
    User
        The found user object
    """
    return user_CRUD.get(session, email_or_id)


@router.put("/{email_or_id}/profile", response_model=User)
async def update_user(
    email_or_id: str | int,
    user_data: Annotated[dict, Depends(as_dict)],
    session: Session = Depends(get_session),
) -> User:
    """Update an existing user with fields passed in the request body.

    The user can pass as few as one field to update.
    Others fields retain their existing values.

    Parameters
    ----------
    email_or_id : str | int
        Email address or user ID of the user to update
    user_data : dict
        Dictionary containing fields to update
    session : Session
        Database session dependency

    Returns
    -------
    User
        The updated user object
    """
    return user_CRUD.update(session, email_or_id, user_data)


@router.put("/{user_id}/deactivate", response_model=User)
async def deactivate_user(
    user_id: int, session: Session = Depends(get_session)
) -> User:
    """Deactivate a user by changing their condition to 'Deactivated'.

    Parameters
    ----------
    user_id : int
        ID of the user to deactivate
    session : Session
        Database session dependency

    Returns
    -------
    User
        The updated user object with deactivated status
    """
    return user_CRUD.update(session, user_id, {"condition": ConditionEnum.DEACTIVATED})


@router.put("/{user_id}/delete", response_model=User)
async def mark_user_for_deletion(
    user_id: int, session: Session = Depends(get_session)
) -> User:
    """Mark a user for deletion by changing their condition to 'Marked for deletion'.

    Parameters
    ----------
    user_id : int
        ID of the user to mark for deletion
    session : Session
        Database session dependency

    Returns
    -------
    User
        The updated user object with marked for deletion status
    """
    return user_CRUD.update(
        session, user_id, {"condition": ConditionEnum.MARKED_FOR_DELETION}
    )


@router.post("/", response_model=User)
async def create_user(user_data: User, session: Session = Depends(get_session)) -> User:
    """Create a new user or reactivate a deactivated user.

    If the email exists in the deactivated users table, reactivate the user
    and update with the provided values. If the user doesn't exist anywhere,
    create a new user.

    Parameters
    ----------
    user_data : User
        User data for creation or reactivation
    session : Session
        Database session dependency

    Returns
    -------
    User
        The created or reactivated user object

    Raises
    ------
    HTTPException
        If user with email already exists and is active
    """
    existing_user = user_CRUD.get_existing_email(session, user_data.email)
    if existing_user:
        if existing_user.condition == ConditionEnum.DEACTIVATED:
            data = user_data.model_dump(exclude={"id", "email", "condition"})
            data["condition"] = ConditionEnum.ACTIVE
            return user_CRUD.update(session, existing_user.id, data)
        raise HTTPException(
            status_code=422,
            detail=(f"User with email {user_data.email} already exists and is active."),
        )
    user_data.id = None  # Remove the id from the request body for auto-increment
    if not isinstance(
        user_data.birth_date, date
    ):  # Needed for SQLite to create the object in testing
        user_data.birth_date = date.fromisoformat(user_data.birth_date)
    user_data.condition = ConditionEnum.ACTIVE  # Default to active
    return user_CRUD.create(session, user_data)


@router.get("/{email_or_id}/allergies", response_model=list[Allergy])
async def get_user_allergies(
    email_or_id: str | int, session: Session = Depends(get_session)
) -> list[Allergy]:
    """Get all allergies for a user.

    Parameters
    ----------
    email_or_id : str | int
        Email address or user ID of the user
    session : Session
        Database session dependency

    Returns
    -------
    list[Allergy]
        List of allergy objects associated with the user
    """
    return user_CRUD.get_allergies(session, email_or_id)


@router.post("/{user_id}/allergies", response_model=list[Allergy])
async def add_allergy(
    user_id: int, allergy_name: str, session: Session = Depends(get_session)
) -> list[Allergy]:
    """Add an allergy to a user.

    Parameters
    ----------
    user_id : int
        ID of the user to add allergy to
    allergy_name : str
        Name of the allergy to add
    session : Session
        Database session dependency

    Returns
    -------
    list[Allergy]
        Updated list of allergies for the user
    """
    return user_CRUD.add_allergy(session, user_id, allergy_name)


@router.delete("/{user_id}/allergies", response_model=list[Allergy])
async def delete_allergy(
    user_id: int, allergy_name: str, session: Session = Depends(get_session)
) -> list[Allergy]:
    """Delete an allergy from a user.

    Parameters
    ----------
    user_id : int
        ID of the user to remove allergy from
    allergy_name : str
        Name of the allergy to remove
    session : Session
        Database session dependency

    Returns
    -------
    list[Allergy]
        Updated list of allergies for the user
    """
    return user_CRUD.delete_allergy(session, user_id, allergy_name)
