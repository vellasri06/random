from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import io
import uuid

from .pipeline.chain import generate_mom_from_text
from .utils.pdf import render_mom_pdf
from . import config


class GenerateMoMRequest(BaseModel):
    transcript: str

class MoMSection(BaseModel):
    meeting_title: str
    date: Optional[str] = None
    attendees: List[str] = []
    executive_summary: str
    key_decisions: List[str]
    action_items: List[Dict[str, Optional[str]]]


def create_app() -> FastAPI:
    app = FastAPI(title=config.API_TITLE, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/generate-mom")
    async def generate_mom(transcript: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)) -> Any:
        try:
            raw_text = transcript or ""
            if file is not None:
                content = await file.read()
                try:
                    raw_text = content.decode("utf-8", errors="ignore")
                except Exception:
                    raw_text = content.decode(errors="ignore")

            if not raw_text or len(raw_text.strip()) == 0:
                raise HTTPException(status_code=400, detail="No transcript text provided")

            mom = await generate_mom_from_text(raw_text)

            # Save PDF
            pdf_id = str(uuid.uuid4())
            pdf_path = os.path.join(config.GENERATED_PDFS_DIR, f"{pdf_id}.pdf")
            os.makedirs(config.GENERATED_PDFS_DIR, exist_ok=True)
            render_mom_pdf(mom, pdf_path)

            return JSONResponse({"mom": mom, "pdf_id": pdf_id})
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/download/{pdf_id}")
    def download_pdf(pdf_id: str):
        pdf_path = os.path.join(config.GENERATED_PDFS_DIR, f"{pdf_id}.pdf")
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF not found")
        return FileResponse(pdf_path, media_type="application/pdf", filename=f"mom_{pdf_id}.pdf")

    return app


app = create_app()
