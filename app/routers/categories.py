from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryOut
from app.crud import category as category_crud
from app.auth.dependencies import get_current_active_superuser

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return category_crud.get_categories(db)


@router.post("/", response_model=CategoryOut, dependencies=[Depends(get_current_active_superuser)])
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    return category_crud.create_category(db, category_in)
