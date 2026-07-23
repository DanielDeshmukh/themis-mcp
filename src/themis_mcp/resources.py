"""Static resources: disclaimer, supported acts, and law PDF links."""

import json

DISCLAIMER = (
    "This is not legal advice. THEMIS provides orientation on Indian statutory law. "
    "Consult a qualified lawyer for authoritative guidance."
)

ACTS = {
    "bns": {
        "name": "The Bharatiya Nyaya Sanhita, 2023",
        "short": "BNS",
        "sections": 358,
        "domain": "Criminal law",
    },
    "bnss": {
        "name": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
        "short": "BNSS",
        "sections": 531,
        "domain": "Criminal procedure",
    },
    "bsa": {
        "name": "The Bharatiya Sakshya Adhiniyam, 2023",
        "short": "BSA",
        "sections": 170,
        "domain": "Evidence",
    },
    "ipc": {
        "name": "The Indian Penal Code, 1860",
        "short": "IPC",
        "sections": 511,
        "domain": "Legacy criminal law",
    },
    "rti_2005": {
        "name": "The Right to Information Act, 2005",
        "short": "RTI",
        "sections": 31,
        "domain": "Right to Information",
    },
    "consumer_protection_2019": {
        "name": "The Consumer Protection Act, 2019",
        "short": "CPA",
        "sections": 107,
        "domain": "Consumer protection",
    },
}

# Official law PDF links from Indian government
LAW_PDFS = {
    "bns": {
        "title": "Bharatiya Nyaya Sanhita, 2023",
        "pdf_url": "https://www.indiacode.nic.in/bitstream/123456789/2008/1/A2023-45.pdf",
        "legislative_url": "https://www.legislative.gov.in/act/A2023-45",
        "date_enacted": "2023-12-25",
        "effective_date": "2024-07-01",
    },
    "bnss": {
        "title": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "pdf_url": "https://www.indiacode.nic.in/bitstream/123456789/2009/1/A2023-46.pdf",
        "legislative_url": "https://www.legislative.gov.in/act/A2023-46",
        "date_enacted": "2023-12-25",
        "effective_date": "2024-07-01",
    },
    "bsa": {
        "title": "Bharatiya Sakshya Adhiniyam, 2023",
        "pdf_url": "https://www.indiacode.nic.in/bitstream/123456789/2010/1/A2023-47.pdf",
        "legislative_url": "https://www.legislative.gov.in/act/A2023-47",
        "date_enacted": "2023-12-25",
        "effective_date": "2024-07-01",
    },
    "ipc": {
        "title": "Indian Penal Code, 1860",
        "pdf_url": "https://www.indiacode.nic.in/bitstream/123456789/3647/1/A1860-45.pdf",
        "legislative_url": "https://www.legislative.gov.in/act/A1860-45",
        "date_enacted": "1860-10-06",
        "effective_date": "1862-01-01",
    },
    "rti_2005": {
        "title": "Right to Information Act, 2005",
        "pdf_url": "https://www.indiacode.nic.in/bitstream/123456789/2008/1/A2005-22.pdf",
        "legislative_url": "https://www.legislative.gov.in/act/A2005-22",
        "date_enacted": "2005-06-21",
        "effective_date": "2005-10-12",
    },
    "consumer_protection_2019": {
        "title": "Consumer Protection Act, 2019",
        "pdf_url": "https://www.indiacode.nic.in/bitstream/123456789/2009/1/A2019-35.pdf",
        "legislative_url": "https://www.legislative.gov.in/act/A2019-35",
        "date_enacted": "2019-08-09",
        "effective_date": "2020-07-20",
    },
}


def get_disclaimer() -> str:
    return DISCLAIMER


def get_acts() -> str:
    return json.dumps(ACTS, indent=2)


def get_law_pdfs() -> str:
    return json.dumps(LAW_PDFS, indent=2)


def get_law_pdf(act: str) -> str:
    """Get PDF info for a specific act."""
    act_lower = act.lower()
    if act_lower in LAW_PDFS:
        return json.dumps(LAW_PDFS[act_lower], indent=2)
    return json.dumps({"error": f"No PDF info found for act: {act}"}, indent=2)
