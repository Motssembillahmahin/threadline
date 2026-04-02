import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.middleware.auth_middleware import get_current_user
from app.models.comment import Comment
from app.models.like import CommentLike
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import AuthorSchema, CommentCreateRequest, CommentResponse

router = APIRouter(prefix="/api/comments", tags=["comments"])


async def _build(comment: Comment, author: User, current_user: User, session: AsyncSession) -> CommentResponse:
    liked = await session.execute(
        select(CommentLike).where(CommentLike.comment_id == comment.id, CommentLike.user_id == current_user.id)
    )
    return CommentResponse(
        id=comment.id,
        content=comment.content,
        like_count=comment.like_count,
        reply_count=comment.reply_count,
        created_at=comment.created_at,
        author=AuthorSchema(id=author.id, first_name=author.first_name, last_name=author.last_name, avatar_url=author.avatar_url),
        liked_by_me=liked.scalar_one_or_none() is not None,
    )


@router.get("/post/{post_id}", response_model=List[CommentResponse])
async def list_comments(
    post_id: uuid.UUID,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Comment, User)
        .join(User, Comment.user_id == User.id)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    rows = await session.execute(stmt)
    return [await _build(c, a, current_user, session) for c, a in rows.all()]


@router.post("/post/{post_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: uuid.UUID,
    body: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    post_res = await session.execute(select(Post).where(Post.id == post_id))
    post = post_res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")

    comment = Comment(post_id=post_id, user_id=current_user.id, content=body.content)
    session.add(comment)
    # atomically increment comment_count
    post.comment_count = post.comment_count + 1
    session.add(post)
    await session.commit()
    await session.refresh(comment)
    return await _build(comment, current_user, current_user, session)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = res.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="comment_not_found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")

    post_res = await session.execute(select(Post).where(Post.id == comment.post_id))
    post = post_res.scalar_one_or_none()
    if post and post.comment_count > 0:
        post.comment_count = post.comment_count - 1
        session.add(post)

    await session.delete(comment)
    await session.commit()
