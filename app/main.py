import shutil
import tempfile
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import UnidentifiedImageError
from sqlalchemy.exc import SQLAlchemyError

from app.configs.config import (
    ATTRIBUTOR_CHECKPOINT_PATH,
    DETECTOR_CHECKPOINT_PATH,
)
from app.schemas.predictions import AnalysisResult
from app.services.analysis_service import AnalysisService
from app.repositories.analysis_repository import AnalysisRepository
from app.database.database import Base, engine, SessionLocal


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the models once when the API starts, not for every uploaded image.
    app.state.analysis_service = AnalysisService(
        detector_checkpoint_path=str(DETECTOR_CHECKPOINT_PATH),
        attributor_checkpoint_path=str(ATTRIBUTOR_CHECKPOINT_PATH),
    )

    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="ImageTrust API",
    description="Analyze images for likely AI generation and source attribution.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception(
        "UNHANDLED ERROR on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResult)
def analyze_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=415,
            detail="Please upload an image file.",
        )

    suffix = Path(file.filename or "upload.png").suffix or ".png"
    temp_path = None
    db = SessionLocal()

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temporary_file:
            shutil.copyfileobj(file.file, temporary_file)
            temp_path = Path(temporary_file.name)

        result = app.state.analysis_service.analyze(str(temp_path))

        repository = AnalysisRepository(db=db)
        repository.save(
            image_file_name=Path(file.filename or "upload").name,
            result=result,
        )

        return result

    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file could not be read as an image.",
        ) from error

    except SQLAlchemyError as error:
        db.rollback()
        logger.exception("DATABASE ERROR during image analysis")
        raise HTTPException(
            status_code=500,
            detail="Database error while saving the analysis.",
        ) from error

    except Exception as error:
        logger.exception("ANALYZE FAILED")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {error}",
        ) from error

    finally:
        db.close()
        file.file.close()

        if temp_path and temp_path.exists():
            temp_path.unlink()
