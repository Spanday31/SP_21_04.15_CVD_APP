import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import date

# Configure page
st.set_page_config(page_title="SMART-2 CVD Risk Calculator", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .risk-high { background-color: #ffcccc; padding: 10px; border-radius: 5px; }
    .risk-medium { background-color: #fff3cd; padding: 10px; border-radius: 5px; }
    .risk-low { background-color: #d4edda; padding: 10px; border-radius: 5px; }
    .header-box { border-bottom: 2px solid #0056b3; margin-top: 20px; }
    .stMetric { border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

# Evidence database with tooltips
EVIDENCE = {
    "smoking": {
        "study": "Hackshaw et al. BMJ 2018",
        "link": "https://www.bmj.com/content/360/bmj.j5855",
        "effect": "2-4x higher risk of recurrent events"
    },
    "ldl": {
        "study": "CTT Collaboration, Lancet 2010",
        "link": "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(10)61350-5/",
        "effect": "22% RR reduction per 1 mmol/L LDL reduction"
    },
    "statin_high": {
        "study": "TNT Trial, NEJM 2005",
        "link": "https://www.nejm.org/doi/full/10.1056/nejmoa050461",
        "effect": "22% RR reduction vs moderate-intensity"
    },
    "sbp": {
        "study": "SPRINT Trial, NEJM 2015",
        "link": "https://www.nejm.org/doi/full/10.1056/NEJMoa1511939",
        "effect": "25% RR reduction with intensive control"
    }
}

def create_evidence_tooltip(key):
    """Generate hover tooltip with study evidence"""
    study = EVIDENCE.get(key, {})
    if study:
        return f"**Effect:** {study['effect']} | **Source:** {study['study']}"
    return ""

# SMART-2 Risk Calculation
def calculate_smart2_risk(age, sex, diabetes, smoker, egfr, vasc_count, ldl, sbp):
    """Calculate 10-year recurrent CVD risk using SMART-2 model"""
    coefficients = {
        'intercept': -8.1937,
        'age': 0.0635,
        'female': -0.3372,
        'diabetes': 0.5034,
        'smoker': 0.7862,
        'egfr<30': 0.9235 if egfr < 30 else 0,
        'egfr30-60': 0.5539 if 30 <= egfr < 60 else 0,
        'polyvascular': 0.5434 if vasc_count >= 2 else 0,
        'ldl': 0.2436 * (ldl - 2.5),
        'sbp': 0.0083 * (sbp - 120)
    }
    
    lp = (coefficients['intercept'] + 
          coefficients['age'] * (age - 60) + 
          coefficients['female'] * (1 if sex == "Female" else 0) +
          coefficients['diabetes'] * diabetes +
          coefficients['smoker'] * smoker +
          coefficients['egfr<30'] +
          coefficients['egfr30-60'] +
          coefficients['polyvascular'] +
          coefficients['ldl'] +
          coefficients['sbp'])
    
    risk_percent = 100 * (1 - np.exp(-np.exp(lp) * 10))
    return round(risk_percent, 1)

# App Header
st.title("SMART-2 Recurrent CVD Risk Calculator")
st.markdown("""
*Calculates 10-year risk of recurrent cardiovascular events in patients with established CVD*  
*Based on: Dorresteijn JAN et al. Eur Heart J 2019;40(37):3133-3140*  
[View SMART-2 Study](https://academic.oup.com/eurheartj/article/40/37/3133/5376566)
""")

# 1. PATIENT DEMOGRAPHICS ----------------------------------
st.markdown('<div class="header-box"><h2>1. Patient Characteristics</h2></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("Age (years)", min_value=30, max_value=90, value=65, step=1)
    sex = st.radio("Sex", ["Male", "Female"])
    
with col2:
    diabetes = st.checkbox("Diabetes mellitus")
    smoker = st.checkbox("Current smoker", help=create_evidence_tooltip("smoking"))
    
with col3:
    weight = st.number_input("Weight (kg)", min_value=40.0, max_value=200.0, value=75.0, step=0.1)
    height = st.number_input("Height (cm)", min_value=140.0, max_value=210.0, value=170.0, step=0.1)
    bmi = round(weight / ((height/100)**2, 1)
    st.markdown(f"**BMI:** {bmi} kg/m²")

# 2. CLINICAL MARKERS --------------------------------------
st.markdown('<div class="header-box"><h2>2. Clinical Markers</h2></div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Laboratory Values", "Vascular History"])
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        ldl = st.number_input("LDL-C (mmol/L)", min_value=0.5, max_value=6.0, value=3.0, step=0.1,
                             help=create_evidence_tooltip("ldl"))
        hdl = st.number_input("HDL-C (mmol/L)", min_value=0.5, max_value=3.0, value=1.3, step=0.1)
    with col2:
        sbp = st.number_input("Systolic BP (mmHg)", min_value=80, max_value=220, value=140, step=1,
                             help=create_evidence_tooltip("sbp"))
        egfr = st.slider("eGFR (mL/min/1.73m²)", min_value=15, max_value=120, value=60)

with tab2:
    vasc_cor = st.checkbox("Coronary artery disease")
    vasc_cer = st.checkbox("Cerebrovascular disease")
    vasc_per = st.checkbox("Peripheral artery disease")
    vasc_count = sum([vasc_cor, vasc_cer, vasc_per])

# 3. TREATMENT OPTIONS -------------------------------------
st.markdown('<div class="header-box"><h2>3. Treatment Options</h2></div>', unsafe_allow_html=True)

with st.expander("Lipid-Lowering Therapy", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        statin = st.radio("Statin intensity", ["None", "Moderate", "High"],
                         help=create_evidence_tooltip("statin_high"))
    with col2:
        ezetimibe = st.checkbox("Ezetimibe 10mg daily")
        pcsk9i = st.checkbox("PCSK9 inhibitor", disabled=ldl < 1.8)

with st.expander("Blood Pressure Management"):
    sbp_target = st.slider("Target SBP (mmHg)", 80, 220, 130, help="SPRINT trial target")
    st.checkbox("ACE inhibitor/ARB")
    st.checkbox("Calcium channel blocker")

with st.expander("Lifestyle Interventions"):
    st.checkbox("Mediterranean diet")
    st.checkbox("Regular exercise (150 min/week)")
    if smoker:
        st.checkbox("Smoking cessation program")

# 4. RISK CALCULATION & RESULTS ----------------------------
st.markdown('<div class="header-box"><h2>4. Risk Assessment</h2></div>', unsafe_allow_html=True)

# Calculate risks
baseline_risk = calculate_smart2_risk(age, sex, diabetes, smoker, egfr, vasc_count, ldl, sbp)

# Apply treatment effects (simplified model)
rr_reduction = 0
if statin == "Moderate":
    rr_reduction += 25
elif statin == "High":
    rr_reduction += 35
if ezetimibe:
    rr_reduction += 6
if pcsk9i:
    rr_reduction += 15
if sbp_target < 130:
    rr_reduction += 15

projected_risk = baseline_risk * (1 - rr_reduction/100)

# Display metrics
col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="Baseline 10-Year Risk",
        value=f"{baseline_risk}%",
        help="Untreated risk of recurrent CVD event"
    )
    
with col2:
    st.metric(
        label="Projected Risk with Treatments",
        value=f"{projected_risk:.1f}%",
        delta=f"-{baseline_risk - projected_risk:.1f}%",
        delta_color="inverse",
        help=f"Estimated {rr_reduction}% relative risk reduction"
    )

# Risk trend visualization
risk_data = pd.DataFrame({
    "Scenario": ["Baseline", "With Interventions"],
    "Risk (%)": [baseline_risk, projected_risk],
    "Color": ["#ff5a5f", "#25a55f"]
})

fig = px.bar(risk_data, x="Scenario", y="Risk (%)", color="Color", 
             color_discrete_map={"#ff5a5f": "#ff5a5f", "#25a55f": "#25a55f"},
             text="Risk (%)", height=300)
fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="10-Year Risk (%)")
st.plotly_chart(fig, use_container_width=True)

# Clinical recommendations
st.markdown("### Clinical Recommendations")
if projected_risk > 30:
    st.markdown('<div class="risk-high">'
               '<h4>🔴 Very High Risk</h4>'
               '<ul>'
               '<li>Intensive lipid lowering (target LDL <1.4 mmol/L)</li>'
               '<li>Consider PCSK9 inhibitor if LDL remains elevated</li>'
               '<li>Multidisciplinary risk factor management</li>'
               '</ul></div>', unsafe_allow_html=True)
elif projected_risk > 20:
    st.markdown('<div class="risk-medium">'
               '<h4>🟠 High Risk</h4>'
               '<ul>'
               '<li>Optimize statin therapy (high-intensity preferred)</li>'
               '<li>Target SBP <130 mmHg if tolerated</li>'
               '<li>Address all modifiable risk factors</li>'
               '</ul></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="risk-low">'
               '<h4>🟢 Moderate Risk</h4>'
               '<ul>'
               '<li>Maintain adherence to current therapies</li>'
               '<li>Focus on lifestyle interventions</li>'
               '<li>Annual risk reassessment</li>'
               '</ul></div>', unsafe_allow_html=True)

# References
st.markdown("---")
with st.expander("Evidence References"):
    for key, study in EVIDENCE.items():
        st.markdown(f"🔹 **{study['study']}**: {study['effect']} | [Read study]({study['link']})")

# Footer
st.markdown("---")
st.markdown("""
*Developed for clinical use • Based on SMART-2 risk model • Not a substitute for clinical judgment*  
*Version 1.0 • {date.today().strftime('%Y-%m-%d')}*
""")
