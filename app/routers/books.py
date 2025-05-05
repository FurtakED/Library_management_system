from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import Book, BookCreate
from app.crud import create_book, get_books, get_book, update_book, delete_book
from app.auth import get_current_admin_user, get_current_user
from app.models import User

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=Book)
def create_book_endpoint(book: BookCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    return create_book(db, book)

@router.get("/", response_model=List[Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_books(db, skip, limit)

@router.get("/{book_id}", response_model=Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.put("/{book_id}", response_model=Book)
def update_book_endpoint(book_id: int, book: BookCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_book = update_book(db, book_id, book)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.delete("/{book_id}")
def delete_book_endpoint(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_book = delete_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}
