from fastapi import FastAPI
from app.routers import books, users, borrows, recommendations
from app.database import engine
from app.models import Base

app = FastAPI(title="Library Management System")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router)
app.include_router(books.router)
app.include_router(borrows.router)
app.include_router(recommendations.router)
