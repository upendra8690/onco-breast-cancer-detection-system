# pages/15_Imaging_Guide.py
import streamlit as st
from auth.guard import check_login
from utils.language import get_text

check_login()

lang = st.session_state.get("app_language", "English")

st.title(f"📡 {get_text('imaging_guide', lang)}")
st.write("Understanding how breast ultrasound images are taken and used in AI diagnosis.")

# ---- What is Breast Ultrasound ----
st.subheader("🔬 What is Breast Ultrasound?")
st.markdown("""
Breast ultrasound (sonography) uses **high-frequency sound waves** to create images of the inside 
of the breast. It is safe, painless, and uses **no radiation**.

It is commonly used:
- To evaluate a lump found during a physical exam
- To distinguish between solid tumors and fluid-filled cysts
- As a supplement to mammography
- For women with dense breast tissue
""")

# ---- How Images Are Taken ----
st.subheader("📋 Step-by-Step: How the Image is Taken")

steps = [
    {
        "step": "Step 1: Patient Preparation",
        "detail": "The patient lies on their back with arm raised behind the head. No special preparation is needed. Clothing above the waist is removed.",
        "icon": "🛏️"
    },
    {
        "step": "Step 2: Gel Application",
        "detail": "A water-based gel is applied to the breast skin. This gel eliminates air pockets between the probe and skin, allowing better sound transmission.",
        "icon": "💧"
    },
    {
        "step": "Step 3: Transducer Placement",
        "detail": "A handheld device called a transducer (probe) is pressed against the breast. It emits high-frequency sound waves (7.5–15 MHz) into the tissue.",
        "icon": "📡"
    },
    {
        "step": "Step 4: Sound Wave Reflection",
        "detail": "Sound waves bounce back differently from fat, tissue, fluid, and tumors. These echoes are captured by the transducer.",
        "icon": "🔊"
    },
    {
        "step": "Step 5: Image Generation",
        "detail": "A computer converts the echoes into a real-time 2D grayscale image showing internal breast structures. Cysts appear dark, solid masses appear lighter.",
        "icon": "🖥️"
    },
    {
        "step": "Step 6: Image Analysis by AI",
        "detail": "In our system, the ultrasound image is fed to a trained CNN model which classifies the tissue as Benign, Malignant, or Normal with a confidence score.",
        "icon": "🤖"
    },
    {
        "step": "Step 7: GradCAM Heatmap",
        "detail": "Our GradCAM algorithm highlights the exact region of the image that the AI focused on to make its decision. This improves doctor trust and explainability.",
        "icon": "🔥"
    }
]

for item in steps:
    with st.expander(f"{item['icon']} {item['step']}"):
        st.write(item["detail"])

# ---- Image Characteristics ----
st.markdown("---")
st.subheader("🏷️ How to Read an Ultrasound Image")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("🟢 **Benign Cyst**")
    st.write("""
    - Appears as a dark (hypoechoic) oval/round structure
    - Has smooth, well-defined edges
    - Contains fluid → appears very dark
    - Posterior acoustic enhancement (brighter behind)
    """)

with col2:
    st.error("🔴 **Malignant Tumor**")
    st.write("""
    - Irregular shape with spiculated (spiky) margins
    - Heterogeneous internal texture
    - May have posterior shadowing
    - Taller than wide (vertical orientation)
    """)

with col3:
    st.info("🔵 **Normal Tissue**")
    st.write("""
    - Homogeneous layered appearance
    - Clearly defined fat and glandular layers
    - No discrete masses
    - Symmetric compared to other breast
    """)

# ---- BUSI Dataset Info ----
st.markdown("---")
st.subheader("📂 Dataset Used: BUSI (Breast Ultrasound Images)")

import pandas as pd
dataset_info = {
    "Property": ["Dataset Name", "Total Images", "Image Size", "Classes", "Source", "Year Published"],
    "Value": [
        "BUSI - Breast Ultrasound Images Dataset",
        "780 images",
        "224 × 224 pixels",
        "Benign (437), Malignant (210), Normal (133)",
        "Cairo University, Egypt",
        "2020"
    ]
}
st.table(pd.DataFrame(dataset_info))

st.info("""
**Reference:** Al-Dhabyani W, Gomaa M, Khaled H, Fahmy A. 
*Dataset of breast ultrasound images.* 
Data in Brief, 2020; 28:104863. 
DOI: 10.1016/j.dib.2019.104863
""")

# ---- CNN Model Architecture ----
st.markdown("---")
st.subheader("🧠 CNN Model Architecture")

arch_data = {
    "Layer": ["Conv2D (32 filters)", "MaxPooling2D", "Conv2D (64 filters)", "MaxPooling2D",
              "Conv2D (128 filters)", "MaxPooling2D", "Flatten", "Dense (128)", "Output Dense (3)"],
    "Details": [
        "3×3 kernel, ReLU activation, input 224×224×3",
        "2×2 pool size",
        "3×3 kernel, ReLU activation",
        "2×2 pool size",
        "3×3 kernel, ReLU activation",
        "2×2 pool size",
        "Flatten to 1D vector",
        "128 neurons, ReLU activation",
        "Softmax — Benign / Malignant / Normal"
    ]
}
st.table(pd.DataFrame(arch_data))

# ---- GradCAM Explanation ----
st.markdown("---")
st.subheader("🔥 What is GradCAM?")
st.markdown("""
**Gradient-weighted Class Activation Mapping (GradCAM)** is an AI explainability technique that:

1. Takes the **last convolutional layer** of the CNN model
2. Computes **gradients** of the predicted class score with respect to feature maps
3. Pools the gradients to get **weights** for each feature map
4. Produces a **heatmap** showing which regions influenced the prediction most

🔴 **Red/warm areas** = High importance for the prediction  
🔵 **Blue/cool areas** = Low importance for the prediction

This helps doctors **verify** the AI's reasoning and builds clinical trust.
""")