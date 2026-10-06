import csv
from pathlib import Path
import fitz

DATA_DIR = Path(r"C:\Users\hites\.gemini\antigravity-ide\scratch\speech-and-text-conversion-sentimentanalysis-api\eval\data")
OUTPUT_CSV = Path(r"C:\Users\hites\.gemini\antigravity-ide\scratch\speech-and-text-conversion-sentimentanalysis-api\eval\dataset_v2_draft.csv")

# Extract text of all 8 PDFs for automated verbatim verification
DOC_TEXTS = {}
for pdf_file in DATA_DIR.glob("*.pdf"):
    doc = fitz.open(pdf_file)
    text = " ".join(" ".join(p.get_text().split()) for p in doc)
    DOC_TEXTS[pdf_file.name] = text
    doc.close()

# Assemble 200 questions: 30 existing + 170 new
DATASET = []

# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT 1: cloud_data_lakehouse_architecture.pdf (25 items: 17 fact, 8 adv)
# ══════════════════════════════════════════════════════════════════════════════
doc1 = "cloud_data_lakehouse_architecture.pdf"

# Existing 10 items
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-01", "question_type": "factual",
    "question_text": "What table format is used for all transformed tables in the Gold analytical layer?",
    "ground_truth": "Apache Iceberg v2",
    "evidence_span": "Apache Iceberg v2 tables"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-02", "question_type": "factual",
    "question_text": "What is the sustained ingestion SLA for raw transactional events captured from Kafka topics?",
    "ground_truth": "Under 500 milliseconds (p95)",
    "evidence_span": "under 500 milliseconds (p95)"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-03", "question_type": "factual",
    "question_text": "How frequently does the Bronze to Silver compaction job run?",
    "ground_truth": "Every 15 minutes",
    "evidence_span": "every 15 minutes"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-04", "question_type": "factual",
    "question_text": "What compression algorithm and level are applied to Parquet files?",
    "ground_truth": "ZSTD compression at level 3",
    "evidence_span": "ZSTD compression at compression level 3"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-05", "question_type": "factual",
    "question_text": "How long are aggregated financial marts retained for regulatory compliance?",
    "ground_truth": "7 years",
    "evidence_span": "7 years to satisfy regulatory compliance"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-06", "question_type": "factual",
    "question_text": "How often are Customer-Managed Encryption Keys (CMEK) rotated?",
    "ground_truth": "Automatically every 90 days",
    "evidence_span": "rotated automatically every 90 days"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-07", "question_type": "factual",
    "question_text": "What is the standardized Parquet row-group size?",
    "ground_truth": "128 MB",
    "evidence_span": "standardized at 128 MB"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-ADV-01", "question_type": "adversarial",
    "question_text": "What is the annual cloud infrastructure budget allocated for the Lakehouse cluster?",
    "ground_truth": "The document does not mention an annual cloud infrastructure budget.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-ADV-02", "question_type": "adversarial",
    "question_text": "Which Snowflake data warehouse sizing is recommended for downstream reporting?",
    "ground_truth": "The document does not mention Snowflake; it specifies Google Cloud BigLake metastore catalog and GCS.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-ADV-03", "question_type": "adversarial",
    "question_text": "What version of Apache Flink is used for real-time streaming transformations?",
    "ground_truth": "The document does not mention Apache Flink.",
    "evidence_span": "None (unanswerable)"
})

# New 15 items (10 fact, 5 adv)
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-08", "question_type": "factual",
    "question_text": "What is the document identifier for the Lakehouse architecture specification?",
    "ground_truth": "DLH-SPEC-2026-V3",
    "evidence_span": "DLH-SPEC-2026-V3"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-09", "question_type": "factual",
    "question_text": "What storage tier is used for partitions older than 90 days?",
    "ground_truth": "Nearline storage",
    "evidence_span": "Nearline storage for partitions older than 90 days"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-10", "question_type": "factual",
    "question_text": "In which Google Cloud region does the primary cluster operate?",
    "ground_truth": "us-central1 (Iowa)",
    "evidence_span": "us-central1 (Iowa)"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-11", "question_type": "factual",
    "question_text": "Where is the multi-region replication bucket located?",
    "ground_truth": "us-east1 (South Carolina)",
    "evidence_span": "us-east1 (South Carolina)"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-12", "question_type": "factual",
    "question_text": "What payload checksum is recorded for each raw event in the Bronze layer?",
    "ground_truth": "SHA-256",
    "evidence_span": "SHA-256 payload checksum"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-13", "question_type": "factual",
    "question_text": "By which field are events deduplicated during Bronze to Silver compaction?",
    "ground_truth": "transaction_id",
    "evidence_span": "deduplicating events by transaction_id"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-14", "question_type": "factual",
    "question_text": "What is the guaranteed end-to-end target data freshness for the Silver layer?",
    "ground_truth": "20 minutes end-to-end",
    "evidence_span": "guaranteed at 20 minutes end-to-end"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-15", "question_type": "factual",
    "question_text": "What average space reduction does ZSTD level 3 compression achieve over uncompressed CSVs?",
    "ground_truth": "average 4.2x space reduction",
    "evidence_span": "average 4.2x space reduction over uncompressed CSVs"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-16", "question_type": "factual",
    "question_text": "What is the standardized dictionary page limit for Parquet files?",
    "ground_truth": "1 MB",
    "evidence_span": "dictionary page limit of 1 MB"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-17", "question_type": "factual",
    "question_text": "What is the active raw payload retention period in the Bronze immutable bucket?",
    "ground_truth": "30 days",
    "evidence_span": "30 days in Bronze immutable bucket"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-ADV-04", "question_type": "adversarial",
    "question_text": "What is the minimum CPU core count required for Apache Spark executor nodes?",
    "ground_truth": "The document does not mention CPU core counts or Apache Spark executor sizing.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-ADV-05", "question_type": "adversarial",
    "question_text": "Which AWS S3 lifecycle transition rule is configured for raw telemetry archives?",
    "ground_truth": "The document does not mention AWS S3; storage is managed via Google Cloud Storage (GCS).",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-ADV-06", "question_type": "adversarial",
    "question_text": "What is the maximum allowed network jitter in milliseconds for Kafka mirror makers?",
    "ground_truth": "The document does not mention network jitter thresholds or Kafka mirror makers.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-ADV-07", "question_type": "adversarial",
    "question_text": "Who is the designated Chief Information Security Officer approving CMEK key destruction?",
    "ground_truth": "The document does not mention the Chief Information Security Officer or key destruction approval.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc1, "question_id": "Q-DLH-ADV-08", "question_type": "adversarial",
    "question_text": "What OAuth 2.0 grant type is enforced for client service account token issuance?",
    "ground_truth": "The document does not mention OAuth 2.0 grant types or service account token issuance.",
    "evidence_span": "None (unanswerable)"
})


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT 2: clinical_cardiology_trial_protocol.pdf (25 items: 17 fact, 8 adv)
# ══════════════════════════════════════════════════════════════════════════════
doc2 = "clinical_cardiology_trial_protocol.pdf"

