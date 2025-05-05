from sqlalchemy.orm import Session
from app.models import User, Book, Borrow
from app.schemas import UserCreate, BookCreate, BorrowCreate
from app.auth import get_password_hash
from datetime import datetime

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_book(db: Session, book: BookCreate):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Book).offset(skip).limit(limit).all()

def get_book(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()

def update_book(db: Session, book_id: int, book: BookCreate):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book:
        for key, value in book.dict().items():
            setattr(db_book, key, value)
        db.commit()
        db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book:
        db.delete(db_book)
        db.commit()
    return db_book

def create_borrow(db: Session, borrow: BorrowCreate):
    db_borrow = Borrow(**borrow.dict())
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

def get_borrows(db: Session, user_id: int = None):
    query = db.query(Borrow)
    if user_id:
        query = query.filter(Borrow.user_id == user_id)
    return query.all()

def return_book(db: Session, borrow_id: int):
    db_borrow = db.query(Borrow).filter(Borrow.id == borrow_id).first()
    if db_borrow:
        db_borrow.return_date = datetime.utcnow()
        db.commit()
        db.refresh(db_borrow)
    return db_borrow

def get_user_borrowed_books(db: Session, user_id: int):
    return db.query(Borrow).filter(Borrow.user_id == user_id, Borrow.return_date.is_(None)).all()
