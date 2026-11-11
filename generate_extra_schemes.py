"""
Script to generate 10 additional official-style reference PDFs for government schemes.
Expands the knowledge base to 15 scheme documents with over 100 chunks.
Explicitly labeled as supplementary reference documents compiled from official portals.
"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

EXTRA_SCHEMES = [
    {
        "filename": "pm_fasal_bima_yojana.pdf",
        "title": "PRADHAN MANTRI FASAL BIMA YOJANA (PMFBY) - OPERATIONAL GUIDELINES",
        "ministry": "Ministry of Agriculture & Farmers Welfare, Government of India",
        "category": "Agriculture & Insurance",
        "level": "Central",
        "url": "https://pmfby.gov.in",
        "sections": [
            ("1. Overview & Objectives",
             "Pradhan Mantri Fasal Bima Yojana (PMFBY) provides comprehensive crop insurance cover against non-preventable natural risks from pre-sowing to post-harvest stages. It aims to stabilize farmers' income, encourage adoption of modern agricultural practices, and ensure flow of credit to the agriculture sector."),
            ("2. Premium Rates & Subsidy",
             "- Kharif Food & Oilseed Crops: Maximum 2.0% of Sum Insured paid by farmer.\n"
             "- Rabi Food & Oilseed Crops: Maximum 1.5% of Sum Insured paid by farmer.\n"
             "- Commercial & Horticultural Crops: Maximum 5.0% of Sum Insured paid by farmer.\n"
             "- Balance premium is shared 50:50 between Central and State Government (90:10 for North Eastern States)."),
            ("3. Eligibility Criteria",
             "- All farmers including sharecroppers and tenant farmers growing notified crops in notified areas.\n"
             "- Mandatory for loanee farmers availing Seasonal Agricultural Operations (SAO) loans from financial institutions (made voluntary post-2020 revision).\n"
             "- Non-loanee farmers may opt-in voluntarily with land ownership/tenancy documentation.\n"
             "- No minimum or maximum landholding ceiling; no income ceiling."),
            ("4. Required Documents Checklist",
             "1. Aadhaar Card of the farmer.\n"
             "2. Land ownership record (RTC / RoR / Land Possession Certificate / Registered Tenancy Agreement).\n"
             "3. Sowing Certificate / declaration issued by Patwari / Village Agriculture Worker.\n"
             "4. Active Bank Account Passbook with IFSC (Aadhaar linked)."),
            ("5. Application & Claim Procedure",
             "Step 1: Apply online through the National Crop Insurance Portal at https://pmfby.gov.in or through banks / CSCs.\n"
             "Step 2: Enter Aadhaar, bank details, crop details, and survey/khasra number.\n"
             "Step 3: Pay farmer share of premium within cutoff date (usually July 31 for Kharif, Dec 31 for Rabi).\n"
             "Step 4: In case of localized calamities (hailstorm, landslide, inundation), report loss within 72 hours via Crop Insurance App or toll-free number 1800-180-1551.\n"
             "Step 5: Assessment conducted by Insurance Company and Revenue officials; claim credited directly to bank account.")
        ]
    },
    {
        "filename": "sukanya_samriddhi_yojana.pdf",
        "title": "SUKANYA SAMRIDDHI YOJANA (SSY) - BETI BACHAO BETI PADHAO CAMPAIGN",
        "ministry": "Department of Posts, Ministry of Communications & Ministry of Finance, Government of India",
        "category": "Girl Child & Financial Savings",
        "level": "Central",
        "url": "https://www.indiapost.gov.in/Financial/pages/content/sukanya-samridhi-account.aspx",
        "sections": [
            ("1. Overview & Scheme Objectives",
             "Sukanya Samriddhi Yojana (SSY) is a government-backed small deposit savings scheme launched under the Beti Bachao Beti Padhao campaign. It is designed to build a dedicated education and marriage fund for the female child with attractive tax-free sovereign guaranteed returns."),
            ("2. Financial Terms & Interest Rate",
             "- Current Interest Rate: 8.2% per annum (compounded annually, subject to quarterly revision by Ministry of Finance).\n"
             "- Minimum Annual Deposit: Rs 250 per financial year.\n"
             "- Maximum Annual Deposit: Rs 1,50,000 per financial year.\n"
             "- Tax Benefit: Triple tax exemption under EEE status (Section 80C deduction, interest exempt, maturity exempt).\n"
             "- Deposit Period: Deposits must be made for 15 years from account opening date.\n"
             "- Maturity Period: 21 years from account opening or upon marriage of the girl after attaining 18 years."),
            ("3. Eligibility Criteria",
             "- Account can be opened by biological parents or legal guardians for a girl child from her birth up to age 10 years.\n"
             "- Maximum of two accounts per family (allowed for three in case of twins/triplets in first or second order).\n"
             "- The girl child must be an Indian citizen and resident throughout the account tenure."),
            ("4. Required Documents Checklist",
             "1. Birth Certificate of the girl child (mandatory, issued by municipal authority/registrar).\n"
             "2. Aadhaar Card of parent / legal guardian.\n"
             "3. PAN Card of parent / legal guardian.\n"
             "4. Proof of address (Voter ID, Passport, Electricity Bill).\n"
             "5. Medical certificate in case of twins/triplets."),
            ("5. Step-by-Step Account Opening Procedure",
             "Step 1: Visit any Post Office or authorized Commercial / Public Sector Bank branch.\n"
             "Step 2: Collect and fill Form-1 (Sukanya Samriddhi Account Opening Form).\n"
             "Step 3: Attach girl child birth certificate and parent KYC documents.\n"
             "Step 4: Deposit initial amount (minimum Rs 250 in cash/cheque/DD).\n"
             "Step 5: Collect SSY Passbook containing account number, girl child details, and nomination details.\n"
             "Step 6: Partial withdrawal up to 50% of balance permitted after girl turns 18 for higher education admission.")
        ]
    },
    {
        "filename": "pm_mudra_yojana.pdf",
        "title": "PRADHAN MANTRI MUDRA YOJANA (PMMY) - MICRO-ENTERPRISE CREDIT SCHEME",
        "ministry": "Department of Financial Services, Ministry of Finance, Government of India",
        "category": "MSME, Livelihood & Business Loans",
        "level": "Central",
        "url": "https://www.mudra.org.in",
        "sections": [
            ("1. Overview & Loan Categories",
             "Pradhan Mantri MUDRA Yojana (PMMY) provides collateral-free institutional credit up to Rs 10 Lakh to micro and small non-farm, non-corporate enterprises. Loans are classified into three stages:\n"
             "- Shishu: Loans up to Rs 50,000 (for starters/early-stage micro units).\n"
             "- Kishore: Loans from Rs 50,001 to Rs 5,00,000 (for established units seeking working capital/machinery).\n"
             "- Tarun: Loans from Rs 5,00,001 to Rs 10,00,000 (for expansion of running businesses).\n"
             "- Tarun Plus: Up to Rs 20 Lakh for entrepreneurs who have successfully repaid previous Tarun loans."),
            ("2. Eligibility Criteria",
             "- Any Indian citizen with a feasible business plan for non-farm income-generating micro enterprises.\n"
             "- Eligible sectors: Manufacturing, trading, retail, services, transport operators, food processing, artisans.\n"
             "- Applicant must not be a defaulter to any bank or financial institution.\n"
             "- Collateral: No collateral security required for loans up to Rs 10 Lakh under Credit Guarantee Fund for Micro Units (CGFMU)."),
            ("3. Required Documents Checklist",
             "1. Aadhaar Card / Voter ID / Passport for identity and address proof.\n"
             "2. PAN Card of applicant / business entity.\n"
             "3. Business Address Proof (Shop & Establishment Act certificate, Udyam Registration).\n"
             "4. Bank account statement for last 6 months.\n"
             "5. Project Report / Quotation of machinery/equipment to be purchased.\n"
             "6. Passport-size photographs (2 copies)."),
            ("4. Application Procedure",
             "Step 1: Prepare business plan and determine loan tier (Shishu, Kishore, or Tarun).\n"
             "Step 2: Apply online at Udyami Mitra portal (https://www.udyamimitra.in) or visit any Public, Private, Regional Rural Bank or NBFC/MFI.\n"
             "Step 3: Fill MUDRA loan application form and submit business profile with KYC.\n"
             "Step 4: Bank assesses proposal and sanctions loan within 7-14 working days.\n"
             "Step 5: MUDRA Debit Card issued for working capital overdraft withdrawal.")
        ]
    },
    {
        "filename": "atal_pension_yojana.pdf",
        "title": "ATAL PENSION YOJANA (APY) - UNIVERSAL SOCIAL SECURITY PENSION SCHEME",
        "ministry": "Pension Fund Regulatory and Development Authority (PFRDA), Ministry of Finance, Government of India",
        "category": "Social Security & Pension",
        "level": "Central",
        "url": "https://www.npscra.nsdl.co.in/scheme-details.php",
        "sections": [
            ("1. Overview & Benefits",
             "Atal Pension Yojana (APY) is a periodic guaranteed pension scheme targeted at unorganized sector workers. It guarantees a monthly pension of Rs 1,000, Rs 2,000, Rs 3,000, Rs 4,000, or Rs 5,000 after attaining 60 years of age, depending on contribution amount and entry age. The pension is paid for life to subscriber, then to spouse, and on demise of both, entire accumulated pension wealth is returned to nominee."),
            ("2. Eligibility Criteria",
             "- Citizen of India.\n"
             "- Entry Age: Minimum 18 years, Maximum 40 years.\n"
             "- Contribution Period: Minimum 20 years of continuous contributions until age 60.\n"
             "- Exclusions: From October 1, 2022, any citizen who is or has been an Income Tax payer under the Income Tax Act is NOT eligible to join APY.\n"
             "- Must possess an active savings bank account or post office savings account."),
            ("3. Monthly Contribution Slabs",
             "- For Entry Age 18: Monthly contribution is Rs 42 for Rs 1,000 pension; Rs 210 for Rs 5,000 pension.\n"
             "- For Entry Age 30: Monthly contribution is Rs 116 for Rs 1,000 pension; Rs 577 for Rs 5,000 pension.\n"
             "- For Entry Age 40: Monthly contribution is Rs 291 for Rs 1,000 pension; Rs 1,454 for Rs 5,000 pension.\n"
             "- Contributions are auto-debited from linked bank account monthly, quarterly, or half-yearly."),
            ("4. Required Documents Checklist",
             "1. Aadhaar Card (primary KYC).\n"
             "2. Savings Bank Account details with auto-debit consent mandate.\n"
             "3. Mobile number linked to bank account for contribution notifications.\n"
             "4. Spouse and Nominee details (Aadhaar number and date of birth)."),
            ("5. Registration Process",
             "Step 1: Approach the bank branch or post office where you hold a savings bank account.\n"
             "Step 2: Fill APY Registration Form specifying chosen monthly pension slab (Rs 1,000 - Rs 5,000).\n"
             "Step 3: Provide auto-debit mandate authorising deduction on designated dates.\n"
             "Step 4: Permanent Retirement Account Number (PRAN) is generated and APY e-PRAN card can be downloaded from NSDL portal.")
        ]
    },
    {
        "filename": "pmegp.pdf",
        "title": "PRIME MINISTER'S EMPLOYMENT GENERATION PROGRAMME (PMEGP)",
        "ministry": "Ministry of Micro, Small and Medium Enterprises (MSME), Government of India (Implemented by KVIC)",
        "category": "Employment & Self-Employment Subsidy",
        "level": "Central",
        "url": "https://www.kviconline.gov.in/pmegpeportal",
        "sections": [
            ("1. Overview & Scheme Scope",
             "PMEGP is a flagship credit-linked subsidy programme aimed at generating self-employment opportunities through establishment of micro-enterprises in non-farm sectors. Beneficiaries receive bank finance with government margin money subsidy ranging from 15% to 35% of total project cost."),
            ("2. Financial Limits & Subsidy Slabs",
             "- Maximum Project Cost: Rs 50 Lakh for Manufacturing sector; Rs 20 Lakh for Service / Business sector.\n"
             "- Subsidy Rates (Margin Money):\n"
             "  * General Category: 15% in Urban areas (own contribution 10%), 25% in Rural areas (own contribution 10%).\n"
             "  * Special Categories (SC/ST/OBC/Minorities/Women/Ex-servicemen/PH/NER/Hill/Border): 25% in Urban areas (own contribution 5%), 35% in Rural areas (own contribution 5%).\n"
             "- Balance 60% to 75% of project cost is financed by bank as term loan and working capital."),
            ("3. Eligibility Criteria",
             "- Any individual aged 18 years and above.\n"
             "- Minimum Educational Qualification: At least Class 8th pass for projects above Rs 10 Lakh in manufacturing and above Rs 5 Lakh in service sector.\n"
             "- Existing units or units already availing government subsidy under other central/state schemes are NOT eligible.\n"
             "- Only new micro units are eligible under first loan phase."),
            ("4. Required Documents Checklist",
             "1. Aadhaar Card and PAN Card.\n"
             "2. Detailed Project Report (DPR) detailing capital expenditure and working capital requirements.\n"
             "3. Educational qualification certificate / marksheet (8th standard or higher).\n"
             "4. Special category certificate (Caste certificate, disability certificate, ex-servicemen certificate) if claiming 25-35% subsidy.\n"
             "5. Rural area certificate issued by Gram Panchayat / Revenue Officer (for rural subsidy rate).\n"
             "6. EDP Training completion certificate (mandatory before loan disbursement, provided free by KVIC)."),
            ("5. Step-by-Step Online Application Procedure",
             "Step 1: Visit the KVIC PMEGP e-Portal at https://www.kviconline.gov.in/pmegpeportal.\n"
             "Step 2: Click 'Apply for New Unit (Individual)' and enter 12-digit Aadhaar number.\n"
             "Step 3: Fill personal details, sponsoring agency (KVIC/KVIB/DIC), financing bank branch, and project cost.\n"
             "Step 4: Upload DPR, caste certificate, education proof, and submit.\n"
             "Step 5: District Level Task Force Committee (DLTFC) scrutinizes and forwards application to financing bank.\n"
             "Step 6: Bank sanctions loan and claims Margin Money subsidy from KVIC which is kept in 3-year term deposit lock-in.")
        ]
    },
    {
        "filename": "e_shram_card.pdf",
        "title": "E-SHRAM PORTAL - NATIONAL DATABASE OF UNORGANISED WORKERS (NDUW)",
        "ministry": "Ministry of Labour and Employment, Government of India",
        "category": "Labour Welfare & Social Security",
        "level": "Central",
        "url": "https://eshram.gov.in",
        "sections": [
            ("1. Overview & Objectives",
             "e-Shram is the first-ever National Database of Unorganised Workers (NDUW) created to identify, register, and deliver social security benefits to unorganised workers across India. Enrolled workers are issued a 12-digit Universal Account Number (UAN) e-Shram card that is recognized nationwide."),
            ("2. Benefits to Registered Workers",
             "- Accidental Insurance Cover under PMSBY: Rs 2,00,000 on accidental death or permanent total disability; Rs 1,00,000 on partial disability.\n"
             "- Seamless portability of social security welfare benefits during interstate migration.\n"
             "- Direct cash assistance during national pandemics / disasters (as seen during COVID-19 relief).\n"
             "- Priority integration with social security schemes like PM-SYM, PM-JAY, and National Apprenticeship Promotion."),
            ("3. Eligibility Criteria",
             "- Occupation: Any unorganised worker (construction worker, migrant worker, gig & platform worker, street vendor, domestic worker, agriculture worker, auto/cab driver, fisherfolk, brick kiln worker).\n"
             "- Age Limit: Between 16 and 59 years of age.\n"
             "- Exclusion: Must NOT be an active member of EPFO (Employees' Provident Fund) or ESIC (Employees' State Insurance).\n"
             "- Exclusion: Must NOT be an Income Tax payer."),
            ("4. Required Documents Checklist",
             "1. Aadhaar Number (Mandatory: Aadhaar must be linked to active mobile number for OTP).\n"
             "2. Active Bank Account details (Account Number, Bank Name, and IFSC).\n"
             "3. Mobile number.\n"
             "4. Occupation details (Primary and secondary occupation code as per National Classification of Occupations NCO)."),
            ("5. Self-Registration & Card Download Procedure",
             "Step 1: Open https://eshram.gov.in and click 'Register on e-Shram'.\n"
             "Step 2: Enter Aadhaar-linked mobile number and captcha, submit OTP.\n"
             "Step 3: Authenticate identity using Aadhaar e-KYC (OTP, fingerprint, or iris scan).\n"
             "Step 4: Verify pre-filled demographic details from UIDAI.\n"
             "Step 5: Fill residential address, educational qualification, occupation/skill, and bank account details.\n"
             "Step 6: Preview summary and submit. The 12-digit UAN Card is generated instantly and can be downloaded or printed for free.")
        ]
    },
    {
        "filename": "pm_jan_dhan_yojana.pdf",
        "title": "PRADHAN MANTRI JAN-DHAN YOJANA (PMJDY) - FINANCIAL INCLUSION MISSION",
        "ministry": "Department of Financial Services, Ministry of Finance, Government of India",
        "category": "Banking & Financial Inclusion",
        "level": "Central",
        "url": "https://pmjdy.gov.in",
        "sections": [
            ("1. Overview & Core Pillars",
             "PMJDY is the National Mission for Financial Inclusion aimed at ensuring universal access to banking services with at least one basic banking account for every unbanked adult. It guarantees zero minimum balance requirements, free debit card, and built-in insurance protections."),
            ("2. Key Financial Benefits",
             "- Zero Balance Account: No requirement of maintaining minimum balance; zero penalty fees.\n"
             "- Free RuPay Debit Card with built-in Accidental Insurance Cover of Rs 2,00,000 (for accounts opened after August 28, 2018).\n"
             "- Overdraft (OD) Facility: Up to Rs 10,000 available to one account per household (preferably female head) after 6 months of satisfactory account operation; no conditions for OD up to Rs 2,000.\n"
             "- Direct Benefit Transfer (DBT): Direct crediting of subsidies from PM-KISAN, PMAY, MGNREGA, and LPG subsidy into account without leakage.\n"
             "- Life Insurance cover of Rs 30,000 payable upon death of beneficiary (for accounts opened during initial phase)."),
            ("3. Eligibility Criteria",
             "- Any Indian citizen aged 10 years and above.\n"
             "- Minors above 10 years can operate accounts independently or with legal guardian.\n"
             "- Any individual who does not have an existing basic savings bank deposit account (BSBDA) at any bank."),
            ("4. Required Documents Checklist",
             "1. Aadhaar Card (sufficient standalone document for identity and address).\n"
             "2. If Aadhaar is not available: Voter ID, Driving Licence, PAN Card, Passport, or NREGA Job Card.\n"
             "3. If officially valid documents (OVD) are not available: Small Account can be opened with self-attested photograph and signature/thumb impression (valid for 12 months).\n"
             "4. Two passport-size photographs."),
            ("5. Account Opening Steps",
             "Step 1: Visit any commercial bank branch, regional rural bank, or Bank Mitra / Business Correspondent (BC) kiosk.\n"
             "Step 2: Collect PMJDY Account Opening Form (available in Hindi, English, and regional languages).\n"
             "Step 3: Fill personal details, nominee details, and submit along with Aadhaar photocopy.\n"
             "Step 4: Bank Mitra registers biometric thumbprint and opens account instantly.\n"
             "Step 5: Account passbook and personalized RuPay Debit Card are issued free of charge.")
        ]
    },
    {
        "filename": "nfsa_ration_card.pdf",
        "title": "NATIONAL FOOD SECURITY ACT (NFSA) - TARGETED PUBLIC DISTRIBUTION SYSTEM",
        "ministry": "Department of Food and Public Distribution, Ministry of Consumer Affairs, Government of India",
        "category": "Food Security & Social Welfare",
        "level": "Central & State Joint",
        "url": "https://dfpd.gov.in and https://nfsa.gov.in",
        "sections": [
            ("1. Overview & Legal Entitlement",
             "The National Food Security Act (NFSA), 2013 legally entitles up to 75% of rural and 50% of urban population (over 81 crore citizens) to receive subsidized foodgrains under the Targeted Public Distribution System (TPDS). Under Pradhan Mantri Garib Kalyan Anna Yojana (PMGKAY), foodgrains are provided 100% free of cost."),
            ("2. Beneficiary Categories & Grain Entitlements",
             "- Antyodaya Anna Yojana (AAY): Poorest of the poor families receive 35 kg of foodgrains per family per month (fixed allocation regardless of family size).\n"
             "- Priority Households (PHH): Eligible low-income and vulnerable families receive 5 kg of foodgrains per person per month.\n"
             "- Pricing: Under the central decision effective 2023-2028, NFSA grains (Rice, Wheat, Coarse Grains) are distributed completely FREE at Fair Price Shops (FPS).\n"
             "- One Nation One Ration Card (ONORC): Beneficiaries can lift entitled foodgrains from any biometric e-PoS Fair Price Shop anywhere in India using Aadhaar."),
            ("3. Eligibility Criteria & Identification",
             "- Beneficiaries identified by respective State/UT Governments based on socio-economic criteria.\n"
             "- Rural Inclusion: Agricultural landless labourers, marginal farmers, rural artisans, households headed by widows, terminally ill persons, primitive tribal households.\n"
             "- Urban Inclusion: Daily wage earners, domestic workers, rickshaw pullers, street vendors, construction labourers, beggars, homeless destitute.\n"
             "- Exclusion: Households with members owning pucca houses of specified area, motorized four-wheelers, regular government employees, or income taxpayers."),
            ("4. Required Documents Checklist",
             "1. Aadhaar Card of all family members to be seeded on Ration Card.\n"
             "2. Domicile / Residence Proof (Electricity bill, LPG connection book, rent agreement).\n"
             "3. Income Certificate issued by Revenue Authority (Tahsildar / Village Administrative Officer).\n"
             "4. Recent passport-size family photograph showing family head.\n"
             "5. Bank account passbook of the female head of the family (designated head of household under NFSA)."),
            ("5. Application Procedure",
             "Step 1: Visit state food and civil supplies portal (e.g., ahara.kar.nic.in in Karnataka, fcs.up.gov.in in UP) or nearest Gram One / CSC / Seva Kendra.\n"
             "Step 2: Submit application for New BPL / PHH / AAY Ration Card with Aadhaar e-KYC of all members.\n"
             "Step 3: Food Inspector / Revenue Inspector conducts field verification of economic status.\n"
             "Step 4: Upon verification, digital Ration Card is approved and physical RC or e-Ration card is issued.\n"
             "Step 5: Collect foodgrains monthly by biometric fingerprint authentication at any Fair Price Shop.")
        ]
    },
    {
        "filename": "senior_citizen_savings_scheme.pdf",
        "title": "SENIOR CITIZEN SAVINGS SCHEME (SCSS) - SECURED RETIREMENT INCOME",
        "ministry": "Department of Economic Affairs, Ministry of Finance, Government of India",
        "category": "Senior Citizens & Retirement Savings",
        "level": "Central",
        "url": "https://www.indiapost.gov.in and https://rbi.org.in",
        "sections": [
            ("1. Overview & Scheme Highlights",
             "Senior Citizen Savings Scheme (SCSS) is a premier government-guaranteed small savings scheme designed to provide senior citizens with a steady and secure quarterly retirement income with highest sovereign safety and attractive interest rates."),
            ("2. Financial Terms & Interest Payments",
             "- Current Interest Rate: 8.2% per annum paid quarterly on 1st working day of April, July, October, and January.\n"
             "- Minimum Deposit: Rs 1,000.\n"
             "- Maximum Deposit Limit: Rs 30,00,000 (enhanced from Rs 15 Lakh in Budget 2023).\n"
             "- Tenure: 5 years (can be extended in blocks of 3 years indefinitely upon application).\n"
             "- Tax Deductions: Investment qualifies for tax deduction under Section 80C up to Rs 1.5 Lakh per financial year; interest is taxable as per income slab with TDS applicable above Rs 50,000."),
            ("3. Eligibility Criteria",
             "- Indian citizens aged 60 years or above.\n"
             "- Retired civilian employees aged 55 to 60 years who have retired on superannuation or VRS, provided account is opened within 1 month of receipt of retirement benefits.\n"
             "- Retired Defence personnel aged 50 years and above (subject to conditions).\n"
             "- Exclusions: Non-Resident Indians (NRIs) and Persons of Indian Origin (PIO) / Hindu Undivided Families (HUF) are NOT eligible to invest in SCSS."),
            ("4. Required Documents Checklist",
             "1. Aadhaar Card (mandatory identification and address proof).\n"
             "2. PAN Card (mandatory for deposits above Rs 50,000).\n"
             "3. Age Proof (Voter ID, Passport, Birth Certificate, School Leaving Certificate).\n"
             "4. Superannuation / Retirement Benefit Certificate (for retired individuals aged 55-60).\n"
             "5. Two passport-size color photographs.\n"
             "6. Cheque / DD for deposit amount."),
            ("5. Step-by-Step Account Opening Steps",
             "Step 1: Visit any Post Office offering savings bank facilities or authorized branches of Public and Private Commercial Banks.\n"
             "Step 2: Fill Form-A (SCSS Account Opening Form) and select quarterly interest credit mode into savings bank account.\n"
             "Step 3: Attach KYC documents, retirement proof (if under 60), and nominee details.\n"
             "Step 4: Deposit funds via cheque/DD (cash permitted only up to Rs 1 Lakh).\n"
             "Step 5: Bank/Post Office issues SCSS Passbook containing deposit certificate and quarterly interest schedule.")
        ]
    },
    {
        "filename": "ladli_behna_yojana_mp.pdf",
        "title": "MUKHYAMANTRI LADLI BEHNA YOJANA - WOMEN FINANCIAL EMPOWERMENT SCHEME",
        "ministry": "Department of Women and Child Development, Government of Madhya Pradesh",
        "category": "Women Empowerment & Direct Income Support",
        "level": "State (Madhya Pradesh)",
        "url": "https://cmladlibehna.mp.gov.in",
        "sections": [
            ("1. Overview & Scheme Objectives",
             "Mukhyamantri Ladli Behna Yojana is a state welfare initiative by the Government of Madhya Pradesh to foster economic self-reliance, improve nutritional health, and enhance decision-making authority among women. Under the scheme, monthly financial assistance of Rs 1,250 is directly credited to beneficiary bank accounts via DBT on the 10th of every month."),
            ("2. Monthly Financial Assistance",
             "- Monthly direct benefit transfer: Rs 1,250 per month (Rs 15,000 annually) transferred directly to woman's Aadhaar-linked DBT enabled bank account.\n"
             "- Direct cashless assistance credited without any middlemen or commission fees."),
            ("3. Strict Eligibility Criteria",
             "- State Domicile: The woman must be a permanent resident and domicile of Madhya Pradesh state.\n"
             "- Age Limit: Between 21 and 60 years of age (married, widowed, divorced, or abandoned women).\n"
             "- Income Ceiling: Total annual family income must be LESS than Rs 2,50,000 (Rs 2.5 Lakh per annum).\n"
             "- Landholding Ceiling: Family must own LESS than 5 acres of agricultural land.\n"
             "- Four-Wheeler Exclusion: Family must NOT own any four-wheeler motorized vehicle (excluding tractor).\n"
             "- Tax Exclusion: No member of the family should be an Income Tax payer.\n"
             "- Government Employment: No member of the family should be a permanent or contractual employee of Central/State Government, Board, Corporation, or receiving pension > Rs 10,000/mo."),
            ("4. Required Documents Checklist",
             "1. Samagra Family ID and Individual Samagra Member ID (mandatory 9-digit ID).\n"
             "2. Aadhaar Card (mandatory, must be e-KYC linked with Samagra ID).\n"
             "3. Active Personal Bank Account Passbook (must be Aadhaar-seeded with active Direct Benefit Transfer DBT).\n"
             "4. Mobile number registered on Samagra portal for OTP confirmation."),
            ("5. Application & Verification Procedure",
             "Step 1: Complete Samagra e-KYC by linking Aadhaar on samagra.gov.in or through local CSC / MP Online kiosk.\n"
             "Step 2: Ensure individual bank account is Aadhaar linked with DBT enabled at your bank branch.\n"
             "Step 3: Attend designated Ladli Behna registration camp organized at your local Gram Panchayat / Ward Office.\n"
             "Step 4: Camp in-charge captures live photograph and verifies Samagra ID and Aadhaar biometrics online (no physical paper application required).\n"
             "Step 5: Receive acknowledgement receipt on mobile via SMS.\n"
             "Step 6: Provisional eligibility list displayed on portal; objection resolution conducted by Gram Sabha before final monthly disbursement on 10th of each month.")
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
        fontSize=14,
        leading=17,
        textColor=colors.HexColor('#0f4c81'),
        alignment=1,
        spaceAfter=8
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#4a5568'),
        alignment=1,
        spaceAfter=12
    )

    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1a365d'),
        spaceBefore=10,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2d3748')
    )

    story = []
    story.append(Paragraph(scheme_info["title"], title_style))
    story.append(Paragraph(
        f"<b>SUPPLEMENTARY REFERENCE - Compiled from Official Government Portals (November 2026)</b><br/>"
        f"{scheme_info['ministry']} | Level: {scheme_info['level']} | Category: {scheme_info['category']}<br/>"
        f"Official Portal: {scheme_info['url']}",
        meta_style
    ))
    story.append(Spacer(1, 8))

    for sec_title, sec_content in scheme_info["sections"]:
        story.append(Paragraph(sec_title, section_header))
        formatted_content = sec_content.replace("\n", "<br/>")
        story.append(Paragraph(formatted_content, body_style))
        story.append(Spacer(1, 6))

    doc.build(story)
    print(f"Generated: {filepath.name}")

def main():
    print("Generating 10 additional reference scheme PDFs...")
    for s in EXTRA_SCHEMES:
        build_pdf(s)
    print("All 10 supplementary reference PDFs generated successfully!")

if __name__ == "__main__":
    main()