# Existing 10 items
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-01", "question_type": "factual",
    "question_text": "What is the investigational product name and code in the trial?",
    "ground_truth": "Cardiovastin (CV-882)",
    "evidence_span": "Cardiovastin (CV-882)"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-02", "question_type": "factual",
    "question_text": "How many total subjects will be enrolled and how are they stratified across cohorts?",
    "ground_truth": "450 subjects total stratified 1:1:1 into three cohorts of 150 subjects each (Cardiovastin 25 mg, Cardiovastin 50 mg, and Placebo)",
    "evidence_span": "total of 450 adult subjects"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-03", "question_type": "factual",
    "question_text": "What resting systolic blood pressure range is required at screening?",
    "ground_truth": "Between 140 mmHg and 179 mmHg",
    "evidence_span": "between 140 mmHg and 179 mmHg"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-04", "question_type": "factual",
    "question_text": "What is the baseline estimated Glomerular Filtration Rate (eGFR) below which subjects are excluded?",
    "ground_truth": "Below 30 mL/min/1.73 m^2",
    "evidence_span": "below 30 mL/min/1.73 m^2"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-05", "question_type": "factual",
    "question_text": "At what study weeks are 12-lead electrocardiograms (ECGs) scheduled to be recorded?",
    "ground_truth": "Weeks 0, 4, 8, and 12",
    "evidence_span": "Weeks 0, 4, 8, and 12"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-06", "question_type": "factual",
    "question_text": "What threshold of Grade 3 hypotension triggers the predefined study halting criteria?",
    "ground_truth": "Exceeding 2.5% in any active treatment arm",
    "evidence_span": "exceed 2.5% in any active treatment arm"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-07", "question_type": "factual",
    "question_text": "What is the primary efficacy endpoint of the study?",
    "ground_truth": "Placebo-subtracted change from baseline in mean sitting trough cuff SBP measured at Week 12",
    "evidence_span": "placebo-subtracted change from baseline in mean sitting trough cuff SBP measured at Week 12"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-ADV-01", "question_type": "adversarial",
    "question_text": "What is the recommended pediatric dosage for Cardiovastin in children under 12 years old?",
    "ground_truth": "The document does not mention pediatric dosage; the trial is restricted to adults aged 35 to 75.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-ADV-02", "question_type": "adversarial",
    "question_text": "What percentage of participants experienced mild nausea during the Phase I trial?",
    "ground_truth": "The document does not mention Phase I results or nausea rates.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-ADV-03", "question_type": "adversarial",
    "question_text": "What is the commercial retail price per pill approved by the FDA?",
    "ground_truth": "The document does not mention commercial pricing or FDA approval.",
    "evidence_span": "None (unanswerable)"
})

# New 15 items (10 fact, 5 adv)
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-08", "question_type": "factual",
    "question_text": "What is the protocol identifier code for the clinical trial?",
    "ground_truth": "CV-EVAL-402",
    "evidence_span": "CV-EVAL-402"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-09", "question_type": "factual",
    "question_text": "What clinical diagnosis is required for patients to participate in the trial?",
    "ground_truth": "Stage 2 essential hypertension",
    "evidence_span": "Stage 2 essential hypertension"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-10", "question_type": "factual",
    "question_text": "What cardiac secondary objective is monitored alongside renal biomarker clearance?",
    "ground_truth": "left ventricular ejection fraction (LVEF)",
    "evidence_span": "left ventricular ejection fraction (LVEF)"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-11", "question_type": "factual",
    "question_text": "How many clinical investigative sites in North America are enrolling participants?",
    "ground_truth": "12 clinical investigative sites",
    "evidence_span": "12 clinical investigative sites in North America"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-12", "question_type": "factual",
    "question_text": "What daily oral dosage of Cardiovastin is prescribed to subjects in Group B?",
    "ground_truth": "Cardiovastin 50 mg once daily (oral)",
    "evidence_span": "Cardiovastin 50 mg once daily (oral)"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-13", "question_type": "factual",
    "question_text": "What Body Mass Index (BMI) range is required for trial inclusion?",
    "ground_truth": "between 18.5 and 38.0 kg/m^2",
    "evidence_span": "between 18.5 and 38.0 kg/m^2"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-14", "question_type": "factual",
    "question_text": "For how long must participants document compliance with diet modifications prior to Day 1?",
    "ground_truth": "at least 4 weeks prior to Day 1",
    "evidence_span": "at least 4 weeks prior to Day 1"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-15", "question_type": "factual",
    "question_text": "What cardiovascular history within 6 months prior to screening causes patient exclusion?",
    "ground_truth": "acute myocardial infarction or stroke within 6 months",
    "evidence_span": "acute myocardial infarction or stroke within 6 months prior to screening"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-16", "question_type": "factual",
    "question_text": "Which independent entity reviews adverse events on a continuous weekly basis?",
    "ground_truth": "independent Data Safety Monitoring Board (DSMB)",
    "evidence_span": "independent Data Safety Monitoring Board (DSMB)"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-17", "question_type": "factual",
    "question_text": "What version and date are specified on the cardiology trial protocol?",
    "ground_truth": "Version: 4.1 | Date: January 15, 2026",
    "evidence_span": "Version: 4.1 | Date: January 15, 2026"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-ADV-04", "question_type": "adversarial",
    "question_text": "What is the required fasting blood glucose level in mg/dL for diabetic subgroup stratification?",
    "ground_truth": "The document does not mention fasting blood glucose levels or diabetic subgroup stratification.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-ADV-05", "question_type": "adversarial",
    "question_text": "How much financial stipend is reimbursed to subjects for each clinical site visit?",
    "ground_truth": "The document does not mention financial compensation or subject travel stipends.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-ADV-06", "question_type": "adversarial",
    "question_text": "Which commercial laboratory assay is specified for measuring high-sensitivity C-reactive protein (hs-CRP)?",
    "ground_truth": "The document does not mention hs-CRP measurements or commercial laboratory assays.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-ADV-07", "question_type": "adversarial",
    "question_text": "What is the shelf life in months of Cardiovastin blister packs at room temperature?",
    "ground_truth": "The document does not mention drug shelf life or blister pack storage stability.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc2, "question_id": "Q-CLIN-ADV-08", "question_type": "adversarial",
    "question_text": "What surgical coronary artery bypass grafting protocol is followed if a patient experiences unstable angina?",
    "ground_truth": "The document does not mention surgical bypass grafting protocols.",
    "evidence_span": "None (unanswerable)"
})


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT 3: fintech_payment_security_spec.pdf (25 items: 17 fact, 8 adv)
# ══════════════════════════════════════════════════════════════════════════════
doc3 = "fintech_payment_security_spec.pdf"

