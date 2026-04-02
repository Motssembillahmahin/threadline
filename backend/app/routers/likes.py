import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.middleware.auth_middleware import get_current_user
from app.models.comment import Comment
from app.models.like import CommentLike, PostLike, ReplyLike
from app.models.post import Post
from app.models.reply import Reply
from app.models.user import User
from app.schemas.comment import LikedUserSchema

router = APIRouter(prefix="/api/likes", tags=["likes"])


# ─── Post likes ──────────────────────────────────────────────────────────────

@router.post("/post/{post_id}", status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    post_res = await session.execute(select(Post).where(Post.id == post_id))
    post = post_res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")

    existing = await session.execute(
        select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == current_user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="already_liked")

    session.add(PostLike(post_id=post_id, user_id=current_user.id))
    post.like_count = post.like_count + 1
    session.add(post)
    await session.commit()
    return {"like_count": post.like_count}


@router.delete("/post/{post_id}", status_code=status.HTTP_200_OK)
async def unlike_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    post_res = await session.execute(select(Post).where(Post.id == post_id))
    post = post_res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")

    existing = await session.execute(
        select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == current_user.id)
    )
    like = existing.scalar_one_or_none()
    if not like:
        raise HTTPException(status_code=404, detail="not_liked")

    await session.delete(like)
    if post.like_count > 0:
        post.like_count = post.like_count - 1
    session.add(post)
    await session.commit()
    return {"like_count": post.like_count}


@router.get("/post/{post_id}/users", response_model=List[LikedUserSchema])
async def post_liked_by(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    rows = await session.execute(
        select(User).join(PostLike, PostLike.user_id == User.id).where(PostLike.post_id == post_id)
    )
    return rows.scalars().all()


# ─── Comment likes ────────────────────────────────────────────────────────────

@router.post("/comment/{comment_id}", status_code=status.HTTP_201_CREATED)
async def like_comment(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = res.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="comment_not_found")

    existing = await session.execute(
        select(CommentLike).where(CommentLike.comment_id == comment_id, CommentLike.user_id == current_user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="already_liked")

    session.add(CommentLike(comment_id=comment_id, user_id=current_user.id))
    comment.like_count = comment.like_count + 1
    session.add(comment)
    await session.commit()
    return {"like_count": comment.like_count}


@router.delete("/comment/{comment_id}", status_code=status.HTTP_200_OK)
async def unlike_comment(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = res.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="comment_not_found")

    existing = await session.execute(
        select(CommentLike).where(CommentLike.comment_id == comment_id, CommentLike.user_id == current_user.id)
    )
    like = existing.scalar_one_or_none()
    if not like:
        raise HTTPException(status_code=404, detail="not_liked")

    await session.delete(like)
    if comment.like_count > 0:
        comment.like_count = comment.like_count - 1
    session.add(comment)
    await session.commit()
    return {"like_count": comment.like_count}


@router.get("/comment/{comment_id}/users", response_model=List[LikedUserSchema])
async def comment_liked_by(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    rows = await session.execute(
        select(User).join(CommentLike, CommentLike.user_id == User.id).where(CommentLike.comment_id == comment_id)
    )
    return rows.scalars().all()


# ─── Reply likes ──────────────────────────────────────────────────────────────

@router.post("/reply/{reply_id}", status_code=status.HTTP_201_CREATED)
async def like_reply(
    reply_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Reply).where(Reply.id == reply_id))
    reply = res.scalar_one_or_none()
    if not reply:
        raise HTTPException(status_code=404, detail="reply_not_found")

    existing = await session.execute(
        select(ReplyLike).where(ReplyLike.reply_id == reply_id, ReplyLike.user_id == current_user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="already_liked")

    session.add(ReplyLike(reply_id=reply_id, user_id=current_user.id))
    reply.like_count = reply.like_count + 1
    session.add(reply)
    await session.commit()
    return {"like_count": reply.like_count}


@router.delete("/reply/{reply_id}", status_code=status.HTTP_200_OK)
async def unlike_reply(
    reply_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Reply).where(Reply.id == reply_id))
    reply = res.scalar_one_or_none()
    if not reply:
        raise HTTPException(status_code=404, detail="reply_not_found")

    existing = await session.execute(
        select(ReplyLike).where(ReplyLike.reply_id == reply_id, ReplyLike.user_id == current_user.id)
    )
    like = existing.scalar_one_or_none()
    if not like:
        raise HTTPException(status_code=404, detail="not_liked")

    await session.delete(like)
    if reply.like_count > 0:
        reply.like_count = reply.like_count - 1
    session.add(reply)
    await session.commit()
    return {"like_count": reply.like_count}


@router.get("/reply/{reply_id}/users", response_model=List[LikedUserSchema])
async def reply_liked_by(
    reply_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    rows = await session.execute(
        select(User).join(ReplyLike, ReplyLike.user_id == User.id).where(ReplyLike.reply_id == reply_id)
    )
    return rows.scalars().all()
