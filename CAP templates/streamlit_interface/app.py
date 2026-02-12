import streamlit as st
import os
import sys
import shutil

# Add root directory to sys.path for local imports
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_path not in sys.path:
    sys.path.append(root_path)

from utils.templates import load_index, load_template, render_template_form
from utils.llm import generate_report
from transcriber import ContextAwareTranscriber
from extractor import ReportRefiner, ProtocolClassifier, DocxGenerator
from verifier import TranscriptionVerifier

# Initialize Engines
transcriber = ContextAwareTranscriber()
refiner = ReportRefiner()
classifier = ProtocolClassifier()
verifier = TranscriptionVerifier()
docx_gen = DocxGenerator()

# Page Config
st.set_page_config(
    page_title="V2 CAP AI Master Assistant",
    page_icon="🤖",
    layout="wide"
)

# Session State
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'selected_template' not in st.session_state:
    st.session_state.selected_template = None
if 'filled_data' not in st.session_state:
    st.session_state.filled_data = {}

def main():
    st.title("🤖 Radiology & Pathology V2: Hyper-Accuracy Engine")
    
    with st.sidebar:
        st.header("⚙️ Processing Settings")
        do_noise_reduction = st.checkbox("Enable Background Noise Filtering", value=True)
        do_verification = st.checkbox("Enable LangGraph Verification (Multi-Model)", value=True)
        
        st.divider()
        st.header("📂 Protocol Selection")
        index = load_index()
        template_names = {t['organ']: t for t in index['templates'] if t['organ']}
        
        manual_select = st.selectbox("Manually Select Protocol (or let AI decide)", options=["Automatic Identification"] + list(template_names.keys()))
        
        st.divider()
        audio_file = st.file_uploader("Upload Medical Dictation", type=["mp3", "wav", "m4a"])
        
        if audio_file and st.button("🚀 Process & Generate Report"):
            with st.spinner("Processing..."):
                # Save temp
                os.makedirs("temp_audio", exist_ok=True)
                temp_path = os.path.join("temp_audio", audio_file.name)
                with open(temp_path, "wb") as f:
                    f.write(audio_file.getbuffer())
                
                try:
                    # 1. Transcribe (with optional noise reduction)
                    st.toast("Transcribing...")
                    raw_res = transcriber.transcribe(temp_path, "GENERAL", preprocess=do_noise_reduction)
                    transcript = raw_res.raw_text
                    
                    # 2. Verify (LangGraph)
                    if do_verification:
                        st.toast("Verifying with LangGraph...")
                        transcript = verifier.verify(transcript, "GENERAL")
                    
                    # 3. Classify
                    if manual_select == "Automatic Identification":
                        st.toast("Identifying Protocol...")
                        meta = classifier.classify(transcript, index)
                    else:
                        meta = template_names[manual_select]
                    
                    st.session_state.selected_template = load_template(meta['filename'])
                    
                    # 4. Extract
                    st.toast("Extracting Structured Data...")
                    report = refiner.refine_and_extract(transcript, st.session_state.selected_template)
                    st.session_state.filled_data = report.extracted_data
                    
                    # Add to chat
                    st.session_state.messages.append({"role": "assistant", "content": f"**Protocol Identified:** {meta['organ']}\n\n**Final Transcript:**\n{transcript}"})
                    
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                st.rerun()

    # Main Area
    if st.session_state.selected_template:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("📝 Extracted Data")
            st.session_state.filled_data = render_template_form(st.session_state.selected_template, st.session_state.filled_data)
            
        with col2:
            st.header("📄 Final Report & Export")
            report_text = generate_report(st.session_state.selected_template, st.session_state.filled_data)
            st.text_area("Report Preview", value=report_text, height=400)
            
            # DOCX Export
            if st.button("Generate Final CAP DOCX"):
                with st.spinner("Populating Word Template..."):
                    template_fn = st.session_state.selected_template['template_id'] + ".docx"
                    template_path = os.path.join(root_path, "CAP templates", template_fn)
                    output_path = f"Final_Report_{st.session_state.selected_template['template_id']}.docx"
                    
                    if os.path.exists(template_path):
                        docx_gen.generate(
                            template_path, 
                            st.session_state.filled_data, 
                            st.session_state.selected_template['organ'],
                            output_path
                        )
                        with open(output_path, "rb") as f:
                            st.download_button("Download DOCX", f, file_name=output_path)
                    else:
                        st.error(f"Template file {template_fn} not found in CAP templates directory.")

if __name__ == "__main__":
    main()
