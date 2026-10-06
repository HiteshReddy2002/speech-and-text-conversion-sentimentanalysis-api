import fitz
from pathlib import Path

EVAL_DATA_DIR = Path(r"C:\Users\hites\.gemini\antigravity-ide\scratch\speech-and-text-conversion-sentimentanalysis-api\eval\data")
EVAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── PDF 4: Aerospace Avionics Thermal & Environmental Spec ─────────────────────
doc4 = fitz.open()

p4_1_text = """AEROSPACE AVIONICS THERMAL MANAGEMENT & ENVIRONMENTAL SPECIFICATION
Document ID: AERO-SPEC-FCC900-V4
Classification: Restricted Aerospace Technical Standard
Authority: Flight Avionics Systems Directorate
Effective Date: April 12, 2026

1. Scope and System Overview
This specification defines the thermal envelope, mechanical vibration tolerances, and emergency
fail-safe behavior for the FCC-900 Primary Flight Control Computer. The FCC-900 operates within
the unpressurized forward avionics bay across commercial and tactical aerospace flight envelopes.
The computing core features quad-redundant lockstep processor modules communicating over a
dual-redundant CAN-FD serial telemetry bus operating at a standardized bitrate of 5.0 Mbps with
a cyclic telemetry broadcast interval of exactly 20 milliseconds.

2. Thermal Operational Limits and Coolant Architecture
- Operational ambient temperature envelope: -40.0 deg C to +85.0 deg C under continuous flight conditions.
- Non-operational storage survival range: -55.0 deg C to +105.0 deg C.
- Maximum permitted silicon semiconductor junction temperature: 105.0 deg C.
- Primary active cooling mechanism: Closed-loop liquid cooling using dielectric Polyalphaolefin (PAO)
  heat-transfer fluid conforming to MIL-PRF-87252.
- Sustained coolant flow rate: 3.2 liters per minute (L/min) at a nominal loop pressure of 45.0 psi.
- Cold-plate thermal resistance: Standardized at maximum 0.085 deg C/W per computing node.
"""

p4_1 = doc4.new_page()
p4_1.insert_textbox(fitz.Rect(50, 50, 550, 750), p4_1_text, fontsize=11, fontname="helv")

p4_2_text = """3. Environmental Shock, Vibration, and Altitude Specifications
- Mechanical random vibration tolerance: Conforms to MIL-STD-810H, Method 514.8, Category 24,
  withstanding an overall vibration power spectral density of 7.7 g_rms across 20 Hz to 2,000 Hz.
- Shock tolerance: Withstands 20g terminal-peak sawtooth shock pulses of 11 milliseconds duration
  along each of the three orthogonal axes.
- Maximum operational barometric altitude: 65,000 feet (19,812 meters) above mean sea level.

4. Thermal Degradation and Fail-Safe Trip Thresholds
- Stage 1 Thermal Warning: Silicon core temperature reaching 88.0 deg C asserts an advisory telemetry flag.
- Stage 2 Autonomous Throttling: If silicon junction temperature reaches 92.0 deg C, the power management
  controller dynamically throttles processor clock frequency from 1.8 GHz down to 900 MHz.
- Stage 3 Emergency Thermal Trip: If internal sensor temperature exceeds 115.0 deg C, hardware thermal
  cutoff relays disconnect non-essential payload power within 150 milliseconds to prevent battery runaways.
- System Reliability Metric: Mean Time Between Failures (MTBF) is established at 150,000 flight hours,
  verified via MIL-HDBK-217F reliability prediction modeling.
"""

p4_2 = doc4.new_page()
p4_2.insert_textbox(fitz.Rect(50, 50, 550, 750), p4_2_text, fontsize=11, fontname="helv")

pdf4_path = EVAL_DATA_DIR / "aerospace_avionics_thermal_spec.pdf"
doc4.save(str(pdf4_path))
doc4.close()
print(f"Generated {pdf4_path.name}")


# ── PDF 5: Clinical Oncology Biomarker Protocol ──────────────────────────────
doc5 = fitz.open()

