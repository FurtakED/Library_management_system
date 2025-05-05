from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import get_borrows, get_books
from app.schemas import Book
from app.auth import get_current_user
from typing import List
from app.models import User

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/", response_model=List[Book])
def get_recommendations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Get all borrow records
    all_borrows = get_borrows(db)
    
    # Get current user's borrowed books
    user_borrows = get_borrows(db, current_user.id)
    user_book_ids = {borrow.book_id for borrow in user_borrows}
    
    # Find similar users
    similar_users = {}
    for borrow in all_borrows:
        if borrow.user_id != current_user.id:
            if borrow.book_id in user_book_ids:
                similar_users[borrow.user_id] = similar_users.get(borrow.user_id, 0) + 1
    
    # Get books borrowed by similar users
    recommended_book_ids = set()
    for borrow in all_borrows:
        if borrow.user_id in similar_users and borrow.book_id not in user_book_ids:
            recommended_book_ids.add(borrow.book_id)
    
    # Get book details
    recommended_books = []
    for book_id in recommended_book_ids:
        book = db.query(Book).filter(Book.id == book_id).first()
        if book:
            recommended_books.append(book)
    
    # Sort by relevance (number of similar users who borrowed)
    return sorted(recommended_books, key=lambda x: len([b for b in all_borrows if b.book_id == x.id]), reverse=True)[:5]
