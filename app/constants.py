GLOBAL_DISCLAIMER = (
    "LoanLens is an educational document-analysis tool, not a lender, regulator, lawyer, or financial adviser. "
    "Estimates depend on visible information and may be wrong when terms are missing, ambiguous, or misread. "
    "A flag is a potential concern, not a legal finding of fraud or illegality. "
    "Verify with the lender and seek qualified help before acting."
)

DLA_NOTICE_TEMPLATE = (
    "Directory result is based on a snapshot dated {date}. "
    "Listing indicates a reported association, not RBI approval, registration, or endorsement. "
    "A missing match may be caused by name differences or an outdated snapshot."
)

RULE_IDS = [
    "KFS-01",
    "COST-01",
    "FEE-01",
    "FLOW-01",
    "DATA-01",
    "GRV-01",
    "COOL-01",
    "DLA-01",
]

CRITICAL_FIELDS = [
    "lender_name",
    "sanctioned_amount",
    "net_disbursal",
    "tenure",
    "repayment_schedule",
]

CRITICAL_CONFIDENCE_THRESHOLD = 0.8
