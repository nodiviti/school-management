"""API Routes Package"""
from fastapi import APIRouter

# Import all routers
from app.routes.auth import router as auth_router
from app.routes.users import router as user_router
from app.routes.students import router as student_router
from app.routes.teachers import router as teacher_router
from app.routes.classes import router as class_router
from app.routes.subjects import router as subject_router
from app.routes.attendance import router as attendance_router
from app.routes.grades import router as grade_router
from app.routes.finance import router as finance_router
from app.routes.dormitory import router as dormitory_router
from app.routes.library import router as library_router
from app.routes.admin import router as admin_router

__all__ = [
    "auth_router",
    "user_router",
    "student_router",
    "teacher_router",
    "class_router",
    "subject_router",
    "attendance_router",
    "grade_router",
    "finance_router",
    "dormitory_router",
    "library_router",
    "admin_router"
]