p5_1_text = """CLINICAL TRIAL PROTOCOL: TARGETED IMMUNOTHERAPY IN GASTRIC ONCOLOGY
Protocol Identifier: ONCO-TRIAL-704
Study Phase: Phase III Multicenter Double-Blind Randomized Study
Investigational Product: Zanabrutinib-Pegol (ZP-408)
Sponsor: Global Oncology Therapeutics Research Group
Document Version: 3.2 | Release Date: March 20, 2026

1. Clinical Objectives and Study Design
The primary objective of this trial is to evaluate Overall Survival (OS) at Month 24 in adult subjects
with Claudin-18.2-positive advanced gastric or gastroesophageal junction adenocarcinoma.
The key secondary endpoint is Objective Response Rate (ORR) assessed by blinded independent central
review according to RECIST version 1.1 criteria every 6 weeks.
The trial will enroll 720 adult subjects across 35 international clinical investigative cancer centers.
Randomization is allocated 1:1 between Active Treatment (Arm 1) and Control (Arm 2).

2. Investigational Dosing Regimen and Premedication
- Arm 1 (Investigational): Zanabrutinib-Pegol administered at a standardized dose of 600 mg/m^2 via
  intravenous (IV) infusion over 90 minutes on Day 1 of each 21-day cycle (Q3W).
- Premedication: Mandatory oral dexamethasone 20 mg and intravenous diphenhydramine 50 mg administered
  exactly 30 minutes prior to the start of each Zanabrutinib-Pegol infusion to prevent hypersensitivity.
- Infusion rate reduction rule: If Grade 1 or 2 infusion reactions occur, infusion speed is reduced by 50%.
"""

p5_1 = doc5.new_page()
p5_1.insert_textbox(fitz.Rect(50, 50, 550, 750), p5_1_text, fontsize=11, fontname="helv")

p5_2_text = """3. Inclusion and Exclusion Biomarker Criteria
Inclusion Criteria:
- Male or female aged 18 to 80 years at screening.
- Histologically confirmed unresectable or metastatic adenocarcinoma with Claudin-18.2 expression in
  greater than or equal to 70% of tumor cells showing 2+ or 3+ staining intensity by central IHC.
- Baseline Absolute Neutrophil Count (ANC) >= 1,500 cells/uL (1.5 x 10^9 /L).
- Baseline Platelet count >= 100,000 cells/uL (100 x 10^9 /L).
- Serum total bilirubin <= 1.5 times upper limit of normal (ULN).

Exclusion Criteria:
- Active untreated central nervous system (CNS) brain metastases or leptomeningeal disease.
- Corrected QT interval (QTcB) exceeding 470 milliseconds on screening 12-lead ECG.
- Prior systemic exposure to Claudin-targeting antibody therapies within 12 months.

4. Toxicity Halting Criteria & Pharmacokinetics
- Dose-Limiting Toxicity (DLT): Defined as any confirmed Grade 4 neutropenia lasting longer than
  7 consecutive days, or febrile neutropenia (oral temperature >= 38.3 deg C with ANC < 500 cells/uL).
- Serial pharmacokinetic (PK) blood sampling schedule: Pre-infusion (0 hour), 2 hours, 6 hours,
  24 hours post-infusion, and Day 8, Day 15, and Day 21 of Cycle 1.
- Biospecimen storage: Serum PK aliquots must be cryopreserved at -80.0 deg C in vapor-phase liquid nitrogen.
"""

p5_2 = doc5.new_page()
p5_2.insert_textbox(fitz.Rect(50, 50, 550, 750), p5_2_text, fontsize=11, fontname="helv")

pdf5_path = EVAL_DATA_DIR / "clinical_oncology_biomarker_protocol.pdf"
doc5.save(str(pdf5_path))
doc5.close()
print(f"Generated {pdf5_path.name}")


# ── PDF 6: Kubernetes SRE Incident Runbook ────────────────────────────────────
doc6 = fitz.open()

p6_1_text = """KUBERNETES SITE RELIABILITY ENGINEERING (SRE) INCIDENT RUNBOOK
Document Identifier: SRE-K8S-RUNBOOK-V5
Classification: Enterprise Production Systems Standard
Author: Global Infrastructure & Reliability Engineering Team
Effective Date: January 10, 2026

1. Production Infrastructure Topology and SLO Definitions
Production clusters run on Google Kubernetes Engine (GKE) version 1.30 utilizing Calico CNI networking
and Cilium eBPF for cluster mesh routing.
Service Level Objectives (SLOs) mandate a 99.95% monthly availability target for tier-0 transaction APIs,
calculated over a rolling 30-day window. This permits a maximum monthly error budget of exactly
21.6 minutes of unmitigated service degradation before triggering an immediate deployment freeze.
Monitoring metrics are scraped by Prometheus at a standardized collection cadence of 15 seconds,
with automated alerting rules evaluating conditions across a 5-minute moving average window.

2. Autoscaling and Pod Disruption Thresholds
- Horizontal Pod Autoscaler (HPA) policies trigger pod scale-out when average pod CPU utilization
  exceeds 75.0% or resident memory consumption exceeds 80.0% of configured resource limits.
- Pod replica limits: Tier-0 services enforce a mandatory minimum of 6 pod replicas and a maximum
  cap of 60 pod replicas distributed across 3 independent availability zones (2 pods per zone minimum).
- PodDisruptionBudget (PDB): Mandatory configuration enforcing minAvailable of 80% during voluntary
  node maintenance drains or automated cluster node version upgrades.
"""

