from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import Borrow, BorrowCreate
from app.crud import create_borrow, get_borrows, return_book
from app.auth import get_current_user, get_current_admin_user
from app.models import User

router = APIRouter(prefix="/borrows", tags=["borrows"])

@router.post("/", response_model=Borrow)
def create_borrow_endpoint(borrow: BorrowCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_borrow(db, borrow)

@router.get("/", response_model=List[Borrow])
def read_borrows(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return get_borrows(db)
    return get_borrows(db, current_user.id)

@router.put("/{borrow_id}", response_model=Borrow)
def return_book_endpoint(borrow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_borrow = return_book(db, borrow_id)
    if db_borrow is None:
        raise HTTPException(status_code=404, detail="Borrow record not found")
    return db_borrow
