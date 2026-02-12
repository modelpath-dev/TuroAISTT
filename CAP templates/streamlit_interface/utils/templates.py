import json
import os
import streamlit as st

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# JSON_Output is in CAP templates/, which is two levels up from this utils folder
OUTPUT_FOLDER = os.path.abspath(os.path.join(SCRIPT_DIR, "../../JSON_Output"))

def load_index():
    """Load the master index of templates."""
    index_path = os.path.join(OUTPUT_FOLDER, "index.json")
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Index not found at {index_path}. Run scraper first.")
    
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_template(filename):
    """Load a specific template JSON."""
    path = os.path.join(OUTPUT_FOLDER, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def render_template_form(template, current_data):
    """Render the Streamlit form components for a template."""
    updated_data = current_data.copy()
    
    for idx, section in enumerate(template.get('sections', [])):
        with st.expander(section['section_name'], expanded=True):
            
            # Special Handling for Comments/Notes sections
            # Make sure to handle all forms of "Comments", "Additional Findings", "Notes"
            s_name = section['section_name'].upper()
            if "COMMENT" in s_name or "ADDITIONAL FINDINGS" in s_name or "NOTES" in s_name:
                key = f"section_text_{section['section_id']}_{idx}"
                val = current_data.get(section['section_id'])
                new_val = st.text_area(
                    "Enter text here:",
                    value=str(val) if val else "",
                    key=key,
                    height=150
                )
                updated_data[section['section_id']] = new_val
                continue

            for f_idx, field in enumerate(section.get('fields', [])):
                field_id = field['field_id']
                label = field['label']
                required = field.get('required', False)
                f_type = field.get('type', 'free_text')
                
                # Label decoration
                display_label = f"{label} {'*' if required else ''}"
                
                # Get current value
                val = current_data.get(field_id)
                
                # Render based on type
                if f_type in ('single_select', 'multi_select'):
                    options = [opt['label'] for opt in field.get('options', [])]
                    
                    # Map stored value (snake_case) back to label if possible
                    # or just use it if it's already a label
                    
                    if f_type == 'single_select':
                        # Find index if val exists
                        idx = 0
                        if val:
                             # Try to match value to option label or value
                            for i, opt in enumerate(field.get('options', [])):
                                if val == opt['value'] or val == opt['label']:
                                    idx = i
                                    break
                        
                        selection = st.selectbox(
                            display_label, 
                            options, 
                            index=idx, 
                            key=f"field_{section['section_id']}_{field_id}_{idx}_{f_idx}"
                        )
                        # Store the snake_case value if possible
                        selected_opt = next((o for o in field['options'] if o['label'] == selection), None)
                        if selected_opt:
                            updated_data[field_id] = selected_opt['value']
                            
                    elif f_type == 'multi_select':
                        # Ensure val is list
                        if not isinstance(val, list):
                            val = [val] if val else []
                            
                        # Map stored values to labels for default
                        default_opts = []
                        for v in val:
                            match = next((o['label'] for o in field['options'] if o['value'] == v or o['label'] == v), None)
                            if match:
                                default_opts.append(match)
                                
                        selections = st.multiselect(
                            display_label,
                            options,
                            default=default_opts,
                            key=f"field_{section['section_id']}_{field_id}_{idx}_{f_idx}"
                        )
                        # Store values
                        stored_vals = []
                        for sel in selections:
                            match = next((o for o in field['options'] if o['label'] == sel), None)
                            if match:
                                stored_vals.append(match['value'])
                        updated_data[field_id] = stored_vals
                        
                else: # free_text, numeric, etc.
                    new_val = st.text_input(
                        display_label,
                        value=str(val) if val else "",
                        key=f"field_{section['section_id']}_{field_id}_{idx}_{f_idx}"
                    )
                    updated_data[field_id] = new_val
                    
    return updated_data