p6_1 = doc6.new_page()
p6_1.insert_textbox(fitz.Rect(50, 50, 550, 750), p6_1_text, fontsize=11, fontname="helv")

p6_2_text = """3. Severity Classification & Incident Response Escalation SLAs
- Severity 1 (P1 - Critical Outage): Full outage affecting payment processing.
  - Incident Commander (IC) acknowledgement SLA: Within 5 minutes of automated alert firing.
  - War room coordination bridge established: Within 10 minutes.
  - Executive status broadcast interval: Transmitted every 30 minutes until resolution.
  - Root Cause Analysis (RCA) post-mortem draft: Published within 72 hours of incident mitigation.
- Severity 2 (P2 - Major Degradation): Partial subsystem degradation with active fallback routing.
  - Engineering lead acknowledgement SLA: Within 15 minutes.
  - Executive update broadcast interval: Transmitted every 2 hours.

4. Disaster Recovery, etcd Snapshots, and Failover Targets
- Automated cluster state backup: etcd control plane snapshots are executed automatically every 6 hours.
- Backup snapshot retention policy: Snapshots are retained for 14 calendar days in Google Cloud Storage
  (GCS) with mandatory Object Retention Lock enabled to prevent ransomware alteration.
- Cross-region failover target: Secondary warm standby cluster operates in us-east4 (Northern Virginia),
  with a Recovery Time Objective (RTO) of under 15 minutes and Recovery Point Objective (RPO) of under 60 seconds.
"""

p6_2 = doc6.new_page()
p6_2.insert_textbox(fitz.Rect(50, 50, 550, 750), p6_2_text, fontsize=11, fontname="helv")

pdf6_path = EVAL_DATA_DIR / "cloud_kubernetes_sre_incident_runbook.pdf"
doc6.save(str(pdf6_path))
doc6.close()
print(f"Generated {pdf6_path.name}")


# ── PDF 7: Cold Storage Supply Chain & Sensor Spec ────────────────────────────
doc7 = fitz.open()

p7_1_text = """PHARMACEUTICAL COLD CHAIN LOGISTICS & SENSOR MONITORING SPECIFICATION
Specification Standard: LOG-COLD-CHAIN-502
Issuing Body: Global BioPharma Logistics Compliance Council
Effective Date: May 1, 2026 | Version: 2.4

1. Scope and Temperature Control Classifications
This specification sets technical requirements for the intercontinental transportation of temperature-
sensitive biologic therapies, mRNA vaccines, and viral vectors across multi-modal transit networks.
- Ultra-Low Temperature (ULT) Transport: Operating setpoint range from -80.0 deg C to -60.0 deg C.
  Packaging utilizes Vacuum Insulated Panel (VIP) active dry-ice containers.
- Standard Refrigerated Transport: Operating setpoint range from +2.0 deg C to +8.0 deg C.
- Ambient Controlled Transport: Operating setpoint range from +15.0 deg C to +25.0 deg C.

2. IoT Telemetry Loggers and Sampling Protocols
Shipments must be equipped with dual-redundant SensiTrack-4G environmental IoT data loggers.
- Temperature and ambient pressure logging frequency: Recorded internally once every 60 seconds.
- Cellular telemetry reporting cadence: Transmitted via NB-IoT or LTE-M networks every 15 minutes.
- Sensor measurement accuracy: Calibrated accuracy of +/-0.3 deg C across the operational range of
  -90.0 deg C to +30.0 deg C, re-certified within the past 12 months.
- Battery endurance: Logger internal lithium-thionyl chloride battery must guarantee a minimum of
  120 hours of continuous operation at -80.0 deg C ambient temperatures.
"""

p7_1 = doc7.new_page()
p7_1.insert_textbox(fitz.Rect(50, 50, 550, 750), p7_1_text, fontsize=11, fontname="helv")

p7_2_text = """3. Dry Ice Consumption and Physical Handling Limits
- Shippers are standardized with a dry ice payload capacity of 42.0 kilograms.
- Validated dry ice sublimation rate: Maximum allowable sublimation rate is 0.45 kilograms per hour
  under external ambient temperatures up to 25.0 deg C.
- Shock and vibration thresholds: Integrated 3-axis accelerometers monitor physical handling; peak
  acceleration events exceeding 4.5g trigger an automatic cargo inspection flag upon arrival.

4. Excursion Alarm Triggers and Quarantine Protocols
- Temperature Excursion Definition: Any recorded sensor reading rising above -55.0 deg C for longer
  than 10 consecutive minutes triggers an immediate critical excursion alert.
- Immediate Quarantine SLA: Warehouse operations must transfer affected containers into a validated
  mechanical cold storage vault within 30 minutes of excursion alert notification.
- Quality Deviation Filing: A formal GMP Deviation Investigation Report must be submitted to the
  Quality Assurance Directorate within 4 business hours of shipment quarantine.
- Temperature mapping re-validation: Shippers must undergo 3-point thermal re-validation every 6 months.
"""

