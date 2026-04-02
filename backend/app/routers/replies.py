import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.middleware.auth_middleware import get_current_user
from app.models.comment import Comment
from app.models.like import ReplyLike
from app.models.reply import Reply
from app.models.user import User
from app.schemas.comment import AuthorSchema, ReplyCreateRequest, ReplyResponse

router = APIRouter(prefix="/api/replies", tags=["replies"])


async def _build(reply: Reply, author: User, current_user: User, session: AsyncSession) -> ReplyResponse:
    liked = await session.execute(
        select(ReplyLike).where(ReplyLike.reply_id == reply.id, ReplyLike.user_id == current_user.id)
    )
    return ReplyResponse(
        id=reply.id,
        content=reply.content,
        like_count=reply.like_count,
        created_at=reply.created_at,
        author=AuthorSchema(id=author.id, first_name=author.first_name, last_name=author.last_name, avatar_url=author.avatar_url),
        liked_by_me=liked.scalar_one_or_none() is not None,
    )


@router.get("/comment/{comment_id}", response_model=List[ReplyResponse])
async def list_replies(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Reply, User)
        .join(User, Reply.user_id == User.id)
        .where(Reply.comment_id == comment_id)
        .order_by(Reply.created_at.asc())
    )
    rows = await session.execute(stmt)
    return [await _build(r, a, current_user, session) for r, a in rows.all()]


@router.post("/comment/{comment_id}", response_model=ReplyResponse, status_code=status.HTTP_201_CREATED)
async def create_reply(
    comment_id: uuid.UUID,
    body: ReplyCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    comment_res = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = comment_res.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="comment_not_found")

    reply = Reply(comment_id=comment_id, user_id=current_user.id, content=body.content)
    session.add(reply)
    comment.reply_count = comment.reply_count + 1
    session.add(comment)
    await session.commit()
    await session.refresh(reply)
    return await _build(reply, current_user, current_user, session)


@router.delete("/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reply(
    reply_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Reply).where(Reply.id == reply_id))
    reply = res.scalar_one_or_none()
    if not reply:
        raise HTTPException(status_code=404, detail="reply_not_found")
    if reply.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")

    comment_res = await session.execute(select(Comment).where(Comment.id == reply.comment_id))
    comment = comment_res.scalar_one_or_none()
    if comment and comment.reply_count > 0:
        comment.reply_count = comment.reply_count - 1
        session.add(comment)

    await session.delete(reply)
    await session.commit()
