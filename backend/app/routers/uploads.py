from fastapi import APIRouter, Depends, UploadFile, status

from ..images import save_upload
from ..schemas import UploadOut
from ..security import require_admin

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/image", response_model=UploadOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def upload_image(file: UploadFile):
    return {"url": await save_upload(file)}
