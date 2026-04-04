import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, File, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.middleware.auth_middleware import get_current_user
from app.models.post import Post
from app.models.user import User
from app.models.like import PostLike
from app.schemas.post import AuthorSchema, PostResponse, PostUpdateRequest
from app.services.upload_service import save_upload

router = APIRouter(prefix="/api/posts", tags=["posts"])


async def _build_response(post: Post, author: User, current_user: User, session: AsyncSession) -> PostResponse:
    liked = await session.execute(
        select(PostLike).where(PostLike.post_id == post.id, PostLike.user_id == current_user.id)
    )
    return PostResponse(
        id=post.id,
        content=post.content,
        image_url=post.image_url,
        visibility=post.visibility,
        like_count=post.like_count,
        comment_count=post.comment_count,
        created_at=post.created_at,
        author=AuthorSchema(
            id=author.id,
            first_name=author.first_name,
            last_name=author.last_name,
            avatar_url=author.avatar_url,
        ),
        liked_by_me=liked.scalar_one_or_none() is not None,
    )


@router.get("", response_model=List[PostResponse])
async def get_feed(
    cursor: Optional[str] = Query(default=None),
    limit: int = Query(default=10, le=50),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Cursor-based feed: public posts + own posts, newest first."""
    stmt = (
        select(Post, User)
        .join(User, Post.user_id == User.id)
        .where(
            (Post.visibility == "public") | (Post.user_id == current_user.id)
        )
    )
    if cursor:
        cursor_dt = datetime.fromisoformat(cursor)
        stmt = stmt.where(Post.created_at < cursor_dt)

    stmt = stmt.order_by(Post.created_at.desc()).limit(limit)
    rows = await session.execute(stmt)
    results = rows.all()

    posts = []
    for post, author in results:
        posts.append(await _build_response(post, author, current_user, session))
    return posts


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    content: Optional[str] = Form(default=None),
    visibility: str = Form(default="public"),
    image: Optional[UploadFile] = File(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not content and not image:
        raise HTTPException(status_code=400, detail="post_must_have_content_or_image")
    if visibility not in ("public", "private"):
        raise HTTPException(status_code=400, detail="invalid_visibility")

    image_url = None
    if image and image.filename:
        image_url = await save_upload(image)

    post = Post(
        user_id=current_user.id,
        content=content,
        image_url=image_url,
        visibility=visibility,
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return await _build_response(post, current_user, current_user, session)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Post, User).join(User, Post.user_id == User.id).where(Post.id == post_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="post_not_found")
    post, author = row
    if post.visibility == "private" and post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    return await _build_response(post, author, current_user, session)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: uuid.UUID,
    body: PostUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")

    if body.content is not None:
        post.content = body.content
    if body.visibility is not None:
        if body.visibility not in ("public", "private"):
            raise HTTPException(status_code=400, detail="invalid_visibility")
        post.visibility = body.visibility

    session.add(post)
    await session.commit()
    await session.refresh(post)
    return await _build_response(post, current_user, current_user, session)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    await session.delete(post)
    await session.commit()
