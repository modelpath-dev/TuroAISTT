import os
from typing import Annotated, TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
import json
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class TranscriptSegment(TypedDict):
    text: str
    start: float
    end: float

class AgentState(TypedDict):
    audio_path: str
    body_part: str
    raw_transcript: str
    segments: List[TranscriptSegment]
    refined_transcript: str
    template_id: str
    extracted_data: Dict[str, Any]
    iteration_count: int
    missing_fields: List[str]
    errors: List[str]

# LLMs
# Using OpenAI GPT-4o for medical context refinement and extraction
llm = ChatOpenAI(model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_node(state: AgentState):
    """Pass-through for raw transcription data."""
    return {"raw_transcript": state.get("raw_transcript", "")}

def refine_transcript_node(state: AgentState):
    """Refine transcript with a single-pass AI check for spelling and medical context."""
    system_msg = SystemMessage(content=f"""
    You are a medical editor. Your task is to check the following radiology transcription for {state['body_part']} and fix any spelling mistakes or phonetic errors.
    
    Guidelines:
    1. Only fix spelling and obvious transcription errors (e.g., 'adrenal' instead of 'a drain all').
    2. Ensure medical terms are correct for a {state['body_part']} study.
    3. Do NOT rewrite the entire report; keep the original structure.
    4. Return ONLY the corrected transcript text.
    """)
    
    human_msg = HumanMessage(content=f"Raw Transcript: {state['raw_transcript']}")
    response = llm.invoke([system_msg, human_msg])
    return {"refined_transcript": response.content}

def extract_data_node(state: AgentState):
    """Extract structured data based on the CAP template JSON schema with a 3-pass self-verification loop."""
    template_path = Path(f"CAP templates/JSON_Output/{state['template_id']}.json")
    if not template_path.exists():
        return {"errors": ["Template not found"]}
    
    with open(template_path, 'r') as f:
        template_schema = json.load(f)
    
    # Analyze transcript line-by-line for extraction
    full_transcript = state['refined_transcript']
    
    # Get current iteration
    iteration = state.get("iteration_count", 0) + 1
    current_extracted = state.get("extracted_data", {})
    
    # Sophisticated System Prompt - Questionnaire Style
    system_msg = SystemMessage(content=f"""
    You are a specialized Medical Oncology Data Extraction AI. 
    CURRENT TASK: Extract clinical data for a {state['body_part']} examination by treating the CAP protocol as a CLINICAL QUESTIONNAIRE.
    
    INPUT DATA:
    1. Body Part: {state['body_part']}
    2. Questionnaire (CAP Protocol): {json.dumps(template_schema.get('sections', []), indent=1)}
    3. Transcription: {full_transcript}
    
    CRITICAL INSTRUCTIONS:
    - Treat each 'field' in the questionnaire as a question.
    - Match terminology accurately to the protocol fields.
    - If a field is explicitly stated or strongly implied by medical context, extract the technical 'value' from the corresponding 'options' in the questionnaire.
    - If it's free_text, extract the exact specified details.
    - IF INFORMATION IS MISSING OR NOT FOUND: Set the value exactly to "not determined".
    - PREVIOUS PASS DATA (Current state): {json.dumps(current_extracted, indent=1)}
    
    ITERATION PASS: {iteration}/3
    In this pass, focus specifically on fields currently marked "not determined" or missing. Double-check the transcript lines to ensure no subtle mention was missed.
    
    OUTPUT FORMAT:
    Return ONLY a valid JSON object where keys are the 'field_id' from the questionnaire and values are the extracted clinical findings (technical values or free text) or "not determined".
    """)
    
    human_msg = HumanMessage(content=f"Focus on refining the extraction. Transcription lines: \n{full_transcript}")
    response = llm.invoke([system_msg, human_msg])
    
    try:
        # Strip potential markdown code blocks
        clean_content = response.content.replace("```json", "").replace("```", "").strip()
        new_extracted = json.loads(clean_content)
        # Merge with existing data (preferring new extractions)
        merged_extracted = {**current_extracted, **new_extracted}
    except Exception as e:
        print(f"Extraction JSON error: {e}")
        merged_extracted = current_extracted
    
    # Identify fields still missing
    all_field_ids = []
    for section in template_schema.get('sections', []):
        for field in section.get('fields', []):
            all_field_ids.append(field['field_id'])
            
    missing_now = [fid for fid in all_field_ids if merged_extracted.get(fid) == "not determined" or fid not in merged_extracted]
    
    return {
        "extracted_data": merged_extracted, 
        "iteration_count": iteration, 
        "missing_fields": missing_now
    }

def should_continue_extraction(state: AgentState):
    """Route to continue loop or end extraction after 3 passes or no missing fields."""
    if state.get("iteration_count", 0) >= 3:
        return "end"
    if not state.get("missing_fields"):
        return "end"
    return "continue"

def create_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("transcribe", transcribe_node)
    workflow.add_node("refine", refine_transcript_node)
    workflow.add_node("extract", extract_data_node)
    
    workflow.set_entry_point("transcribe")
    workflow.add_edge("transcribe", "refine")
    workflow.add_edge("refine", "extract")
    
    workflow.add_conditional_edges(
        "extract",
        should_continue_extraction,
        {
            "continue": "extract",
            "end": END
        }
    )
    
    return workflow.compile()

workflow = create_workflow()
