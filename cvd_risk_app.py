import streamlit as st
import os
import math
import pandas as pd
import matplotlib.pyplot as plt

# ----- Page Configuration & Branding -----
st.set_page_config(layout="wide", page_title="SMART CVD Risk Reduction")

# Layout columns for logo alignment
col1, col2, col3 = st.columns([1, 6, 1])
with col3:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=1000)
    else:
        st.warning("⚠️ Logo not found — please upload 'logo.png' into the app directory.")

# ----- Sidebar: Risk Profile -----
st.sidebar.markdown("### 🔹 Risk Profile")
age = st.sidebar.slider("Age (years)", 30, 90, 60)
sex = st.sidebar.radio("Sex", ["Male", "Female"])
weight = st.sidebar.number_input("Weight (kg)", 40.0, 200.0, 75.0)
height = st.sidebar.number_input("Height (cm)", 140.0, 210.0, 170.0)
bmi = weight / ((height / 100) ** 2)
st.sidebar.markdown(f"**BMI:** {bmi:.1f} kg/m²")
smoker = st.sidebar.checkbox("Current smoker", help="Tobacco use increases CVD risk (JAMA 2019)")
diabetes = st.sidebar.checkbox("Diabetes", help="Diabetes doubles CVD risk (UKPDS 1998)")
egfr = st.sidebar.slider("eGFR (mL/min/1.73m²)", 15, 120, 90, help="Renal function; CKD increases risk")
st.sidebar.markdown("**Vascular Disease (tick all that apply)**")
vasc1 = st.sidebar.checkbox("Coronary artery disease", help="History of MI or revascularization")
vasc2 = st.sidebar.checkbox("Cerebrovascular disease", help="Stroke/TIA history")
vasc3 = st.sidebar.checkbox("Peripheral artery disease", help="Claudication or revascularization")
vasc_count = sum([vasc1, vasc2, vasc3])

# ----- Main Page: Step 1 -----
st.title("SMART CVD Risk Reduction Calculator")
st.markdown("### Step 1: Lab Results")
total_chol = st.number_input("Total Cholesterol (mmol/L)", 2.0, 10.0, 5.2, 0.1, help="Calculated or fasting")
hdl = st.number_input("HDL‑C (mmol/L)", 0.5, 3.0, 1.3, 0.1, help="High‑density lipoprotein")
baseline_ldl = st.number_input("Baseline LDL‑C (mmol/L)", 0.5, 6.0, 3.0, 0.1, help="Calculated via Friedewald or direct")
crp = st.number_input("hs‑CRP (mg/L) — Baseline (not during acute MI)", 0.1, 20.0, 2.5, 0.1, help="JUPITER: NEJM 2008")
hba1c = st.number_input("Latest HbA₁c (%)", 4.5, 15.0, 7.0, 0.1, help="UKPDS: Lancet 1998")
tg = st.number_input("Fasting Triglycerides (mmol/L)", 0.5, 5.0, 1.5, 0.1, help="REDUCE‑IT: NEJM 2019")

st.markdown("---")

# ----- Main Page: Step 2 -----
st.markdown("### Step 2: Therapies")

st.subheader("Pre‑admission Lipid‑lowering Therapy")
statin = st.selectbox("Statin", ["None", "Atorvastatin 80 mg", "Rosuvastatin 20 mg"],
                      help="CTT meta‑analysis: Lancet 2010")
ez = st.checkbox("Ezetimibe 10 mg", help="IMPROVE‑IT: NEJM 2015")
bemp = st.checkbox("Bempedoic acid", help="CLEAR Outcomes: Lancet 2023")

# Anticipated LDL after current
adj_ldl = baseline_ldl
if statin != "None":
    adj_ldl *= (1 - {"Atorvastatin 80 mg":0.50, "Rosuvastatin 20 mg":0.55}[statin])
if ez:
    adj_ldl *= 0.80
adj_ldl = max(adj_ldl, 1.0)
st.write(f"**Anticipated LDL‑C:** {adj_ldl:.2f} mmol/L")

st.subheader("Add‑on Lipid‑lowering Therapy")
if adj_ldl > 1.8:
    pcsk9 = st.checkbox("PCSK9 inhibitor", help="FOURIER: NEJM 2017")
    incl = st.checkbox("Inclisiran (siRNA)", help="ORION‑10: NEJM 2020")
else:
    st.info("PCSK9i/Inclisiran only if LDL‑C >1.8 mmol/L")

st.markdown("**Lifestyle Changes**")
smoke_iv = st.checkbox("Smoking cessation", disabled=not smoker, help="FHMI: Lancet 2020")
semaglutide = st.checkbox("GLP‑1 RA (Semaglutide)", disabled=(bmi < 30), help="STEP: NEJM 2021")
med_iv = st.checkbox("Mediterranean diet", help="PREDIMED: NEJM 2013")
act_iv = st.checkbox("Physical activity", help="WHO guidelines")
alc_iv = st.checkbox("Alcohol moderation (>14 units/wk)", help="UK guidelines")
str_iv = st.checkbox("Stress reduction", help="Mindfulness trial")

st.markdown("**Other Therapies**")
asa_iv = st.checkbox("Antiplatelet (ASA or Clopidogrel)", help="CAPRIE: Lancet 1996")
bp_iv = st.checkbox("BP control (target <130 mmHg)", help="SPRINT: NEJM 2015")
sglt2iv = st.checkbox("SGLT2 inhibitor (e.g. Empagliflozin)", help="EMPA‑REG: NEJM 2015")
if tg > 1.7:
    ico_iv = st.checkbox("Icosapent ethyl", help="REDUCE‑IT: NEJM 2019")
else:
    st.info("Icosapent ethyl only if TG >1.7 mmol/L")

st.markdown("---")

# ----- Main Page: Step 3 -----
st.markdown("### Step 3: Results & Summary")
# Implement SMART/MACE risk calculation here...
st.write("Results placeholder – insert ARR, RRR, charts here.")

st.markdown("---")
st.markdown("Created by Samuel Panday — 21/04/2025")
st.markdown("Created by PRIME team (Prevention Recurrent Ischaemic Myocardial Events)")
st.markdown("King's College Hospital, London")
st.markdown("This tool is provided for informational purposes and designed to support discussions with your healthcare provider—it’s not a substitute for professional medical advice.")
