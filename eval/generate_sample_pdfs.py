import fitz
from pathlib import Path

EVAL_DATA_DIR = Path(r"C:\Users\hites\.gemini\antigravity-ide\scratch\speech-and-text-conversion-sentimentanalysis-api\eval\data")
EVAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── PDF 1: Cloud Data Lakehouse Architecture Spec ────────────────────────────
doc1 = fitz.open()

# Page 1
page1_text = """CLOUD DATA LAKEHOUSE ARCHITECTURE & GOVERNANCE SPECIFICATION
Document ID: DLH-SPEC-2026-V3
Classification: Internal Engineering Standard
Authors: Enterprise Data Architecture Team

1. Executive Overview
The Lakehouse architecture unifies high-throughput streaming ingestion with ACID-compliant
analytical querying using Apache Iceberg tables backed by Google Cloud Storage (GCS).
The storage tier employs GCS Standard for active partitions and Nearline storage for partitions
older than 90 days. The primary cluster operates across the us-central1 (Iowa) region with
a multi-region replication bucket in us-east1 (South Carolina).

2. Ingestion Pipeline & SLAs
Raw transactional events are captured from Kafka topics at a sustained ingestion SLA of under
500 milliseconds (p95). The Bronze layer enforces append-only immutability, recording each event's
SHA-256 payload checksum and an ingestion timestamp.
The Bronze to Silver compaction job runs every 15 minutes, deduplicating events by transaction_id
and applying UTC timestamp normalization. The target data freshness for the Silver layer is
guaranteed at 20 minutes end-to-end.
"""

p1 = doc1.new_page()
p1.insert_textbox(fitz.Rect(50, 50, 550, 750), page1_text, fontsize=11, fontname="helv")

# Page 2
page2_text = """3. Storage Formats & Catalog Configurations
All transformed tables in the Gold analytical layer are formatted as Apache Iceberg v2 tables.
Metadata operations utilize the Google Cloud BigLake metastore catalog.
Parquet files are compressed using ZSTD compression at compression level 3, balancing CPU
decompression speed with an average 4.2x space reduction over uncompressed CSVs.
Row-group size is standardized at 128 MB with a dictionary page limit of 1 MB.

4. Data Retention and Security Policies
- Active raw payload retention: 30 days in Bronze immutable bucket.
- Aggregated financial mart retention: 7 years to satisfy regulatory compliance (SOX / FINRA).
- Encryption standard: All data at rest is encrypted using Customer-Managed Encryption Keys (CMEK)
  provisioned through Google Cloud KMS, rotated automatically every 90 days.
- Access control is governed strictly through IAM fine-grained row-level security tags,
  enforcing that PII columns (SSN, credit_card_number) are masked with SHA-256 salt hashes.
"""

p2 = doc1.new_page()
p2.insert_textbox(fitz.Rect(50, 50, 550, 750), page2_text, fontsize=11, fontname="helv")

pdf1_path = EVAL_DATA_DIR / "cloud_data_lakehouse_architecture.pdf"
doc1.save(str(pdf1_path))
doc1.close()
print(f"Generated {pdf1_path.name}")


# ── PDF 2: Clinical Trial Protocol for Cardiology Study ──────────────────────
doc2 = fitz.open()

# Page 1
doc2_p1_text = """CLINICAL TRIAL PROTOCOL: CARDIO-VASCULAR EFFICACY (CV-EVAL-402)
Study Phase: Phase IIb Double-Blind Randomized Controlled Trial
Investigational Product: Cardiovastin (CV-882)
Sponsor: Global Biopharma Research Consortium
Version: 4.1 | Date: January 15, 2026

1. Study Objectives and Hypotheses
The primary objective of this trial is to evaluate the reduction in 12-week mean systolic blood
pressure (SBP) in adult patients diagnosed with Stage 2 essential hypertension.
The secondary objectives include assessing changes in left ventricular ejection fraction (LVEF)
and monitoring renal biomarker clearance (serum creatinine and estimated glomerular filtration rate).

2. Patient Population and Sample Size
A total of 450 adult subjects (ages 35 to 75) will be enrolled across 12 clinical investigative
sites in North America. Participants must have documented resting systolic blood pressure between
140 mmHg and 179 mmHg at the time of screening.
Randomization will be stratified 1:1:1 into three parallel cohorts of 150 subjects each:
- Group A: Cardiovastin 25 mg once daily (oral)
- Group B: Cardiovastin 50 mg once daily (oral)
- Group C: Placebo matching tablet once daily
"""