# Existing 10 items
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-01", "question_type": "factual",
    "question_text": "Which version of TLS is required for payment authorization requests?",
    "ground_truth": "TLS version 1.3",
    "evidence_span": "Transport Layer Security (TLS) version 1.3"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-02", "question_type": "factual",
    "question_text": "What cryptographic algorithm is mandated for generating API request signatures?",
    "ground_truth": "HMAC-SHA256",
    "evidence_span": "HMAC-SHA256"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-03", "question_type": "factual",
    "question_text": "What is the maximum permitted timestamp skew before a request is rejected with HTTP 401?",
    "ground_truth": "300 seconds (5 minutes)",
    "evidence_span": "300 seconds (5 minutes)"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-04", "question_type": "factual",
    "question_text": "What action is automatically triggered if a payment card incurs a 6th transaction authorization within 10 minutes?",
    "ground_truth": "A temporary 60-minute card hold",
    "evidence_span": "temporary 60-minute card hold"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-05", "question_type": "factual",
    "question_text": "What transaction amount threshold requires Step-Up Two-Factor Authentication (3D-Secure 2.2)?",
    "ground_truth": "Exceeding 400% of the cardholder's 30-day mean transaction value",
    "evidence_span": "exceeding 400% of the cardholder's 30-day mean transaction value"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-06", "question_type": "factual",
    "question_text": "How many calendar days do merchants have to submit rebuttal documentation for a chargeback?",
    "ground_truth": "Exactly 14 calendar days from the notification date",
    "evidence_span": "exactly 14 calendar days from the notification date"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-07", "question_type": "factual",
    "question_text": "What is the financial settlement SLA for issuing banks to complete dispute arbitration?",
    "ground_truth": "Within 45 calendar days following the submission of rebuttal evidence",
    "evidence_span": "within 45 calendar days following the submission of rebuttal evidence"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-ADV-01", "question_type": "adversarial",
    "question_text": "What is the interchange transaction fee charged for Mastercard debit cards?",
    "ground_truth": "The document does not mention interchange transaction fees.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-ADV-02", "question_type": "adversarial",
    "question_text": "Which biometric hardware scanner model is mandated for in-person POS fingerprint scanning?",
    "ground_truth": "The document does not mention biometric hardware scanners.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-ADV-03", "question_type": "adversarial",
    "question_text": "What cryptocurrency assets are accepted for settlement on the payment switch?",
    "ground_truth": "The document does not mention cryptocurrency assets or settlement.",
    "evidence_span": "None (unanswerable)"
})

# New 15 items (10 fact, 5 adv)
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-08", "question_type": "factual",
    "question_text": "What is the document standard code for the payment security specification?",
    "ground_truth": "FPS-SEC-809",
    "evidence_span": "FPS-SEC-809"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-09", "question_type": "factual",
    "question_text": "Which issuing authority published the payment security standard?",
    "ground_truth": "Global Financial Payments Architecture Council",
    "evidence_span": "Global Financial Payments Architecture Council"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-10", "question_type": "factual",
    "question_text": "What is the official effective date of the payment security specification?",
    "ground_truth": "March 1, 2026",
    "evidence_span": "March 1, 2026"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-11", "question_type": "factual",
    "question_text": "What class of acquiring institutions falls under the scope of this specification?",
    "ground_truth": "tier-1 acquiring institutions",
    "evidence_span": "tier-1 acquiring institutions operating within the payment switch"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-12", "question_type": "factual",
    "question_text": "What cipher suite capability is mandatory alongside TLS version 1.3?",
    "ground_truth": "mandatory cipher suites supporting forward secrecy",
    "evidence_span": "mandatory cipher suites supporting forward secrecy"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-13", "question_type": "factual",
    "question_text": "What parameters are used to compute the HMAC-SHA256 request signature?",
    "ground_truth": "merchant's dedicated private signing key and an epoch timestamp",
    "evidence_span": "merchant's dedicated private signing key and an epoch timestamp"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-14", "question_type": "factual",
    "question_text": "What physical distance velocity between successive transactions triggers impossible travel detection?",
    "ground_truth": "exceeding 800 kilometers per hour",
    "evidence_span": "exceeding 800 kilometers per hour"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-15", "question_type": "factual",
    "question_text": "What specific authentication protocol version is required for Step-Up Two-Factor Authentication?",
    "ground_truth": "3D-Secure 2.2",
    "evidence_span": "3D-Secure 2.2"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-16", "question_type": "factual",
    "question_text": "Within what timeframe must merchants receive initial chargeback notification after filing?",
    "ground_truth": "within 24 hours of filing",
    "evidence_span": "within 24 hours of filing"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-17", "question_type": "factual",
    "question_text": "What three types of rebuttal documentation are cited for merchant chargeback defense?",
    "ground_truth": "proof of delivery, signed receipts, IP address logs",
    "evidence_span": "proof of delivery, signed receipts, IP address logs"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-ADV-04", "question_type": "adversarial",
    "question_text": "What is the daily maximum cash withdrawal limit in Euros for automated teller machines?",
    "ground_truth": "The document does not mention ATM cash withdrawal limits or currency caps in Euros.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-ADV-05", "question_type": "adversarial",
    "question_text": "Which hardware security module (HSM) vendor is certified for PIN encryption key storage?",
    "ground_truth": "The document does not mention hardware security module vendors or PIN encryption.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-ADV-06", "question_type": "adversarial",
    "question_text": "What percentage interchange discount is granted to nonprofit charitable merchants?",
    "ground_truth": "The document does not mention interchange discount rates or nonprofit merchant tiers.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-ADV-07", "question_type": "adversarial",
    "question_text": "What is the penalty fee in dollars charged to merchants with a chargeback ratio exceeding 1%?",
    "ground_truth": "The document does not mention chargeback penalty fees or merchant ratio thresholds.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc3, "question_id": "Q-FIN-ADV-08", "question_type": "adversarial",
    "question_text": "Which SWIFT messaging MT format is specified for international cross-border settlements?",
    "ground_truth": "The document does not mention SWIFT messaging or cross-border MT wire formats.",
    "evidence_span": "None (unanswerable)"
})


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT 4: aerospace_avionics_thermal_spec.pdf (25 items: 18 fact, 7 adv)
# ══════════════════════════════════════════════════════════════════════════════
doc4 = "aerospace_avionics_thermal_spec.pdf"

DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-01", "question_type": "factual",
    "question_text": "What is the document identifier for the avionics thermal management specification?",
    "ground_truth": "AERO-SPEC-FCC900-V4",
    "evidence_span": "AERO-SPEC-FCC900-V4"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-02", "question_type": "factual",
    "question_text": "What is the designation of the primary flight control computer defined in the specification?",
    "ground_truth": "FCC-900",
    "evidence_span": "FCC-900 Primary Flight Control Computer"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-03", "question_type": "factual",
    "question_text": "In which bay of the aircraft does the flight control computer operate?",
    "ground_truth": "unpressurized forward avionics bay",
    "evidence_span": "unpressurized forward avionics bay"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-04", "question_type": "factual",
    "question_text": "What serial telemetry bus architecture connects the quad-redundant processor modules?",
    "ground_truth": "dual-redundant CAN-FD serial telemetry bus",
    "evidence_span": "dual-redundant CAN-FD serial telemetry bus"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-05", "question_type": "factual",
    "question_text": "What is the standardized bitrate of the CAN-FD serial telemetry bus?",
    "ground_truth": "5.0 Mbps",
    "evidence_span": "5.0 Mbps"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-06", "question_type": "factual",
    "question_text": "What is the cyclic telemetry broadcast interval for the flight computer?",
    "ground_truth": "exactly 20 milliseconds",
    "evidence_span": "exactly 20 milliseconds"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-07", "question_type": "factual",
    "question_text": "What is the continuous operational ambient temperature envelope for the FCC-900?",
    "ground_truth": "-40.0 deg C to +85.0 deg C",
    "evidence_span": "-40.0 deg C to +85.0 deg C"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-08", "question_type": "factual",
    "question_text": "What is the non-operational storage survival temperature range?",
    "ground_truth": "-55.0 deg C to +105.0 deg C",
    "evidence_span": "-55.0 deg C to +105.0 deg C"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-09", "question_type": "factual",
    "question_text": "What is the maximum permitted silicon semiconductor junction temperature?",
    "ground_truth": "105.0 deg C",
    "evidence_span": "105.0 deg C"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-10", "question_type": "factual",
    "question_text": "What dielectric liquid coolant fluid is specified for active closed-loop cooling?",
    "ground_truth": "Polyalphaolefin (PAO)",
    "evidence_span": "Polyalphaolefin (PAO) heat-transfer fluid conforming to MIL-PRF-87252"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-11", "question_type": "factual",
    "question_text": "What is the sustained coolant flow rate through the liquid cooling loop?",
    "ground_truth": "3.2 liters per minute (L/min)",
    "evidence_span": "3.2 liters per minute (L/min)"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-12", "question_type": "factual",
    "question_text": "What is the nominal loop pressure for the active liquid cooling system?",
    "ground_truth": "45.0 psi",
    "evidence_span": "nominal loop pressure of 45.0 psi"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-13", "question_type": "factual",
    "question_text": "What is the standardized maximum cold-plate thermal resistance per computing node?",
    "ground_truth": "0.085 deg C/W",
    "evidence_span": "maximum 0.085 deg C/W per computing node"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-14", "question_type": "factual",
    "question_text": "What overall vibration power spectral density must the computer withstand under MIL-STD-810H?",
    "ground_truth": "7.7 g_rms across 20 Hz to 2,000 Hz",
    "evidence_span": "7.7 g_rms across 20 Hz to 2,000 Hz"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-15", "question_type": "factual",
    "question_text": "What shock pulse profile and duration along orthogonal axes can the system survive?",
    "ground_truth": "20g terminal-peak sawtooth shock pulses of 11 milliseconds duration",
    "evidence_span": "20g terminal-peak sawtooth shock pulses of 11 milliseconds duration"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-16", "question_type": "factual",
    "question_text": "What is the maximum operational barometric altitude specified for the FCC-900?",
    "ground_truth": "65,000 feet (19,812 meters)",
    "evidence_span": "65,000 feet (19,812 meters) above mean sea level"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-17", "question_type": "factual",
    "question_text": "At what temperature does Stage 2 autonomous throttling activate, and to what clock speed?",
    "ground_truth": "At 92.0 deg C, dynamically throttles processor clock frequency from 1.8 GHz down to 900 MHz",
    "evidence_span": "92.0 deg C, the power management controller dynamically throttles processor clock frequency from 1.8 GHz down to 900 MHz"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-18", "question_type": "factual",
    "question_text": "What is the Mean Time Between Failures (MTBF) reliability metric established for the system?",
    "ground_truth": "150,000 flight hours",
    "evidence_span": "150,000 flight hours"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-ADV-01", "question_type": "adversarial",
    "question_text": "What is the thickness in millimeters of the head-up display (HUD) anti-reflective cockpit glass?",
    "ground_truth": "The document does not mention head-up display (HUD) glass thickness.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-ADV-02", "question_type": "adversarial",
    "question_text": "What battery chemistry and kilowatt-hour capacity are used in the main flight emergency battery?",
    "ground_truth": "The document does not mention flight emergency battery chemistry or kilowatt-hour capacity.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-ADV-03", "question_type": "adversarial",
    "question_text": "What is the flash point in degrees Celsius of the aviation Jet-A kerosene fuel?",
    "ground_truth": "The document does not mention aviation fuel flash points or Jet-A specifications.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-ADV-04", "question_type": "adversarial",
    "question_text": "What is the maximum continuous oxygen delivery flow rate for the pilot's emergency breathing mask?",
    "ground_truth": "The document does not mention pilot oxygen systems or breathing mask flow rates.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-ADV-05", "question_type": "adversarial",
    "question_text": "Which satellite communication constellation provides Ka-band broadband connectivity for passenger Wi-Fi?",
    "ground_truth": "The document does not mention satellite broadband connectivity or passenger Wi-Fi.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-ADV-06", "question_type": "adversarial",
    "question_text": "What radar frequency band in gigahertz is emitted by the forward weather radar antenna?",
    "ground_truth": "The document does not mention forward weather radar frequencies.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc4, "question_id": "Q-AERO-ADV-07", "question_type": "adversarial",
    "question_text": "How many hydraulic actuators control the rudder mechanical deflection angle?",
    "ground_truth": "The document does not mention rudder hydraulic actuator counts.",
    "evidence_span": "None (unanswerable)"
})


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT 5: clinical_oncology_biomarker_protocol.pdf (25 items: 18 fact, 7 adv)
# ══════════════════════════════════════════════════════════════════════════════
doc5 = "clinical_oncology_biomarker_protocol.pdf"

DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-01", "question_type": "factual",
    "question_text": "What is the protocol identifier code for the Phase III oncology study?",
    "ground_truth": "ONCO-TRIAL-704",
    "evidence_span": "ONCO-TRIAL-704"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-02", "question_type": "factual",
    "question_text": "What is the investigational product name and developmental code in the trial?",
    "ground_truth": "Zanabrutinib-Pegol (ZP-408)",
    "evidence_span": "Zanabrutinib-Pegol (ZP-408)"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-03", "question_type": "factual",
    "question_text": "What cancer indication and biomarker target are evaluated in the study?",
    "ground_truth": "Claudin-18.2-positive advanced gastric or gastroesophageal junction adenocarcinoma",
    "evidence_span": "Claudin-18.2-positive advanced gastric or gastroesophageal junction adenocarcinoma"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-04", "question_type": "factual",
    "question_text": "What is the primary objective and evaluation timeframe of the trial?",
    "ground_truth": "evaluate Overall Survival (OS) at Month 24",
    "evidence_span": "evaluate Overall Survival (OS) at Month 24"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-05", "question_type": "factual",
    "question_text": "What criteria and imaging frequency are specified for evaluating Objective Response Rate (ORR)?",
    "ground_truth": "RECIST version 1.1 criteria every 6 weeks",
    "evidence_span": "RECIST version 1.1 criteria every 6 weeks"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-06", "question_type": "factual",
    "question_text": "How many total adult subjects and clinical cancer centers are participating in the study?",
    "ground_truth": "720 adult subjects across 35 international clinical investigative cancer centers",
    "evidence_span": "720 adult subjects across 35 international clinical investigative cancer centers"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-07", "question_type": "factual",
    "question_text": "What standardized dosage of Zanabrutinib-Pegol is administered in Arm 1?",
    "ground_truth": "600 mg/m^2",
    "evidence_span": "standardized dose of 600 mg/m^2"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-08", "question_type": "factual",
    "question_text": "What is the scheduled infusion duration and cycle frequency (Q3W) for the investigational drug?",
    "ground_truth": "infusion over 90 minutes on Day 1 of each 21-day cycle (Q3W)",
    "evidence_span": "infusion over 90 minutes on Day 1 of each 21-day cycle (Q3W)"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-09", "question_type": "factual",
    "question_text": "What mandatory premedication drugs and dosages must be given prior to infusion?",
    "ground_truth": "oral dexamethasone 20 mg and intravenous diphenhydramine 50 mg",
    "evidence_span": "oral dexamethasone 20 mg and intravenous diphenhydramine 50 mg"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-10", "question_type": "factual",
    "question_text": "How many minutes prior to the start of infusion must premedication be administered?",
    "ground_truth": "exactly 30 minutes prior to the start",
    "evidence_span": "exactly 30 minutes prior to the start of each Zanabrutinib-Pegol infusion"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-11", "question_type": "factual",
    "question_text": "What infusion rate adjustment is mandated if Grade 1 or 2 infusion reactions occur?",
    "ground_truth": "infusion speed is reduced by 50%",
    "evidence_span": "infusion speed is reduced by 50%"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-12", "question_type": "factual",
    "question_text": "What age range is eligible for enrollment in the oncology trial?",
    "ground_truth": "aged 18 to 80 years at screening",
    "evidence_span": "aged 18 to 80 years at screening"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-13", "question_type": "factual",
    "question_text": "What minimum percentage of tumor cells must express Claudin-18.2 for trial inclusion?",
    "ground_truth": "greater than or equal to 70% of tumor cells showing 2+ or 3+ staining intensity",
    "evidence_span": "greater than or equal to 70% of tumor cells showing 2+ or 3+ staining intensity by central IHC"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-14", "question_type": "factual",
    "question_text": "What is the baseline Absolute Neutrophil Count (ANC) cutoff required for inclusion?",
    "ground_truth": "ANC >= 1,500 cells/uL (1.5 x 10^9 /L)",
    "evidence_span": "Absolute Neutrophil Count (ANC) >= 1,500 cells/uL (1.5 x 10^9 /L)"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-15", "question_type": "factual",
    "question_text": "What screening QTc interval cutoff on 12-lead ECG results in patient exclusion?",
    "ground_truth": "QTcB exceeding 470 milliseconds",
    "evidence_span": "Corrected QT interval (QTcB) exceeding 470 milliseconds on screening 12-lead ECG"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-16", "question_type": "factual",
    "question_text": "How is Dose-Limiting Toxicity (DLT) defined regarding Grade 4 neutropenia?",
    "ground_truth": "Grade 4 neutropenia lasting longer than 7 consecutive days",
    "evidence_span": "Grade 4 neutropenia lasting longer than 7 consecutive days"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-17", "question_type": "factual",
    "question_text": "What fever and neutrophil thresholds define febrile neutropenia as a DLT?",
    "ground_truth": "oral temperature >= 38.3 deg C with ANC < 500 cells/uL",
    "evidence_span": "oral temperature >= 38.3 deg C with ANC < 500 cells/uL"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-18", "question_type": "factual",
    "question_text": "At what temperature must serum pharmacokinetic aliquots be cryopreserved?",
    "ground_truth": "-80.0 deg C in vapor-phase liquid nitrogen",
    "evidence_span": "-80.0 deg C in vapor-phase liquid nitrogen"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-ADV-01", "question_type": "adversarial",
    "question_text": "What out-of-pocket prescription co-pay is billed to enrolled patients per treatment cycle?",
    "ground_truth": "The document does not mention patient co-pays or prescription billing costs.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-ADV-02", "question_type": "adversarial",
    "question_text": "What was the highest non-lethal dose in mg/kg observed in cynomolgus monkey toxicology studies?",
    "ground_truth": "The document does not mention non-human animal toxicology studies or monkey dosing.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-ADV-03", "question_type": "adversarial",
    "question_text": "What dosage of Zanabrutinib-Pegol is approved for pediatric patients with neuroblastoma?",
    "ground_truth": "The document does not mention pediatric dosing or neuroblastoma; enrollment is restricted to adults aged 18 to 80.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-ADV-04", "question_type": "adversarial",
    "question_text": "What distinctive color dye is added to the intravenous infusion bag for light-sensitive protection?",
    "ground_truth": "The document does not mention infusion bag dyes or light-sensitive coloring.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-ADV-05", "question_type": "adversarial",
    "question_text": "Which manufacturer's surgical robotic system is approved for laparoscopic biopsy resection?",
    "ground_truth": "The document does not mention surgical robotics or specific biopsy resection equipment.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-ADV-06", "question_type": "adversarial",
    "question_text": "What percentage of trial participants demonstrated complete anti-drug antibody neutralization at Week 52?",
    "ground_truth": "The document does not mention anti-drug antibody rates or Week 52 immunogenicity.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc5, "question_id": "Q-ONCO-ADV-07", "question_type": "adversarial",
    "question_text": "What dietary restrictions regarding grapefruit juice consumption are enforced during Cycle 1?",
    "ground_truth": "The document does not mention dietary restrictions regarding grapefruit juice.",
    "evidence_span": "None (unanswerable)"
})


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT 6: cloud_kubernetes_sre_incident_runbook.pdf (25 items: 18 fact, 7 adv)
# ══════════════════════════════════════════════════════════════════════════════
doc6 = "cloud_kubernetes_sre_incident_runbook.pdf"

DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-01", "question_type": "factual",
    "question_text": "What is the document identifier for the Kubernetes SRE incident runbook?",
    "ground_truth": "SRE-K8S-RUNBOOK-V5",
    "evidence_span": "SRE-K8S-RUNBOOK-V5"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-02", "question_type": "factual",
    "question_text": "Which Kubernetes version and CNI networking are deployed on Google Kubernetes Engine?",
    "ground_truth": "GKE version 1.30 utilizing Calico CNI networking",
    "evidence_span": "Google Kubernetes Engine (GKE) version 1.30 utilizing Calico CNI networking"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-03", "question_type": "factual",
    "question_text": "What monthly availability target is mandated for tier-0 transaction APIs?",
    "ground_truth": "99.95% monthly availability target",
    "evidence_span": "99.95% monthly availability target"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-04", "question_type": "factual",
    "question_text": "What is the maximum allowed monthly downtime error budget in minutes?",
    "ground_truth": "exactly 21.6 minutes",
    "evidence_span": "exactly 21.6 minutes"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-05", "question_type": "factual",
    "question_text": "What collection cadence is standardized for Prometheus metric scraping?",
    "ground_truth": "15 seconds",
    "evidence_span": "standardized collection cadence of 15 seconds"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-06", "question_type": "factual",
    "question_text": "Over what moving average window do automated alerting rules evaluate conditions?",
    "ground_truth": "5-minute moving average window",
    "evidence_span": "5-minute moving average window"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-07", "question_type": "factual",
    "question_text": "At what CPU utilization percentage does the Horizontal Pod Autoscaler (HPA) trigger scale-out?",
    "ground_truth": "exceeds 75.0%",
    "evidence_span": "exceeds 75.0%"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-08", "question_type": "factual",
    "question_text": "At what memory threshold does HPA autoscaling trigger pod expansion?",
    "ground_truth": "exceeds 80.0% of configured resource limits",
    "evidence_span": "exceeds 80.0% of configured resource limits"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-09", "question_type": "factual",
    "question_text": "What are the minimum and maximum replica limits for tier-0 Kubernetes deployments?",
    "ground_truth": "minimum of 6 pod replicas and maximum cap of 60 pod replicas",
    "evidence_span": "minimum of 6 pod replicas and a maximum cap of 60 pod replicas"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-10", "question_type": "factual",
    "question_text": "Across how many availability zones must tier-0 pod replicas be distributed?",
    "ground_truth": "3 independent availability zones (2 pods per zone minimum)",
    "evidence_span": "3 independent availability zones (2 pods per zone minimum)"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-11", "question_type": "factual",
    "question_text": "What minAvailable percentage is enforced by the PodDisruptionBudget (PDB)?",
    "ground_truth": "minAvailable of 80%",
    "evidence_span": "minAvailable of 80%"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-12", "question_type": "factual",
    "question_text": "What is the Incident Commander acknowledgement SLA for a Severity 1 incident?",
    "ground_truth": "Within 5 minutes of automated alert firing",
    "evidence_span": "Within 5 minutes of automated alert firing"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-13", "question_type": "factual",
    "question_text": "Within how many minutes must a war room coordination bridge be established for P1 outages?",
    "ground_truth": "Within 10 minutes",
    "evidence_span": "Within 10 minutes"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-14", "question_type": "factual",
    "question_text": "How frequently must executive status broadcasts be transmitted during a P1 critical outage?",
    "ground_truth": "every 30 minutes until resolution",
    "evidence_span": "every 30 minutes until resolution"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-15", "question_type": "factual",
    "question_text": "What is the publication deadline for a draft Root Cause Analysis (RCA) post-mortem?",
    "ground_truth": "Within 72 hours of incident mitigation",
    "evidence_span": "Within 72 hours of incident mitigation"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-16", "question_type": "factual",
    "question_text": "How often are automated etcd control plane snapshots executed?",
    "ground_truth": "automatically every 6 hours",
    "evidence_span": "automatically every 6 hours"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-17", "question_type": "factual",
    "question_text": "For how many calendar days are etcd backup snapshots retained in GCS?",
    "ground_truth": "14 calendar days",
    "evidence_span": "14 calendar days in Google Cloud Storage"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-18", "question_type": "factual",
    "question_text": "What are the Recovery Time Objective (RTO) and Recovery Point Objective (RPO) for warm standby failover?",
    "ground_truth": "RTO under 15 minutes and RPO under 60 seconds",
    "evidence_span": "Recovery Time Objective (RTO) of under 15 minutes and Recovery Point Objective (RPO) of under 60 seconds"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-ADV-01", "question_type": "adversarial",
    "question_text": "What is the per-gigabyte pricing charged for AWS CloudWatch log metric ingestion?",
    "ground_truth": "The document does not mention AWS CloudWatch or per-gigabyte log pricing.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-ADV-02", "question_type": "adversarial",
    "question_text": "What is the encrypted master root password for the central production MySQL database?",
    "ground_truth": "The document does not mention MySQL root passwords or database credentials.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-ADV-03", "question_type": "adversarial",
    "question_text": "Which Terraform Enterprise plan license tier is subscribed for infrastructure provisioning?",
    "ground_truth": "The document does not mention Terraform licensing or enterprise subscription tiers.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-ADV-04", "question_type": "adversarial",
    "question_text": "Which third-party private security agency provides armed physical security guards at the data center?",
    "ground_truth": "The document does not mention physical security guards or data center security vendors.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-ADV-05", "question_type": "adversarial",
    "question_text": "Which brand and category of Cat6a Ethernet patch cables are installed in top-of-rack switches?",
    "ground_truth": "The document does not mention Ethernet cable brands or physical networking hardware specifications.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-ADV-06", "question_type": "adversarial",
    "question_text": "What is the maximum allowed payload size in megabytes for RabbitMQ message broker queues?",
    "ground_truth": "The document does not mention RabbitMQ message queues or payload size limits.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc6, "question_id": "Q-K8S-ADV-07", "question_type": "adversarial",
    "question_text": "Who is the on-call secondary escalation engineer for front-end Angular CSS rendering bugs?",
    "ground_truth": "The document does not mention front-end engineering on-call rotations or CSS rendering.",
    "evidence_span": "None (unanswerable)"
})


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT 7: supply_chain_cold_storage_logistics.pdf (25 items: 18 fact, 7 adv)
# ══════════════════════════════════════════════════════════════════════════════
doc7 = "supply_chain_cold_storage_logistics.pdf"

DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-01", "question_type": "factual",
    "question_text": "What is the specification standard code for the cold chain logistics specification?",
    "ground_truth": "LOG-COLD-CHAIN-502",
    "evidence_span": "LOG-COLD-CHAIN-502"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-02", "question_type": "factual",
    "question_text": "Which issuing body authored the cold chain compliance specification?",
    "ground_truth": "Global BioPharma Logistics Compliance Council",
    "evidence_span": "Global BioPharma Logistics Compliance Council"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-03", "question_type": "factual",
    "question_text": "What is the operational setpoint range for Ultra-Low Temperature (ULT) transport?",
    "ground_truth": "-80.0 deg C to -60.0 deg C",
    "evidence_span": "-80.0 deg C to -60.0 deg C"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-04", "question_type": "factual",
    "question_text": "What packaging container type is utilized for active dry-ice ULT transport?",
    "ground_truth": "Vacuum Insulated Panel (VIP) active dry-ice containers",
    "evidence_span": "Vacuum Insulated Panel (VIP) active dry-ice containers"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-05", "question_type": "factual",
    "question_text": "What is the operational setpoint range for Standard Refrigerated transport?",
    "ground_truth": "+2.0 deg C to +8.0 deg C",
    "evidence_span": "+2.0 deg C to +8.0 deg C"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-06", "question_type": "factual",
    "question_text": "What is the controlled setpoint range for Ambient transport?",
    "ground_truth": "+15.0 deg C to +25.0 deg C",
    "evidence_span": "+15.0 deg C to +25.0 deg C"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-07", "question_type": "factual",
    "question_text": "What environmental IoT data logger model is mandated for shipments?",
    "ground_truth": "SensiTrack-4G",
    "evidence_span": "SensiTrack-4G environmental IoT data loggers"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-08", "question_type": "factual",
    "question_text": "How frequently are internal temperature and pressure logged by the sensor?",
    "ground_truth": "once every 60 seconds",
    "evidence_span": "once every 60 seconds"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-09", "question_type": "factual",
    "question_text": "What is the cellular telemetry transmission cadence over NB-IoT or LTE-M?",
    "ground_truth": "every 15 minutes",
    "evidence_span": "every 15 minutes"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-10", "question_type": "factual",
    "question_text": "What is the calibrated sensor measurement accuracy required across -90.0 deg C to +30.0 deg C?",
    "ground_truth": "+/-0.3 deg C",
    "evidence_span": "+/-0.3 deg C"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-11", "question_type": "factual",
    "question_text": "What minimum battery endurance is required for the logger at -80.0 deg C?",
    "ground_truth": "minimum of 120 hours of continuous operation",
    "evidence_span": "minimum of 120 hours of continuous operation at -80.0 deg C"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-12", "question_type": "factual",
    "question_text": "What is the standardized dry ice payload capacity for transport shippers?",
    "ground_truth": "42.0 kilograms",
    "evidence_span": "42.0 kilograms"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-13", "question_type": "factual",
    "question_text": "What is the maximum allowable dry ice sublimation rate per hour at 25.0 deg C ambient?",
    "ground_truth": "0.45 kilograms per hour",
    "evidence_span": "0.45 kilograms per hour"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-14", "question_type": "factual",
    "question_text": "What peak acceleration event recorded by 3-axis accelerometers triggers an automatic inspection?",
    "ground_truth": "exceeding 4.5g",
    "evidence_span": "exceeding 4.5g"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-15", "question_type": "factual",
    "question_text": "What temperature reading and duration define a critical temperature excursion alert?",
    "ground_truth": "rising above -55.0 deg C for longer than 10 consecutive minutes",
    "evidence_span": "rising above -55.0 deg C for longer than 10 consecutive minutes"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-16", "question_type": "factual",
    "question_text": "What is the quarantine transfer SLA into a mechanical cold vault upon excursion alert?",
    "ground_truth": "within 30 minutes of excursion alert notification",
    "evidence_span": "within 30 minutes of excursion alert notification"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-17", "question_type": "factual",
    "question_text": "Within how many hours must a GMP Deviation Investigation Report be submitted after quarantine?",
    "ground_truth": "within 4 business hours of shipment quarantine",
    "evidence_span": "within 4 business hours of shipment quarantine"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-18", "question_type": "factual",
    "question_text": "How frequently must shippers undergo 3-point thermal re-validation mapping?",
    "ground_truth": "every 6 months",
    "evidence_span": "every 6 months"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-ADV-01", "question_type": "adversarial",
    "question_text": "What is the commercial driver license (CDL) number of the primary freight transport driver?",
    "ground_truth": "The document does not mention driver licensing or personnel CDL numbers.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-ADV-02", "question_type": "adversarial",
    "question_text": "What is the wholesale fuel cost per gallon for refrigerated diesel delivery trucks?",
    "ground_truth": "The document does not mention diesel fuel costs or truck operating expenses.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-ADV-03", "question_type": "adversarial",
    "question_text": "What is the peak power output in watts of the distribution warehouse rooftop solar panels?",
    "ground_truth": "The document does not mention warehouse solar panel wattage or electrical infrastructure.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-ADV-04", "question_type": "adversarial",
    "question_text": "Which tire brand and tread pattern are approved for electric warehouse forklifts?",
    "ground_truth": "The document does not mention forklift tire brands or warehouse machinery specifications.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-ADV-05", "question_type": "adversarial",
    "question_text": "What is the corporate tax identification number of the cardboard packaging box vendor?",
    "ground_truth": "The document does not mention cardboard packaging vendor tax identification numbers.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-ADV-06", "question_type": "adversarial",
    "question_text": "What is the maximum allowed weight in pounds for wooden transport pallets?",
    "ground_truth": "The document does not mention wooden pallet weights or specifications.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc7, "question_id": "Q-LOG-ADV-07", "question_type": "adversarial",
    "question_text": "Which customs broker handles clearance declarations at Frankfurt International Airport?",
    "ground_truth": "The document does not mention customs brokers or specific airport clearance agencies.",
    "evidence_span": "None (unanswerable)"
})


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT 8: financial_audit_internal_controls_memo.pdf (25 items: 18 fact, 7 adv)
# ══════════════════════════════════════════════════════════════════════════════
doc8 = "financial_audit_internal_controls_memo.pdf"

DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-01", "question_type": "factual",
    "question_text": "What is the memorandum identifier code for the financial audit internal controls memo?",
    "ground_truth": "AUD-SOX-404-2026",
    "evidence_span": "AUD-SOX-404-2026"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-02", "question_type": "factual",
    "question_text": "Under which section of the Sarbanes-Oxley Act (SOX) are internal controls evaluated?",
    "ground_truth": "Section 404 of the Sarbanes-Oxley Act (SOX)",
    "evidence_span": "Section 404 of the Sarbanes-Oxley Act (SOX)"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-03", "question_type": "factual",
    "question_text": "What dollar value is established as Planning Materiality for the fiscal year 2026 audit?",
    "ground_truth": "$12,500,000 USD",
    "evidence_span": "$12,500,000 USD"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-04", "question_type": "factual",
    "question_text": "What percentage of normalized pre-tax operating income was used to calculate planning materiality?",
    "ground_truth": "exactly 5.0% of normalized pre-tax operating income",
    "evidence_span": "exactly 5.0% of normalized pre-tax operating income"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-05", "question_type": "factual",
    "question_text": "What percentage and dollar value are established for Performance Materiality?",
    "ground_truth": "75.0% of planning materiality, amounting to $9,375,000 USD",
    "evidence_span": "75.0% of planning materiality, amounting to $9,375,000 USD"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-06", "question_type": "factual",
    "question_text": "What dollar threshold defines clearly trivial misstatements (de minimis) that are not accumulated?",
    "ground_truth": "below $625,000 USD (5.0% of planning materiality)",
    "evidence_span": "below $625,000 USD (5.0% of planning materiality)"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-07", "question_type": "factual",
    "question_text": "What monetary threshold triggers mandatory dual authorization for manual non-standard journal entries?",
    "ground_truth": "exceeding $500,000 USD",
    "evidence_span": "exceeding $500,000 USD"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-08", "question_type": "factual",
    "question_text": "Which two corporate officers must sign off on manual journal entries exceeding $500,000 USD?",
    "ground_truth": "Corporate Controller and the Chief Accounting Officer (CAO)",
    "evidence_span": "Corporate Controller and the Chief Accounting Officer (CAO)"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-09", "question_type": "factual",
    "question_text": "What threshold of automated recurring journal entries requires post-posting review by Internal Audit?",
    "ground_truth": "exceeding $2,500,000 USD",
    "evidence_span": "exceeding $2,500,000 USD"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-10", "question_type": "factual",
    "question_text": "Within how many business days of month-end close must recurring entries over $2,500,000 be reviewed?",
    "ground_truth": "within 5 business days of financial month-end close",
    "evidence_span": "within 5 business days of financial month-end close"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-11", "question_type": "factual",
    "question_text": "How frequently are high-privilege posting privileges re-certified in SAP S/4HANA?",
    "ground_truth": "re-certified quarterly",
    "evidence_span": "re-certified quarterly"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-12", "question_type": "factual",
    "question_text": "Within how many hours must ERP access privileges be revoked for terminated personnel?",
    "ground_truth": "within 24 hours",
    "evidence_span": "within 24 hours"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-13", "question_type": "factual",
    "question_text": "What is the maximum purchase order approval limit delegated to Department Managers (Tier 1)?",
    "ground_truth": "up to $25,000 USD",
    "evidence_span": "up to $25,000 USD"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-14", "question_type": "factual",
    "question_text": "What approval authority threshold is designated for Vice Presidents (VPs) under Tier 2?",
    "ground_truth": "between $25,001 and $100,000 USD",
    "evidence_span": "between $25,001 and $100,000 USD"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-15", "question_type": "factual",
    "question_text": "Whose joint sign-off is required for capital expenditures or contracts exceeding $500,000 USD (Tier 4)?",
    "ground_truth": "Enterprise Chief Executive Officer (CEO) and Enterprise CFO joint sign-off",
    "evidence_span": "Enterprise Chief Executive Officer (CEO) and Enterprise CFO joint sign-off"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-16", "question_type": "factual",
    "question_text": "What purchase cost and economic life criteria are required to capitalize fixed tangible assets?",
    "ground_truth": "purchase cost greater than or equal to $5,000 USD and an estimated useful economic life of at least 3 years",
    "evidence_span": "purchase cost greater than or equal to $5,000 USD and an estimated useful economic life of at least 3 years"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-17", "question_type": "factual",
    "question_text": "What depreciation method is mandated for capitalized tangible fixed assets?",
    "ground_truth": "straight-line method",
    "evidence_span": "straight-line method"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-18", "question_type": "factual",
    "question_text": "What percentage variance or gross dollar discrepancy in warehouse inventory triggers formal investigation?",
    "ground_truth": "exceeding 1.5% of total SKU book value or an absolute gross dollar discrepancy exceeding $50,000 USD",
    "evidence_span": "exceeding 1.5% of total SKU book value or an absolute gross dollar discrepancy exceeding $50,000 USD"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-ADV-01", "question_type": "adversarial",
    "question_text": "What was the grant strike price per share for the Chief Executive Officer's annual stock option awards?",
    "ground_truth": "The document does not mention executive stock option strike prices or equity grants.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-ADV-02", "question_type": "adversarial",
    "question_text": "Which external catering vendor provides weekday lunch service in the corporate headquarters cafeteria?",
    "ground_truth": "The document does not mention cafeteria catering vendors or lunch services.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-ADV-03", "question_type": "adversarial",
    "question_text": "What hourly billing rate is charged by the external audit firm for first-year staff associates?",
    "ground_truth": "The document does not mention audit firm billing rates or associate fees.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-ADV-04", "question_type": "adversarial",
    "question_text": "What is the physical street address of the registered corporate agent in Wilmington, Delaware?",
    "ground_truth": "The document does not mention Delaware registered agent street addresses.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-ADV-05", "question_type": "adversarial",
    "question_text": "What percentage matching contribution does the enterprise provide for employee 401(k) retirement plans?",
    "ground_truth": "The document does not mention 401(k) matching percentages or retirement benefit plans.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-ADV-06", "question_type": "adversarial",
    "question_text": "What is the annual software licensing fee paid for Microsoft Office 365 enterprise seats?",
    "ground_truth": "The document does not mention Microsoft Office licensing costs or software seat fees.",
    "evidence_span": "None (unanswerable)"
})
DATASET.append({
    "pdf_id": doc8, "question_id": "Q-AUD-ADV-07", "question_type": "adversarial",
    "question_text": "Which commercial bank underwrites the corporate revolving credit facility interest rate spread?",
    "ground_truth": "The document does not mention revolving credit facilities or underwriting commercial banks.",
    "evidence_span": "None (unanswerable)"
})

# ══════════════════════════════════════════════════════════════════════════════
# VERIFICATION SUITE
# ══════════════════════════════════════════════════════════════════════════════

print(f"Total compiled questions: {len(DATASET)}")
assert len(DATASET) == 200, f"Expected 200 questions, got {len(DATASET)}"

# Check unique question IDs
q_ids = [item["question_id"] for item in DATASET]
assert len(q_ids) == len(set(q_ids)), f"Duplicate question IDs detected! Unique: {len(set(q_ids))}"

# Verify every factual evidence_span exists verbatim in document text
missing_spans = []
for item in DATASET:
    if item["question_type"] == "factual":
        doc_text = DOC_TEXTS[item["pdf_id"]].lower()
        span_clean = " ".join(item["evidence_span"].split()).lower()
        if span_clean not in doc_text:
            missing_spans.append((item["pdf_id"], item["question_id"], item["evidence_span"]))

if missing_spans:
    print(f"ERROR: {len(missing_spans)} factual evidence spans not found in documents:")
    for doc, qid, span in missing_spans:
        print(f"  - [{doc}] {qid}: '{span}'")
    raise ValueError("Factual evidence span verification failed!")
else:
    print("SUCCESS: 100% of factual evidence spans verified verbatim in document texts!")

# Verify all adversarial evidence_spans are set properly
for item in DATASET:
    if item["question_type"] == "adversarial":
        assert item["evidence_span"] == "None (unanswerable)", f"Adversarial span invalid: {item}"

# Write to CSV
fieldnames = ["pdf_id", "question_id", "question_text", "ground_truth", "question_type", "evidence_span"]
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in DATASET:
        writer.writerow(row)

print(f"Successfully generated {OUTPUT_CSV.name} with {len(DATASET)} items.")
