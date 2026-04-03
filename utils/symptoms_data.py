# utils/symptoms_data.py

SYMPTOMS_DATA = {
    "English": {
        "title": "Breast Cancer Symptoms Checker",
        "description": "This tool helps you understand common breast cancer symptoms. This is NOT a diagnosis — always consult a doctor.",
        "symptoms": [
            {
                "name": "Lump in the breast or underarm",
                "description": "A painless lump or thickening in the breast or armpit area that doesn't go away.",
                "severity": "High",
                "action": "See a doctor immediately"
            },
            {
                "name": "Change in breast size or shape",
                "description": "Unexplained swelling or shrinkage of the breast, especially on one side.",
                "severity": "High",
                "action": "See a doctor immediately"
            },
            {
                "name": "Nipple discharge",
                "description": "Clear, bloody, or colored fluid leaking from the nipple without squeezing.",
                "severity": "High",
                "action": "See a doctor immediately"
            },
            {
                "name": "Nipple changes",
                "description": "Nipple turning inward (inversion), redness, scaling, or thickening.",
                "severity": "Medium",
                "action": "Schedule a doctor visit within 1 week"
            },
            {
                "name": "Skin changes on breast",
                "description": "Redness, dimpling, puckering, or orange-peel texture on breast skin.",
                "severity": "High",
                "action": "See a doctor immediately"
            },
            {
                "name": "Breast pain",
                "description": "Persistent pain in the breast or nipple area not related to menstrual cycle.",
                "severity": "Medium",
                "action": "Monitor for 2 weeks; see doctor if persists"
            },
            {
                "name": "Swollen lymph nodes",
                "description": "Swelling in the lymph nodes under the arm or near the collarbone.",
                "severity": "High",
                "action": "See a doctor immediately"
            },
            {
                "name": "Skin irritation or dimpling",
                "description": "Skin that looks irritated, scaly, or has dimpling like an orange peel.",
                "severity": "Medium",
                "action": "Schedule a doctor visit within 1 week"
            }
        ],
        "risk_note": "Having these symptoms does not mean you have cancer. Many conditions cause these symptoms. Early detection saves lives.",
        "emergency_note": "⚠️ If you find a new lump, please consult a doctor within 24-48 hours."
    }
}


EARLY_DETECTION_INFO = {
    "English": [
        {
            "title": "Monthly Self-Examination",
            "description": "Perform a breast self-exam once a month, ideally 3-5 days after your menstrual period ends. Look for any new lumps, changes in shape, or skin changes.",
            "icon": "🔍"
        },
        {
            "title": "Annual Clinical Exam",
            "description": "Women aged 20-39 should have a clinical breast exam every 3 years. Women 40+ should have it annually.",
            "icon": "👩‍⚕️"
        },
        {
            "title": "Mammography Screening",
            "description": "Women aged 40 and above should have an annual mammogram. Women with family history may need to start earlier.",
            "icon": "🏥"
        },
        {
            "title": "Ultrasound Imaging",
            "description": "Breast ultrasound uses sound waves to create images. It is used alongside mammography and is safe (no radiation).",
            "icon": "📡"
        }
    ]
}