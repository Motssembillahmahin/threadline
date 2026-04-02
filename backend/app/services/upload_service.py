import uuid
import os
import aiofiles
from fastapi import HTTPException, UploadFile

from app.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def save_upload(file: UploadFile) -> str:
    """Save uploaded image, return relative URL path."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="unsupported_image_type")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="file_too_large")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    dest = os.path.join(settings.UPLOAD_DIR, filename)

    async with aiofiles.open(dest, "wb") as f:
        await f.write(content)

    return f"/static/uploads/{filename}"
