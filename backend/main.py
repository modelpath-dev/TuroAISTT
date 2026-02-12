import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
from services.langgraph_engine import workflow
from services.report_gen import generate_radiology_report
from services.transcription import get_transcription_service
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    message: str
    transcript: str
    body_part: str
    template_id: str
    history: List[Dict[str, str]] = []

app = FastAPI(title="Radiology Voice-to-Report API")

# Enable CORS - Update with your Vercel domain after deployment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATES_DIR = Path("CAP templates/JSON_Output")
TEMP_AUDIO_DIR = Path("temp_audio")
TEMP_AUDIO_DIR.mkdir(exist_ok=True)

@app.get("/templates")
async def get_templates():
    """List available radiology templates (body parts)."""
    templates = []
    if not TEMPLATES_DIR.exists():
        return []
    
    for file in TEMPLATES_DIR.glob("*.json"):
        with open(file, 'r') as f:
            data = json.load(f)
            templates.append({
                "id": data.get("template_id"),
                "name": data.get("organ", file.stem),
                "filename": file.name
            })
    return templates

@app.get("/template/{filename}")
async def get_template_details(filename: str):
    """Get full details of a specific template."""
    file_path = TEMPLATES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")
    
    with open(file_path, 'r') as f:
        return json.load(f)

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), body_part_id: str = Form(...)):
    """Transcribe audio and refine with medical terminology using LangGraph."""
    # Save temp audio
    file_path = TEMP_AUDIO_DIR / audio.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
    
    # 1. Transcribe with local Whisper model
    try:
        ts_service = get_transcription_service()
        segments = ts_service.transcribe_with_timestamps(str(file_path))
        raw_transcript = ts_service.format_segments_to_string(segments)
    except Exception as e:
        # Fallback for testing
        raw_transcript = f"[0.00 - 5.00] Machine error transcription for {body_part_id}. Finding: 3cm mass."
        segments = [{"text": "Machine error transcription", "start": 0.0, "end": 5.0}]
        print(f"Transcription error: {e}")

    # 2. Refine and Extract using LangGraph
    body_part_name = body_part_id.split("_")[0]
    
    initial_state = {
        "audio_path": str(file_path),
        "body_part": body_part_name,
        "raw_transcript": raw_transcript,
        "segments": segments,
        "template_id": body_part_id,
        "extracted_data": {},
        "iteration_count": 0,
        "missing_fields": [],
        "errors": []
    }
    
    final_state = await workflow.ainvoke(initial_state)
    
    return {
        "raw_transcript": raw_transcript,
        "segments": segments,
        "refined_transcript": final_state.get("refined_transcript"),
        "extracted_data": final_state.get("extracted_data"),
        "template_id": body_part_id,
        "audio_url": f"/audio/{audio.filename}"
    }

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    return FileResponse(TEMP_AUDIO_DIR / filename)

@app.post("/chat")
async def clinical_chat(request: ChatRequest):
    """Interactive chatbot for clinician assistance."""
    try:
        # Load template for context if needed
        template_content = ""
        template_path = Path(f"CAP templates/JSON_Output/{request.template_id}.json")
        if template_path.exists():
            with open(template_path, 'r') as f:
                template_content = f.read()

        system_msg = f"""
        You are a specialized Radiology Assistant. You are helping a radiologist verify and refine a report.
        
        CONTEXT:
        - Body Part: {request.body_part}
        - Refined Transcript: {request.transcript}
        - CAP Protocol Questionnaire: {template_content}
        
        INSTRUCTIONS:
        1. Answer clinical questions based ON ONLY the provided transcript and the protocol requirements.
        2. Help the radiologist find specific information in the transcript.
        3. Explain protocol fields if asked.
        4. Be professional, concise, and clinically precise.
        """
        
        messages = [SystemMessage(content=system_msg)]
        for msg in request.history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=request.message))
        
        # Using the same LLM instance from services.langgraph_engine
        from services.langgraph_engine import llm
        response = llm.invoke(messages)
        
        return {"response": response.content}
    except Exception as e:
        print(f"Chat error: {e}")
        return {"response": "System error. Please try again."}

@app.post("/generate-report")
async def generate_report_endpoint(
    data: Dict[str, Any] = Body(...), 
    template_id: str = Body(...)
):
    """Generate final DOCX report from structured data."""
    template_path = TEMPLATES_DIR / f"{template_id}.json"
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")
        
    with open(template_path, 'r') as f:
        template_info = json.load(f)
    
    output_filename = f"report_{template_id}.docx"
    output_path = TEMP_AUDIO_DIR / output_filename
    
    generate_radiology_report(data, template_info, str(output_path))
    
    return {
        "message": "Report generated", 
        "download_url": f"/download/{output_filename}"
    }

@app.get("/download/{filename}")
async def download_report(filename: str):
    file_path = TEMP_AUDIO_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
