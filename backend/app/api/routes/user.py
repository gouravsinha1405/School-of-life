from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import UpdateLanguageRequest, UserOut
from app.schemas.common import Language
from app.services.user_service import delete_user_account, export_user_data

router = APIRouter(tags=["user"])


@router.get("/api/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return UserOut(id=str(user.id), email=user.email, preferred_language=Language(user.preferred_language))


@router.patch("/api/me", response_model=UserOut)
def update_me(
    data: UpdateLanguageRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user.preferred_language = data.preferred_language.value
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(id=str(user.id), email=user.email, preferred_language=Language(user.preferred_language))


@router.get("/api/export")
def export_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = export_user_data(db, user.id)
    return data


@router.delete("/api/account", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    delete_user_account(db, user.id)
    response.delete_cookie("access_token")
    return None
