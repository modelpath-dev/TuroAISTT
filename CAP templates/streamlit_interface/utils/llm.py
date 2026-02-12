import os
import json
from extractor import ReportRefiner

# Initialize our refiner (OpenAI based)
refiner = ReportRefiner()

def process_text_with_llm(text, template):
    """
    Interface for app.py to process text chunks.
    """
    try:
        report = refiner.refine_and_extract(text, template)
        return (
            report.extracted_data,
            report.missing_fields,
            report.clarification_questions
        )
    except Exception:
        return {}, [], []

def generate_report(template, data):
    """Generate a readable text report from the data."""
    lines = []
    lines.append(f"CAP PROTOCOL: {template.get('organ')}")
    lines.append("-" * 40)
    
    for section in template.get('sections', []):
        s_name = section['section_name'].upper()
        if "COMMENT" in s_name or "ADDITIONAL FINDINGS" in s_name or "NOTES" in s_name:
            val = data.get(section['section_id'])
            if val:
                lines.append(f"\n[{section['section_name']}]")
                lines.append(str(val))
            continue

        section_lines = []
        for field in section.get('fields', []):
            val = data.get(field['field_id'])
            if val:
                # Format value
                if isinstance(val, list):
                    val_str = ", ".join(str(v) for v in val)
                else:
                    # Find option label if it's a select type
                    opt_label = val
                    if field.get('type') in ('single_select', 'multi_select'):
                        for opt in field.get('options', []):
                            if opt['value'] == val:
                                opt_label = opt['label']
                                break
                    val_str = str(opt_label)
                section_lines.append(f"{field['label']}: {val_str}")
                
        if section_lines:
            lines.append(f"\n[{section['section_name']}]")
            lines.extend(section_lines)
            
    return "\n".join(lines)