p2_1 = doc2.new_page()
p2_1.insert_textbox(fitz.Rect(50, 50, 550, 750), doc2_p1_text, fontsize=11, fontname="helv")

# Page 2
doc2_p2_text = """3. Inclusion and Exclusion Criteria
Inclusion Criteria:
- Male or female aged 35 to 75 years inclusive at the time of informed consent.
- Body Mass Index (BMI) between 18.5 and 38.0 kg/m^2.
- Documented compliance with lifestyle diet modifications for at least 4 weeks prior to Day 1.

Exclusion Criteria:
- History of acute myocardial infarction or stroke within 6 months prior to screening.
- Baseline estimated Glomerular Filtration Rate (eGFR) below 30 mL/min/1.73 m^2.
- Known hypersensitivity to vascular angiotensin receptor blockers or synthetic excipients.
- Pregnant or lactating females.

4. Primary Endpoint and Safety Monitoring
The primary efficacy endpoint is the placebo-subtracted change from baseline in mean sitting
trough cuff SBP measured at Week 12. Safety assessments include 12-lead electrocardiograms (ECGs)
recorded at Weeks 0, 4, 8, and 12.
Adverse events will be reviewed on a continuous weekly basis by an independent Data Safety
Monitoring Board (DSMB), with predefined halting criteria triggered if confirmed Grade 3
hypotension events exceed 2.5% in any active treatment arm.
"""

p2_2 = doc2.new_page()
p2_2.insert_textbox(fitz.Rect(50, 50, 550, 750), doc2_p2_text, fontsize=11, fontname="helv")

pdf2_path = EVAL_DATA_DIR / "clinical_cardiology_trial_protocol.pdf"
doc2.save(str(pdf2_path))
doc2.close()
print(f"Generated {pdf2_path.name}")


# ── PDF 3: FinTech Payment Security & Dispute Specification ───────────────────
doc3 = fitz.open()

# Page 1
doc3_p1_text = """FINTECH PAYMENT SECURITY, DISPUTE RESOLUTION & FRAUD PREVENTION
Document Standard: FPS-SEC-809
Issuing Authority: Global Financial Payments Architecture Council
Release Date: February 2026 | Effective Date: March 1, 2026

1. Purpose and Scope
This document specifies technical requirements for point-of-sale (POS) and e-commerce payment
message encryption, velocity throttling thresholds, and automated dispute resolution workflows
for all tier-1 acquiring institutions operating within the payment switch.

2. API Authentication & Message Security
- All incoming payment authorization requests must be transmitted over Transport Layer Security
  (TLS) version 1.3 with mandatory cipher suites supporting forward secrecy.
- Each API payload must include a cryptographic request signature generated via HMAC-SHA256,
  computed using the merchant's dedicated private signing key and an epoch timestamp.
- Payloads with timestamp skew exceeding 300 seconds (5 minutes) are unconditionally rejected
  with HTTP error status 401 Unauthorized to mitigate replay attacks.
"""

p3_1 = doc3.new_page()
p3_1.insert_textbox(fitz.Rect(50, 50, 550, 750), doc3_p1_text, fontsize=11, fontname="helv")

# Page 2
doc3_p2_text = """3. Real-Time Velocity Rules & Anomaly Triggers
The fraud prevention gateway evaluates every incoming transaction against multi-dimensional
velocity rules:
- Card Velocity: A single payment card is permitted a maximum of 5 transaction authorizations
  within any sliding 10-minute window. A 6th authorization within this window automatically
  triggers a temporary 60-minute card hold.
- Amount Discrepancy: Any single transaction amount exceeding 400% of the cardholder's 30-day
  mean transaction value requires Step-Up Two-Factor Authentication (3D-Secure 2.2).
- Geographic Velocity: An impossible travel velocity threshold is defined as physical distance
  between successive card transactions exceeding 800 kilometers per hour.

4. Chargeback and Dispute Timelines
- Initial Merchant Notification: Merchants receive chargeback notices within 24 hours of filing.
- Evidence Submission Window: Merchants have exactly 14 calendar days from the notification date
  to submit rebuttal documentation (proof of delivery, signed receipts, IP address logs).
- Financial Settlement SLA: The issuing bank must complete final dispute arbitration within
  45 calendar days following the submission of rebuttal evidence.
"""

p3_2 = doc3.new_page()
p3_2.insert_textbox(fitz.Rect(50, 50, 550, 750), doc3_p2_text, fontsize=11, fontname="helv")

pdf3_path = EVAL_DATA_DIR / "fintech_payment_security_spec.pdf"
doc3.save(str(pdf3_path))
doc3.close()
print(f"Generated {pdf3_path.name}")
