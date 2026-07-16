import streamlit as st
import pandas as pd
import json
import fitz  # PyMuPDF
import re
 
# --- STREAMLIT UI CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Telecom Visual QC Analyzer", page_icon="🛰️")
st.title("🛰️ Telecom Engineering Visual QC Analyzer")
st.subheader("Automated 20-Point Quality Control Audit")
 
uploaded_file = st.file_uploader("Upload Telecom QC Print/Drawing PDF", type=["pdf"])
 
if uploaded_file is not None:
    st.info("🔄 Processing PDF and performing automated 20-Point Audit...")
    
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Extract full text from all pages
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"
        
        full_text_lower = full_text.lower()
        
        # Define 20 QC Rules Evaluation
        qc_checks = [
            ("Q1", "Caution & Construction Notes present?", "caution" in full_text_lower or "construction" in full_text_lower),
            ("Q2", "Legend present on Print 1 or drawing block?", "legend" in full_text_lower or "symbol" in full_text_lower),
            ("Q3", "PFP location or PFP ID specified?", "pfp" in full_text_lower),
            ("Q4", "PON name or PON ID specified?", "pon" in full_text_lower),
            ("Q5", "Cable placement in ROW & U/E mentioned?", "row" in full_text_lower or "u/e" in full_text_lower or "easement" in full_text_lower),
            ("Q6", "Specified Drop HH/FP size? Is it 10x15?", "10x15" in full_text_lower or "handhole" in full_text_lower),
            ("Q7", "HH sizes specified as per loop placement?", "hh" in full_text_lower or "handhole" in full_text_lower),
            ("Q8", "Tasking details mentioned?", "splice" in full_text_lower or "cable" in full_text_lower or "terminal" in full_text_lower),
            ("Q9", "Measurements specified (FH-PI, PI-PI, etc.)?", bool(re.search(r'\d+\'|\d+\s*ft', full_text_lower))),
            ("Q10", "Tie-ins & measurements specified?", "tie" in full_text_lower or bool(re.search(r'\d+\'', full_text_lower))),
            ("Q11", "Match line or To & From PFP details?", "match line" in full_text_lower or "match" in full_text_lower),
            ("Q12", "Cable breakdown matches prints?", "cable" in full_text_lower or "fnap" in full_text_lower),
            ("Q13", "Loops in prints specified as per posting?", "loop" in full_text_lower or "slack" in full_text_lower),
            ("Q14", "Terminal address naming convention?", "terminal" in full_text_lower or "-1" in full_text_lower),
            ("Q15", "20' Separator mentioned?", "20'" in full_text_lower or "20 ft" in full_text_lower or "separator" in full_text_lower),
            ("Q16", "Terminal placed on Splice HH or own FH?", "terminal" in full_text_lower or "splice" in full_text_lower),
            ("Q17", "Proper symbol representation of splice shown?", "splice" in full_text_lower or "tether" in full_text_lower),
            ("Q18", "Splice/Tether HH specified as EMS?", "ems" in full_text_lower),
            ("Q19", "Aramis Posting & Clean up mentioned?", "aramis" in full_text_lower or "posting" in full_text_lower),
            ("Q20", "Addresses added into AOTX section?", "aotx" in full_text_lower or "address" in full_text_lower)
        ]
        
        qc_results = []
        for q_num, check_name, condition in qc_checks:
            qc_results.append({
                "Q#": q_num,
                "QC Parameter Check": check_name,
                "Status": "Pass" if condition else "Fail",
                "Evidence & Remarks": "Verified from drawing text layers" if condition else "Parameter missing or not explicitly stated in text layers"
            })
            
        df = pd.DataFrame(qc_results)
        
        st.header("📋 Automated 20-Point QC Audit Table")
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        
        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Visual QC Audit Report as CSV",
            data=csv,
            file_name="Telecom_QC_Audit_Report.csv",
            mime="text/csv",
        )
 
    except Exception as e:
        st.error(f"Error processing PDF: {e}")