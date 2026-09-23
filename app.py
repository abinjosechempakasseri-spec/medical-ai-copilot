import hashlib
import gradio as gr

# 1. SHA-256 Patient ID Masking Function
def mask_patient_id(name, address):
    combined_info = f"{name.strip().lower()}_{address.strip().lower()}"
    patient_hash = hashlib.sha256(combined_info.encode()).hexdigest()[:6].upper()
    return f"PAT-{patient_hash}"

# 2. Main Logic: PII Masking, Clinical Draft Generation & Dosage Logic
def generate_ai_copilot(p_name, p_address, symptoms, lab_results, present_condition):
    masked_id = mask_patient_id(p_name, p_address)
    
    # Clinical Logic & ICD-10 Mapping based on symptoms
    symp_lower = symptoms.lower()
    if "fever" in symp_lower or "cough" in symp_lower:
        icd_code = "J06.9 (Acute upper respiratory infection, unspecified)"
        medication_suggestion = "Paracetamol 500mg (1-0-1 after food) + Steam Inhalation"
        confidence = "92%"
    elif "chest pain" in symp_lower or "breath" in symp_lower:
        icd_code = "R07.9 (Chest pain, unspecified)"
        medication_suggestion = "Immediate ECG & Emergency Evaluation Required"
        confidence = "88%"
    elif "stomach" in symp_lower or "vomiting" in symp_lower:
        icd_code = "K52.9 (Noninfective gastroenteritis and colitis, unspecified)"
        medication_suggestion = "ORS Hydration + Dicyclomine 10mg (if pain persists)"
        confidence = "90%"
    else:
        icd_code = "R69 (Illness, unspecified)"
        medication_suggestion = "Symptomatic relief & Clinical Observation"
        confidence = "75%"
        
    ai_draft = f"""==================================================
           AI CLINICAL SUMMARY (DRAFT)
==================================================
PATIENT IDENTIFIER : {masked_id} [PII MASKED VIA SHA-256]
PRIMARY SYMPTOMS   : {symptoms}
LAB RESULTS        : {lab_results}
PRESENT CONDITION  : {present_condition}

--------------------------------------------------
CLINICAL DECISION SUPPORT
--------------------------------------------------
RECOMMENDED ICD-10 : {icd_code}
CONFIDENCE SCORE   : {confidence}

PROPOSED PRESCRIPTION & GUIDANCE:
- Suggested Rx: {medication_suggestion}

--------------------------------------------------
⚠️ STATUS: PENDING DOCTOR REVIEW & APPROVAL
=================================================="""
    
    return ai_draft

# 3. Human-in-the-Loop Doctor Action
def doctor_action(ai_draft_text, doc_remarks, status_action):
    if not ai_draft_text or "PATIENT IDENTIFIER" not in ai_draft_text:
        return "⚠️ Please generate an AI Clinical Summary first!"
        
    status_str = "APPROVED & AUTHORIZED" if status_action == "approve" else "REJECTED / NEEDS REVISION"
    
    final_record = f"""{ai_draft_text}

==================================================
           DOCTOR VERIFICATION & AUTHORITY
==================================================
STATUS         : {status_str}
DOCTOR REMARKS : {doc_remarks if doc_remarks else 'None'}
VERIFIED BY    : Duty Medical Officer, M.D.
TIMESTAMP      : Verified via Human-in-the-Loop Workflow
=================================================="""
    
    return final_record

# 4. Gradio Interface Layout
with gr.Blocks(title="Doctor-Controlled Medical AI Co-Pilot") as app:
    
    # Personal Branding Header
    gr.Markdown("""
    # Doctor-Controlled Medical AI Co-Pilot
    *Privacy-First Clinical Decision Support Architecture*
    
    ---
    <div style="display: flex; align-items: center; gap: 15px; background-color: #f0f2f5; padding: 15px; border-radius: 10px;">
        <img src="https://i.postimg.cc/G2VS5MKX/Gemini-Generated-Image-geq1qhgeq1qhgeq1.png" style="border-radius: 50%; width: 85px; height: 85px; object-fit: cover; border: 2px solid #007bff;">
        <div>
            <h2 style="margin: 0; color: #1a1a1a;">Abin Jose</h2>
            <p style="margin: 3px 0; font-weight: bold; color: #555;">AI & Software Architect</p>
            <p style="margin: 0; font-size: 14px;">
                📧 <a href="mailto:abinjosechempakasseri@gmail.com" target="_blank">abinjosechempakasseri@gmail.com</a> | 
                📸 Instagram: <a href="https://instagram.com/abin_x_jose" target="_blank">@abin_x_jose</a>
            </p>
        </div>
    </div>
    ---
    """)

    # Main UI Layout
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Step 1: Patient Data Input")
            p_name = gr.Textbox(label="Patient Name (PII)", value="Abin")
            p_addr = gr.Textbox(label="Patient Address (PII)", value="Kochi, Kerala")
            p_symp = gr.Textbox(label="Symptoms", value="High fever, dry cough")
            p_lab = gr.Textbox(label="Lab Test Results", value="WBC: 11,500/mcL, SpO2: 98%")
            p_cond = gr.Textbox(label="Present Condition", value="Moderate fever for 3 days")
            btn_generate = gr.Button("Generate AI Analysis", variant="primary")
            
        with gr.Column():
            gr.Markdown("### Step 2: AI Clinical Draft & Doctor Approval")
            ai_output = gr.Textbox(label="AI Clinical Summary (Draft)", lines=14)
            doc_notes = gr.Textbox(label="Doctor Remarks / Rx Customization", placeholder="Enter notes or custom instructions here...")
            
            with gr.Row():
                btn_approve = gr.Button("Approve Prescription", variant="primary")
                btn_reject = gr.Button("Reject / Request Modification", variant="stop")
                
            final_output = gr.Textbox(label="Final Authorized Medical Record", lines=18)

    # Click Handlers
    btn_generate.click(fn=generate_ai_copilot, inputs=[p_name, p_addr, p_symp, p_lab, p_cond], outputs=ai_output)
    btn_approve.click(fn=lambda summary, notes: doctor_action(summary, notes, "approve"), inputs=[ai_output, doc_notes], outputs=final_output)
    btn_reject.click(fn=lambda summary, notes: doctor_action(summary, notes, "reject"), inputs=[ai_output, doc_notes], outputs=final_output)

# Launch App
app.launch(server_name="0.0.0.0", server_port=7860)
