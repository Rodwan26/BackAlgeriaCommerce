from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from app.services.image_service import save_product_image

router = APIRouter()


@router.post("/upload/product-image")
def upload_product_image(
    image: UploadFile = File(...)
):
    filename = save_product_image(image)

    return {
        "filename": filename,
        "url": f"/uploads/products/{filename}",
    }