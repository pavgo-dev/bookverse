from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import get_current_user
from app.models.user import UserOrm
from app.schemas.auth import TokenResponse, UserLogin
from app.schemas.response import (
    CURRENT_USER_RESPONSES,
    ConfirmPasswordErrorResponse,
    CredentialsErrorResponse,
    EmailExistsErrorResponse,
)
from app.schemas.user import CreateUser, UserPasswordUpdate, UserProfileUpdate, UserResponse
from app.service import user as user_service

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": EmailExistsErrorResponse,
            "description": "The email is already registered",
        }
    },
    summary="Register a new user",
)
async def register_user(user_data: CreateUser, session: AsyncSession = Depends(get_async_session)):
    return await user_service.create_user(user_data, session)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": CredentialsErrorResponse,
            "description": "Invalid login credentials",
        }
    },
    summary="User login and token generation",
)
async def login_user(login_data: UserLogin, session: AsyncSession = Depends(get_async_session)):
    return await user_service.login_user(login_data, session)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={**CURRENT_USER_RESPONSES},
    summary="Get current user profile",
)
async def get_user_profile(current_user: UserOrm = Depends(get_current_user)):
    return current_user


@router.patch(
    "/me/profile",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        **CURRENT_USER_RESPONSES,
        status.HTTP_409_CONFLICT: {
            "model": EmailExistsErrorResponse,
            "description": "The email is already registered",
        },
    },
    summary="Update user profile data",
)
async def update_user(
    data: UserProfileUpdate,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await user_service.update_user(data, current_user, session)


@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **CURRENT_USER_RESPONSES,
        status.HTTP_400_BAD_REQUEST: {
            "model": ConfirmPasswordErrorResponse,
            "description": "The provided password confirmations do not match or old password is wrong.",
        },
    },
    summary="Change user password",
)
async def update_user_password(
    data: UserPasswordUpdate,
    current_user: UserOrm = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    await user_service.update_password(data, current_user, session)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**CURRENT_USER_RESPONSES},
    summary="Delete current user account",
)
async def delete_user(
    current_user: UserOrm = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)
):
    await user_service.delete_user(current_user, session)
