from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.resume_parser import extract_text
from app.services.resume_data_extractor import extract_resume_data
from app.schemas.resume import ResumeParseResponse

router = APIRouter(
    prefix="/api/v1/resume",
    tags=["Resume"]
)


@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume(file: UploadFile = File(...)):
    filename = file.filename or ""

    if not filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
        )

    file_content = await file.read()

    try:
        extracted_text = extract_text(file_content, filename)
        parsed_data = extract_resume_data(extracted_text)
        return parsed_data

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        await file.close()