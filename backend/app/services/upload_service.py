import asyncio
import uuid
import os
import aiofiles
from fastapi import HTTPException, UploadFile

import cloudinary
import cloudinary.uploader

from app.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def save_upload(file: UploadFile) -> str:
    """Save uploaded image. Returns a Cloudinary URL or a local path."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="unsupported_image_type")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="file_too_large")

    if settings.CLOUDINARY_URL:
        return await _upload_to_cloudinary(content)
    return await _save_locally(content, file.filename)


async def _upload_to_cloudinary(content: bytes) -> str:
    """Upload to Cloudinary and return the secure URL."""
    cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL)

    result = await asyncio.to_thread(
        cloudinary.uploader.upload,
        content,
        folder="threadline",
        resource_type="image",
    )
    return result["secure_url"]


async def _save_locally(content: bytes, filename: str) -> str:
    """Save to local filesystem and return the relative URL path."""
    ext = filename.rsplit(".", 1)[-1].lower() if filename and "." in filename else "jpg"
    dest_filename = f"{uuid.uuid4()}.{ext}"
    dest = os.path.join(settings.UPLOAD_DIR, dest_filename)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    async with aiofiles.open(dest, "wb") as f:
        await f.write(content)

    return f"/static/uploads/{dest_filename}"
