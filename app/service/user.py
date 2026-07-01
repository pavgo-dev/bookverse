import asyncio

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import create_access_token
from app.models.user import UserOrm
from app.repository import user as user_repository
from app.schemas.auth import TokenResponse, UserLogin
from app.schemas.user import CreateUser, UserPasswordUpdate, UserProfileUpdate
from app.utils import hash_password, verify_password


async def create_user(user_data: CreateUser, session: AsyncSession) -> UserOrm:
    existing_user = await user_repository.get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with {user_data.email} already exists",
        )

    hashed_pass = await asyncio.to_thread(
        hash_password, user_data.password.get_secret_value()
    )  # Синнхронная функция через to_thread, подсмотрел фишку, нужно проверить

    new_user = await user_repository.add_user(session, user_data, hashed_pass)
    await session.commit()
    await session.refresh(new_user)

    return new_user


async def login_user(login_data: UserLogin, session: AsyncSession) -> TokenResponse:
    user = await user_repository.get_user_by_email(session, login_data.email)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Password or email is not correct",
    )  # Одниаковая ошибка, от брутфорса

    if not user:
        raise credentials_exception

    is_password_correct = await asyncio.to_thread(
        verify_password, login_data.password.get_secret_value(), user.hashed_password
    )  # Судя по всему нужно отказаться от keyword аргументов и использовать позиционные

    if not is_password_correct:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is banned",
        )

    token_payload = {"sub": str(user.id)}
    token = create_access_token(data=token_payload)

    return TokenResponse(access_token=token)


async def update_user(data: UserProfileUpdate, current_user: UserOrm, session: AsyncSession) -> UserOrm:
    update_data = data.model_dump(exclude_unset=True)
    if "full_name" in update_data and update_data["full_name"] == current_user.full_name:
        update_data.pop("full_name")
    if "email" in update_data and update_data["email"] == current_user.email:
        update_data.pop("email")
    if not update_data:
        return current_user

    if "email" in update_data:
        email_owner = await user_repository.get_user_by_email(session, update_data["email"])
        if email_owner:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=f"User with {update_data['email']} already exists"
            )

    await user_repository.update_user_attributes(session, current_user, update_data)
    await session.commit()
    await session.refresh(current_user)

    return current_user


async def update_password(data: UserPasswordUpdate, current_user: UserOrm, session: AsyncSession) -> None:
    is_password_correct = await asyncio.to_thread(
        verify_password, data.old_password.get_secret_value(), current_user.hashed_password
    )
    if not is_password_correct:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")

    hashed_pass = await asyncio.to_thread(hash_password, data.new_password.get_secret_value())

    await user_repository.update_user_attributes(session, current_user, {"hashed_password": hashed_pass})
    await session.commit()

    return None


async def delete_user(current_user: UserOrm, session: AsyncSession) -> None:
    await user_repository.delete_user(session, current_user)
    await session.commit()
