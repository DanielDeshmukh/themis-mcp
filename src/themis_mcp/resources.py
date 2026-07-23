"""Static resources: disclaimer and supported acts."""

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


def get_disclaimer() -> str:
    return DISCLAIMER


def get_acts() -> str:
    return json.dumps(ACTS, indent=2)
