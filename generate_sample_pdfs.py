"""
Script to generate official-style reference PDFs for central and state government schemes.
These PDFs serve as the grounded knowledge base indexed by ChromaDB.
"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SCHEMES = [
    {
        "filename": "pm_kisan_guidelines.pdf",
        "title": "PRADHAN MANTRI KISAN SAMMAN NIDHI (PM-KISAN) - OPERATIONAL GUIDELINES",
        "ministry": "Ministry of Agriculture & Farmers Welfare, Government of India",
        "category": "Agriculture",
        "level": "Central",
        "url": "https://pmkisan.gov.in/Documents/PM-Kisan_Guidelines.pdf",
        "sections": [
            ("1. Overview & Objectives", 
             "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) is a Central Sector Scheme launched to supplement the financial needs of landholding farmers across India. Under the scheme, income support of Rs 6,000 per year is provided to eligible farmer families across the country in three equal four-monthly installments of Rs 2,000 each. The amount is transferred directly into the bank accounts of the beneficiaries through Direct Benefit Transfer (DBT)."),
            ("2. Eligibility Criteria",
             "A. Eligible Beneficiaries:\n"
             "- All landholder farmer families who own cultivable land in their names as per the official state land records (Record of Rights / RTC / Pahani / Khatauni).\n"
             "- Both small, marginal, and large farmers are eligible irrespective of land holding size (amended to cover all landholding farmers).\n"
             "- Domicile: Citizen and resident of India residing in any State or Union Territory.\n\n"
             "B. Exclusions / Non-Eligible Categories:\n"
             "- All Institutional Landholders.\n"
             "- Farmer families in which one or more of its members belong to: Former and present holders of constitutional posts, former and present Ministers/State Ministers, former/present Members of Lok Sabha/Rajya Sabha/State Legislative Assemblies.\n"
             "- Former and present Chairpersons of District Panchayats, Mayors of Municipal Corporations.\n"
             "- All serving or retired officers and employees of Central/State Government Ministries, Departments and field units (excluding Group D / Multi-Tasking Staff).\n"
             "- All superannuated/retired pensioners whose monthly pension is Rs 10,000 or more.\n"
             "- All persons who paid Income Tax in the last assessment year.\n"
             "- Professionals like Doctors, Engineers, Lawyers, Chartered Accountants, and Architects registered with professional bodies."),
            ("3. Required Documents Checklist",
             "1. Aadhaar Card (Mandatory: Aadhaar must be linked to active bank account and eKYC completed).\n"
             "2. Landholding Records (Khatauni / RTC / RoR / Pahani) proving clear ownership title.\n"
             "3. Savings Bank Account passbook with valid IFSC code.\n"
             "4. Active Mobile number linked to Aadhaar for OTP verification."),
            ("4. Step-by-Step Application Procedure",
             "Step 1: Visit the official PM-KISAN portal at https://pmkisan.gov.in.\n"
             "Step 2: Navigate to 'Farmers Corner' on the homepage and click on 'New Farmer Registration'.\n"
             "Step 3: Select Rural Farmer Registration or Urban Farmer Registration, enter Aadhaar number, State, and mobile number, and submit OTP.\n"
             "Step 4: Enter personal details, land survey number, dag/khasra number, and land area (in hectares/acres).\n"
             "Step 5: Upload scanned copy of land document (Pahani/RTC/Khatauni) and submit.\n"
             "Step 6: Alternatively, visit your nearest Common Service Centre (CSC) or Village Revenue Officer / Taluk Agriculture Officer for offline biometric enrollment.\n"
             "Step 7: Keep the registration reference number to track application and eKYC approval status.")
        ]
    },
    {
        "filename": "ayushman_bharat_pmjay.pdf",
        "title": "AYUSHMAN BHARAT - PRADHAN MANTRI JAN AROGYA YOJANA (AB PM-JAY)",
        "ministry": "National Health Authority, Ministry of Health and Family Welfare, Government of India",
        "category": "Healthcare",
        "level": "Central",
        "url": "https://pmjay.gov.in/guidelines",
        "sections": [
            ("1. Scheme Overview & Objective",
             "Ayushman Bharat PM-JAY is the world's largest government-funded health assurance scheme. It provides a health cover of Rs 5,00,000 per eligible family per year for secondary and tertiary care hospitalization. The scheme covers over 12 crore poor and vulnerable families (approximately 55 crore citizens) across India. Benefit is completely cashless and paperless across all public and empanelled private hospitals."),
            ("2. Eligibility Criteria",
             "A. Rural Beneficiary Identification (based on SECC 2011 deprivation criteria):\n"
             "- Families living in only one room with kuccha walls and kuccha roof (D1).\n"
             "- Families having no adult member between age 16 and 59 (D2).\n"
             "- Female-headed households with no adult male member between 16 and 59 (D3).\n"
             "- Families having disabled member and no able-bodied adult member (D4).\n"
             "- SC/ST households (D5).\n"
             "- Landless households deriving major part of their income from manual casual labour (D6).\n"
             "- Destitute / destitute beggars, manual scavengers, primitive tribal groups.\n"
             "- Annual household income generally below Rs 1,20,000 per annum.\n\n"
             "B. Urban Beneficiary Identification:\n"
             "- Ragpicker, beggar, domestic worker, street vendor, cobbler, hawker, construction worker, plumber, painter, security guard, transport worker, shop worker, waiter.\n\n"
             "C. Exclusions:\n"
             "- Families owning a motorized vehicle (car/tractor).\n"
             "- Families having any member as a regular government employee.\n"
             "- Families paying income tax or professional tax."),
            ("3. Required Documents Checklist",
             "1. Aadhaar Card or Voter ID card of the family head and members.\n"
             "2. Ration Card (BPL / Antyodaya Anna Yojana / State Food Security Card) or NFSA Card.\n"
             "3. PM-JAY Family ID letter or SECC acknowledgement slip.\n"
             "4. Active mobile number."),
            ("4. Step-by-Step Application & Golden Card Generation",
             "Step 1: Check eligibility online at https://beneficiary.nha.gov.in or https://mera.pmjay.gov.in by entering mobile number or Ration Card number.\n"
             "Step 2: If eligible, visit the nearest Empanelled Health Care Provider (EHCP) hospital and meet the 'Ayushman Mitra' desk, or visit a Common Service Centre (CSC).\n"
             "Step 3: Present your Aadhaar Card and Ration Card to the Ayushman Mitra for biometric Aadhaar e-KYC.\n"
             "Step 4: Once verified, the Ayushman Golden Card (PVC/Digital) is generated instantly.\n"
             "Step 5: Present the Ayushman Card at any empanelled hospital in India for cashless hospital admission, surgeries, medicines, and diagnostics up to Rs 5 Lakh.")
        ]
    },
    {
        "filename": "karnataka_raitha_vidya_nidhi.pdf",
        "title": "KARNATAKA RAITHA VIDYA NIDHI SCHEME - SCHOLARSHIP FOR FARMERS' CHILDREN",
        "ministry": "Department of Agriculture, Government of Karnataka",
        "category": "Education & Agriculture",
        "level": "State (Karnataka)",
        "url": "https://raitamitra.karnataka.gov.in/raithavidyanidhi",
        "sections": [
            ("1. Scheme Overview & Objective",
             "Raitha Vidya Nidhi is a flagship state welfare scheme launched by the Government of Karnataka to promote higher education among the children of farmers. Under this scheme, financial scholarship ranging between Rs 2,000 and Rs 11,000 per annum is directly disbursed via DBT to the bank accounts of farmer's children studying after 8th standard to complete their secondary, collegiate, diploma, and post-graduate studies."),
            ("2. Eligibility Criteria",
             "1. State Domicile: The student and their parents must be permanent residents and domiciles of Karnataka State.\n"
             "2. Farmer Parent: The applicant's father or mother must be a registered farmer owning agricultural land in Karnataka, with land ownership verified on Karnataka's FRUITS (Farmer Registration and Unified Beneficiary Information System) portal.\n"
             "3. Course of Study: The student must be actively enrolled in Class 8 to 10 (girl students), PUC / 11th-12th standard, ITI, Diploma, Undergraduate degree (BA, BSc, BCom, BE, MBBS, etc.), or Post-Graduate degree in a recognized institution.\n"
             "4. Scholar Allowance Slabs:\n"
             "   - High School (Classes 8-10, for girls): Rs 2,000 to Rs 3,000/year\n"
             "   - PUC / ITI / Diploma: Rs 2,500 to Rs 3,000/year\n"
             "   - Non-Technical Degree (BA, BCom, BSc): Rs 5,000/year (boys), Rs 5,500/year (girls)\n"
             "   - Professional Courses (BE, MBBS, Agriculture): Rs 10,000/year (boys), Rs 11,000/year (girls).\n\n"
             "Exclusions: Students whose parents do not own agricultural land registered on Karnataka FRUITS portal or students outside Karnataka state."),
            ("3. Required Documents Checklist",
             "1. Student Aadhaar Card.\n"
             "2. Parent's FRUITS ID (FID - 8 digit Farmer Identifier number from Karnataka Agriculture Dept).\n"
             "3. Land Record Certificate (Pahani / RTC copy) proving Karnataka agricultural landholding.\n"
             "4. School / College Admission Receipt or Bonafide Certificate with Student SATS/College Registration Number.\n"
             "5. Student's Aadhaar-seeded Bank Account Passbook (IFSC & Account number).\n"
             "6. Domicile / Residential Certificate of Karnataka."),
            ("4. Step-by-Step Application Procedure",
             "Step 1: Obtain parent's FRUITS ID from https://fruits.karnataka.gov.in or the local Raitha Samparka Kendra (RSK).\n"
             "Step 2: Visit the Karnataka State Scholarship Portal (SSP) at https://ssp.postmatric.karnataka.gov.in.\n"
             "Step 3: Create a student login using Aadhaar Number and authenticate via OTP.\n"
             "Step 4: Navigate to 'Raitha Vidya Nidhi Scholarship', enter Parent's FRUITS ID (FID) and College details.\n"
             "Step 5: The portal automatically matches land records from Bhoomi/FRUITS with student admission records from SATS.\n"
             "Step 6: Submit application online. The scholarship amount is credited directly via Aadhaar-enabled DBT into student's bank account.")
        ]
    },
    {
        "filename": "pm_awas_yojana_gramin.pdf",
        "title": "PRADHAN MANTRI AWAS YOJANA - GRAMIN (PMAY-G) OPERATIONAL GUIDELINES",
        "ministry": "Ministry of Rural Development, Government of India",
        "category": "Housing & Rural Development",
        "level": "Central",
        "url": "https://pmayg.nic.in/netiway/about-us.aspx",
        "sections": [
            ("1. Overview & Objectives",
             "Pradhan Mantri Awas Yojana - Gramin (PMAY-G) aims to provide a pucca house with basic amenities to all houseless households and those living in kutcha and dilapidated houses in rural areas of India. The minimum size of the house is 25 square metres including a hygienic cooking area."),
            ("2. Financial Assistance & Eligibility Criteria",
             "A. Assistance Amount:\n"
             "- Rs 1,20,000 per unit in plain areas.\n"
             "- Rs 1,30,000 per unit in hilly, difficult, and IAP districts.\n"
             "- Additional Rs 12,000 for toilet construction under Swachh Bharat Mission - Gramin (SBM-G).\n"
             "- 90 to 95 days of unskilled labour wages under MGNREGA (approx Rs 25,000 - Rs 28,000).\n\n"
             "B. Eligibility Criteria:\n"
             "- Beneficiaries selected from the Socio-Economic and Caste Census (SECC 2011) and Awaas+ list verified by Gram Sabha.\n"
             "- Houseless rural households or households living in zero, one, or two-room houses with kutcha wall and kutcha roof.\n"
             "- Priority given to SC, ST, freed bonded labourers, minorities, widows, disabled persons, and low-income rural households (annual income under Rs 1,00,000).\n\n"
             "C. Exclusions:\n"
             "- Households owning motorized two/three/four wheelers or agricultural equipment (mechanized 3-4 wheeler tractor).\n"
             "- Households having Kisan Credit Card with credit limit of Rs 50,000 or higher.\n"
             "- Household member earning more than Rs 15,000 per month or government employees.\n"
             "- Households owning 2.5 acres or more of irrigated land or 5 acres or more of un-irrigated land."),
            ("3. Required Documents Checklist",
             "1. Aadhaar Card of all adult family members.\n"
             "2. Active Bank Account details (Passbook with IFSC) linked to Aadhaar for DBT transfer.\n"
             "3. MGNREGA registered Job Card number.\n"
             "4. Land ownership documents or land allotment patta / consent certificate from Gram Panchayat.\n"
             "5. Swachh Bharat Mission (SBM) registration number."),
            ("4. Step-by-Step Application Procedure",
             "Step 1: Contact the local Gram Panchayat Secretary, Village Extension Officer (VEO), or Block Development Office (BDO).\n"
             "Step 2: Check if your name is listed on the Gram Sabha validated Awaas+ priority list.\n"
             "Step 3: Provide Aadhaar and MGNREGA Job Card details to the Panchayat official who uploads registration details on the AwaasSoft mobile app.\n"
             "Step 4: Geo-tagging inspection: Village officer visits existing kutcha dwelling and captures geo-tagged photographs.\n"
             "Step 5: Sanction order is issued by the Block Development Office.\n"
             "Step 6: Financial assistance is disbursed in 3-4 installments directly into bank account linked to stages of construction (foundation, lintel, roof completion).")
        ]
    },
    {
        "filename": "pm_svanidhi_guidelines.pdf",
        "title": "PM STREET VENDOR'S ATMANIRBHAR NIDHI (PM SVANIDHI) GUIDELINES",
        "ministry": "Ministry of Housing and Urban Affairs, Government of India",
        "category": "Livelihood & Micro-Credit",
        "level": "Central",
        "url": "https://pmsvanidhi.mohua.gov.in/",
        "sections": [
            ("1. Overview & Objectives",
             "PM SVANidhi is a central sector micro-credit scheme launched to provide affordable collateral-free working capital loans to urban street vendors and hawkers to resume their livelihoods. The scheme incentivizes digital transactions through monthly cashback and offers interest subsidy for timely repayments."),
            ("2. Loan Details & Eligibility Criteria",
             "A. Loan Facility:\n"
             "- 1st Tranche: Collateral-free working capital loan up to Rs 10,000 with tenure of 1 year.\n"
             "- 2nd Tranche: Up to Rs 20,000 upon timely or early repayment of 1st loan.\n"
             "- 3rd Tranche: Up to Rs 50,000 upon timely repayment of 2nd loan.\n"
             "- Interest Subsidy: 7% per annum interest subsidy credited directly to borrower's account quarterly.\n"
             "- Digital Cashback: Up to Rs 100/month (Rs 1,200/year) on eligible digital receipt/payment transactions.\n\n"
             "B. Eligibility Criteria:\n"
             "- Street vendors / hawkers vending in urban areas.\n"
             "- Vendors in possession of Certificate of Vending (CoV) or Identity Card issued by Urban Local Bodies (ULBs) / Municipalities.\n"
             "- Vendors identified in survey but not issued ID cards, or vendors left out of survey who possess Letter of Recommendation (LoR) from Town Vending Committee (TVC) or ULB.\n"
             "- No minimum education or landholding required. Annual income must not be in tax-paying bracket."),
            ("3. Required Documents Checklist",
             "1. Aadhaar Card (mandatory).\n"
             "2. Certificate of Vending (CoV) / Municipal Vendor ID Card / Letter of Recommendation (LoR).\n"
             "3. Bank Account Passbook (Aadhaar linked).\n"
             "4. Active mobile number linked to Aadhaar."),
            ("4. Step-by-Step Application Procedure",
             "Step 1: Check your vendor status at https://pmsvanidhi.mohua.gov.in using Aadhaar or CoV number.\n"
             "Step 2: If you do not have a CoV, approach the local Urban Local Body / Municipality or Town Vending Committee for a Letter of Recommendation (LoR).\n"
             "Step 3: Click 'Apply for Loan' on the PM SVANidhi portal or visit a Common Service Centre (CSC) or Banking Correspondent (BC).\n"
             "Step 4: Enter mobile number, Aadhaar OTP, and select your preferred lending institution (Public Bank, Private Bank, Regional Rural Bank, or Microfinance Institution).\n"
             "Step 5: Upload Vendor ID / LoR and submit the application.\n"
             "Step 6: Bank approves and disburses loan amount directly into bank account within 7 to 10 working days.")
        ]
    }
]

def build_pdf(scheme_info):
    filepath = DATA_DIR / scheme_info["filename"]
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0f4c81'),
        alignment=1, # Center
        spaceAfter=10
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4a5568'),
        alignment=1,
        spaceAfter=15
    )

    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1a365d'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#2d3748')
    )

    story = []
    # Title
    story.append(Paragraph(scheme_info["title"], title_style))
    story.append(Paragraph(f"{scheme_info['ministry']} | Level: {scheme_info['level']} | Category: {scheme_info['category']}<br/>Official Source: {scheme_info['url']}", meta_style))
    story.append(Spacer(1, 10))

    # Sections
    for sec_title, sec_content in scheme_info["sections"]:
        story.append(Paragraph(sec_title, section_header))
        # Format line breaks
        formatted_content = sec_content.replace("\n", "<br/>")
        story.append(Paragraph(formatted_content, body_style))
        story.append(Spacer(1, 8))

    doc.build(story)
    print(f"Generated: {filepath.name}")

def main():
    print("Generating official reference scheme PDF documents...")
    for s in SCHEMES:
        build_pdf(s)
    print("All reference PDF documents generated in data/ folder!")

if __name__ == "__main__":
    main()
