from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.models.schemas import UploadResponse
from app.security.permissions import require_permissions
from app.services.data_loader import DATASET_FILENAMES, reset_sample_data, save_uploaded_dataset


router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(
    category: str = Form(...),
    file: UploadFile = File(...),
    _user=Depends(require_permissions("*")),
) -> dict[str, object]:
    if category not in DATASET_FILENAMES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported category. Use one of: {', '.join(DATASET_FILENAMES)}",
        )

    rows_loaded = await save_uploaded_dataset(category, file)
    return {
        "category": category,
        "rows_loaded": rows_loaded,
        "message": f"Loaded {rows_loaded} rows for {category}.",
    }


@router.post("/upload/reset")
def reset_data(_user=Depends(require_permissions("*"))) -> dict[str, str]:
    reset_sample_data()
    return {"message": "Sample data regenerated."}
