from fastapi import APIRouter

from src.routers import users, cities, posts

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(cities.router, prefix="/cities", tags=["cities"])
router.include_router(posts.router, prefix="/posts", tags=["posts"])