p7_2 = doc7.new_page()
p7_2.insert_textbox(fitz.Rect(50, 50, 550, 750), p7_2_text, fontsize=11, fontname="helv")

pdf7_path = EVAL_DATA_DIR / "supply_chain_cold_storage_logistics.pdf"
doc7.save(str(pdf7_path))
doc7.close()
print(f"Generated {pdf7_path.name}")


# ── PDF 8: Financial Audit & Internal Controls Memo ───────────────────────────
doc8 = fitz.open()

p8_1_text = """ENTERPRISE FINANCIAL AUDIT & SOX INTERNAL CONTROLS MEMORANDUM
Memorandum ID: AUD-SOX-404-2026
Prepared By: Enterprise Internal Audit & Risk Advisory Committee
Audited Entity: Global Enterprise Operations Holding Corp
Fiscal Review Period: Fiscal Year 2026 | Date: February 18, 2026

1. Purpose and Audit Materiality Framework
This memorandum establishes internal financial control thresholds under Section 404 of the
Sarbanes-Oxley Act (SOX) and the COSO 2013 Internal Control-Integrated Framework.
- Planning Materiality: Established at $12,500,000 USD, calculated as exactly 5.0% of normalized
  pre-tax operating income.
- Performance Materiality: Established at 75.0% of planning materiality, amounting to $9,375,000 USD,
  used for scoping balance sheet testing and analytical substantive procedures.
- Clearly Trivial Reporting Threshold (De Minimis): Misstatements below $625,000 USD (5.0% of planning
  materiality) are deemed trivial and are not accumulated on the summary of audit differences.

2. Journal Entry Segregation of Duties and Dual Authorization
To prevent unauthorized adjustments to revenue and financial statement reserves:
- All manual non-standard journal entries exceeding $500,000 USD require mandatory dual-signature
  authorization from both the Corporate Controller and the Chief Accounting Officer (CAO).
- Automated recurring journal entries exceeding $2,500,000 USD require monthly post-posting review
  by the Internal Audit team within 5 business days of financial month-end close.
- ERP user access reviews: High-privilege posting privileges in SAP S/4HANA must be re-certified
  quarterly; access privileges for terminated personnel must be revoked within 24 hours.
"""

p8_1 = doc8.new_page()
p8_1.insert_textbox(fitz.Rect(50, 50, 550, 750), p8_1_text, fontsize=11, fontname="helv")

p8_2_text = """3. Procurement & Accounts Payable Approval Authority Matrix
Corporate delegations of financial authority enforce strict threshold boundaries:
- Tier 1: Department Managers may approve purchase orders up to $25,000 USD.
- Tier 2: Vice Presidents (VPs) may approve purchase orders between $25,001 and $100,000 USD.
- Tier 3: Business Unit Chief Financial Officers (CFOs) may approve between $100,001 and $500,000 USD.
- Tier 4: Enterprise Chief Executive Officer (CEO) and Enterprise CFO joint sign-off is required for
  any capital expenditure or procurement contract exceeding $500,000 USD.

4. Capitalization Policies and Physical Inventory Variance Controls
- Fixed Asset Capitalization Threshold: Tangible physical assets with an individual purchase cost
  greater than or equal to $5,000 USD and an estimated useful economic life of at least 3 years
  must be capitalized on the balance sheet and depreciated using the straight-line method.
- Physical Inventory Cycle Counts: Conducted on a continuous 90-day cycle across all regional warehouses.
- Inventory Investigation Trigger: Any warehouse cycle count displaying an aggregate inventory variance
  exceeding 1.5% of total SKU book value or an absolute gross dollar discrepancy exceeding $50,000 USD
  requires a mandatory physical recount and formal audit investigation within 48 business hours.
"""

p8_2 = doc8.new_page()
p8_2.insert_textbox(fitz.Rect(50, 50, 550, 750), p8_2_text, fontsize=11, fontname="helv")

pdf8_path = EVAL_DATA_DIR / "financial_audit_internal_controls_memo.pdf"
doc8.save(str(pdf8_path))
doc8.close()
print(f"Generated {pdf8_path.name}")
