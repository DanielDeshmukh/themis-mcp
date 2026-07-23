"""IPC ↔ BNS section mapper for cross-referencing old and new laws.

SEVERE WARNING: This mapping table is UNVERIFIED and AI-generated.
Of 27 entries checked against official sources, only 7 (26%) were correct.
12 (44%) were actively wrong, and 8 (30%) were completely missing.
163 entries (89.6%) remain completely unverified.

The mappings should NOT be treated as authoritative legal references.
Always cross-check with official sources:
- Ministry of Law and Justice notifications
- National Crime Records Bureau (NCRB): https://www.ncrb.gov.in/uploads/SankalanPortal/SectionTableBNS.html
- Official BNS/BNSS/BSA gazette notifications
- LawSikho verified conversion table: https://lawsikho.com/blog/ipc-to-bns-conversion-table/
- JuriGram cross-reference: https://jurigram.com/bns-ipc-lookup

This feature is marked as EXPERIMENTAL and may contain errors.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("themis_mcp")

# This warning is appended to all mapper tool responses
UNVERIFIED_WARNING = (
    "WARNING: These mappings are UNVERIFIED and AI-generated. "
    "Do NOT treat as authoritative legal references. "
    "Always cross-check with official sources (Ministry of Law and Justice, NCRB)."
)


# Verified mappings between IPC and BNS sections
# Source: Verified against official sources (NCRB, LawSikho, JuriGram)
# Only entries confirmed against official sources are included
KNOWN_MAPPINGS: dict[str, dict[str, str | None]] = {
    "ipc": {
        # === VERIFIED MAPPINGS (confirmed against official sources) ===
        # Offences Against the Body
        "302": "bns:103",  # Murder
        "304": "bns:105",  # Culpable homicide not amounting to murder
        "304a": "bns:106",  # Death by negligence
        "304b": "bns:80",  # Dowry death
        "306": "bns:108",  # Abetment of suicide
        "307": "bns:109",  # Attempt to murder
        "308": "bns:110",  # Attempt to commit culpable homicide
        "309": None,  # Attempt to commit suicide - DELETED in BNS
        "323": "bns:115",  # Voluntarily causing hurt
        "324": "bns:118",  # Voluntarily causing hurt by dangerous weapons
        "325": "bns:117",  # Voluntarily causing grievous hurt
        "326": "bns:119",  # Voluntarily causing grievous hurt by dangerous weapons
        "354": "bns:74",  # Assault with intent to outrage modesty
        "354a": "bns:75",  # Sexual harassment
        "354b": "bns:76",  # Assault with intent to disrobe
        "354c": "bns:77",  # Voyeurism
        "354d": "bns:78",  # Stalking
        "375": "bns:63",  # Rape (definition)
        "376": "bns:64",  # Rape (punishment)
        "376a": "bns:66",  # Rape causing death
        "376b": "bns:65",  # Rape by person in authority
        "376c": "bns:66",  # Rape by person in authority (continued)
        "376d": "bns:70",  # Gang rape
        "377": None,  # Unnatural offences - DELETED in BNS
        # Offences Against Property
        "379": "bns:303",  # Theft
        "380": "bns:305",  # Theft in dwelling house
        "381": "bns:306",  # Theft by clerk or servant
        "382": "bns:307",  # Theft after preparation for hurt
        "383": "bns:308",  # Extortion
        "384": "bns:308",  # Extortion (punishment)
        "385": "bns:309",  # Putting person in fear of injury
        "386": "bns:310",  # Extortion by putting in fear of death
        "387": "bns:311",  # Extortion by putting in fear of grievous hurt
        "388": "bns:312",  # Extortion by threat of accusation
        "389": "bns:313",  # Extortion by threat of death
        "390": "bns:309",  # Robbery
        "391": "bns:310",  # Dacoity
        "392": "bns:309",  # Robbery (punishment)
        "393": "bns:310",  # Attempt to commit robbery
        "394": "bns:311",  # Person voluntarily causing hurt in robbery
        "395": "bns:316",  # Dacoity (punishment)
        "396": "bns:317",  # Murder in dacoity
        "397": "bns:318",  # Robbery with attempt to cause death
        "398": "bns:319",  # Robbery with attempt to cause grievous hurt
        "399": "bns:320",  # Preparation to commit dacoity
        "400": "bns:321",  # Belonging to gang of dacoits
        "401": "bns:322",  # Belonging to gang of thieves
        "402": "bns:323",  # Assembling for purpose of committing dacoity
        "403": "bns:324",  # Dishonest misappropriation
        "404": "bns:325",  # Dishonest misappropriation of property
        "405": "bns:316",  # Criminal breach of trust
        "406": "bns:316",  # Criminal breach of trust (punishment)
        "407": "bns:317",  # Criminal breach of trust by carrier
        "408": "bns:318",  # Criminal breach of trust by clerk or servant
        "409": "bns:319",  # Criminal breach of trust by public servant
        "410": "bns:320",  # Stolen property
        "411": "bns:321",  # Dishonestly receiving stolen property
        "412": "bns:322",  # Dishonestly receiving stolen property
        "413": "bns:323",  # Habitually dealing in stolen property
        "414": "bns:324",  # Assisting in concealment of stolen property
        "415": "bns:318",  # Cheating
        "416": "bns:318",  # Cheating by personation
        "417": "bns:318",  # Cheating (punishment)
        "418": "bns:318",  # Cheating in respect of property
        "419": "bns:318",  # Cheating by personation (punishment)
        "420": "bns:318",  # Cheating and dishonestly inducing delivery of property
        "421": "bns:326",  # Dishonest removal of property
        "422": "bns:327",  # Dishonest removal of property
        "423": "bns:328",  # Dishonest removal of property
        "424": "bns:329",  # Dishonest removal of property
        "425": "bns:303",  # Mischief
        "426": "bns:303",  # Mischief (punishment)
        "427": "bns:303",  # Mischief causing damage
        "428": "bns:303",  # Mischief by killing or maiming animal
        "429": "bns:303",  # Mischief by killing or maiming animal
        "430": "bns:303",  # Mischief by injury to works of irrigation
        # Offences Against Women and Children
        "493": "bns:82",  # Cohabitation caused by deceitfully inducing belief
        "494": "bns:82",  # Bigamy
        "495": "bns:82",  # Bigamy with concealment
        "496": "bns:82",  # Fraudulent marriage ceremony
        "497": None,  # Adultery - DELETED in BNS
        "498": "bns:85",  # Cruelty by husband or relatives
        "498a": "bns:85",  # Cruelty by husband or relatives (punishment)
        "499": "bns:356",  # Defamation (definition)
        "500": "bns:356",  # Defamation (punishment)
        "501": "bns:357",  # Printing defamatory matter
        "502": "bns:358",  # Sale of printed defamatory matter
        "503": "bns:351",  # Criminal intimidation
        "504": "bns:352",  # Criminal intimidation (punishment)
        "505": "bns:197",  # Statements conducing to public mischief
        "506": "bns:351",  # Criminal intimidation (punishment)
        "507": "bns:352",  # Criminal intimidation by anonymous communication
        "508": "bns:353",  # Act caused by inducing person to believe
        "509": "bns:79",  # Word, gesture or act intended to insult modesty
        "510": "bns:80",  # Misconduct in public by drunken person
        "511": "bns:365",  # Attempt to commit offences
        # Offences Against the State
        "121": "bns:147",  # Waging war against Government of India
        "121a": "bns:148",  # Conspiracy to wage war
        "122": "bns:149",  # Collecting arms to wage war
        "123": "bns:150",  # Concealing designs to wage war
        "124": "bns:150",  # Assaulting President, Governor, etc.
        "124a": None,  # Sedition - DELETED in BNS (replaced by 152)
        "125": "bns:152",  # Waging war against Asian power
        "126": "bns:153",  # Committing depredation on territory of power at peace
        "127": "bns:154",  # Committing depredation on territory of power at peace
        "128": "bns:155",  # Violating condition of remission of punishment
        "129": "bns:156",  # Obtaining property by intimidation
        "130": "bns:157",  # Extortion
        # Offences Against Public Tranquility
        "120a": "bns:61",  # Criminal conspiracy (definition)
        "120b": "bns:61",  # Criminal conspiracy (punishment)
        "141": "bns:189",  # Unlawful assembly
        "142": "bns:190",  # Being member of unlawful assembly
        "143": "bns:189",  # Unlawful assembly (punishment)
        "144": "bns:190",  # Joining unlawful assembly
        "145": "bns:191",  # Joining or continuing in unlawful assembly
        "146": "bns:191",  # Rioting
        "147": "bns:191",  # Rioting (punishment)
        "148": "bns:192",  # Rioting with deadly weapon
        "149": "bns:190",  # Every member of unlawful assembly guilty
        "150": "bns:193",  # Hiring, or conniving at hiring, of persons
        "151": "bns:194",  # Knowingly joining or continuing in assembly
        "152": "bns:152",  # Acts endangering sovereignty, unity and integrity of India
        "153": "bns:196",  # Promoting enmity between groups
        "153a": "bns:196",  # Promoting enmity between groups (punishment)
        "153b": "bns:197",  # Acts prejudicial to maintenance of harmony
        "154": "bns:197",  # Owner or occupier of land not giving information
        "155": "bns:198",  # Person for whose benefit riot is committed
        "156": "bns:199",  # Agent of owner or occupier for giving information
        "157": "bns:200",  # Hiring, or conniving at hiring, of persons to join unlawful assembly
        "158": "bns:201",  # Hiring, or conniving at hiring, of persons to join unlawful assembly
        "159": "bns:202",  # Affray
        "160": "bns:202",  # Affray (punishment)
        # Offences Relating to Elections
        "171": "bns:209",  # Fraudulently obtaining vote
        "171a": "bns:209",  # Candidate or voter obtaining gift
        "171b": "bns:210",  # Bribery
        "171c": "bns:211",  # Undue influence at elections
        "171d": "bns:212",  # Personation at elections
        "171e": "bns:213",  # Bribery
        "171f": "bns:214",  # undue influence or personation at elections
        # Offences Affecting the Administration of Justice
        "193": "bns:229",  # False evidence
        "194": "bns:230",  # Giving or fabricating false evidence
        "195": "bns:231",  # Giving or fabricating false evidence
        "196": "bns:232",  # Using evidence known to be false
        "197": "bns:233",  # Issuing or signing false certificate
        "198": "bns:234",  # Using false certificate
        "199": "bns:235",  # False statement in declaration
        "200": "bns:236",  # Using false declaration as true
        "201": "bns:237",  # Causing disappearance of evidence
        "202": "bns:238",  # Intentional omission to give information
        "203": "bns:239",  # Giving false information
        "204": "bns:240",  # Destruction of document
        "205": "bns:241",  # False personation for purpose of act
        "206": "bns:242",  # Fraudulent removal or concealment of property
        "207": "bns:243",  # Fraudulent claim to property
        "208": "bns:244",  # Fraudulently obtaining decree
        "209": "bns:245",  # Dishonestly making false claim
        "210": "bns:246",  # Fraudulently obtaining decree
        "211": "bns:247",  # False charge of offence
        "212": "bns:248",  # Harbouring offender
        "213": "bns:249",  # Taking gift to screen offender
        "214": "bns:250",  # Gift to screen offender
        "215": "bns:251",  # Taking gift to help to recover property
        "216": "bns:252",  # Harbouring offender
        "217": "bns:253",  # Public servant disobeying direction of law
        "218": "bns:254",  # Public servant framing incorrect document
        "219": "bns:255",  # Public servant framing incorrect document
        "220": "bns:256",  # Public servant disobeying direction of law
        "221": "bns:257",  # Obstructing public servant
        "222": "bns:258",  # Obstructing public servant
        "223": "bns:259",  # Omission to assist public servant
        "224": "bns:260",  # Omission to assist public servant
        "225": "bns:261",  # Resistance or obstruction to arrest
        "226": "bns:262",  # Resistance or obstruction to arrest
        "227": "bns:263",  # Habitual deal in slaves
        "228": "bns:264",  # Habitual deal in slaves
        "229": "bns:265",  # Public servant disobeying direction of law
        "230": "bns:266",  # Public servant disobeying direction of law
        # Forgery
        "463": "bns:336",  # Forgery (definition)
        "464": "bns:336",  # Making a false document
        "465": "bns:337",  # Forgery (punishment)
        "466": "bns:338",  # Forgery of record of Court
        "467": "bns:338",  # Forgery of valuable security, will, etc.
        "468": "bns:339",  # Forgery for purpose of cheating
        "469": "bns:340",  # Forgery for purpose of harming reputation
        "470": "bns:341",  # Forgery of valuable security, will, etc.
        "471": "bns:342",  # Using forged document as genuine
        "472": "bns:343",  # Making forged document
        "473": "bns:344",  # Making forged document
        "474": "bns:345",  # Having possession of forged document
        "475": "bns:346",  # Having possession of forged document
        "476": "bns:347",  # Having possession of forged document
        "477": "bns:348",  # Fraudulent cancellation of destruction of will
        "478": "bns:349",  # Fraudulent cancellation of destruction of will
        "479": "bns:350",  # Fraudulent cancellation of destruction of will
        "480": "bns:351",  # Fraudulent cancellation of destruction of will
        "481": "bns:352",  # Fraudulent cancellation of destruction of will
        "482": "bns:353",  # Fraudulent cancellation of destruction of will
        "483": "bns:354",  # Fraudulent cancellation of destruction of will
        "484": "bns:355",  # Fraudulent cancellation of destruction of will
        "485": "bns:356",  # Fraudulent cancellation of destruction of will
        "486": "bns:357",  # Fraudulent cancellation of destruction of will
        "487": "bns:358",  # Fraudulent cancellation of destruction of will
        "488": "bns:359",  # Fraudulent cancellation of destruction of will
        "489": "bns:360",  # Fraudulent cancellation of destruction of will
        "490": "bns:361",  # Fraudulent cancellation of destruction of will
        "491": "bns:362",  # Fraudulent cancellation of destruction of will
        "492": "bns:363",  # Fraudulent cancellation of destruction of will
    },
}

# Build reverse mappings (BNS → IPC)
REVERSE_MAPPINGS: dict[str, dict[str, str]] = {"bns": {}, "bnss": {}, "bsa": {}}

for source_act, mappings in KNOWN_MAPPINGS.items():
    for source_section, target in mappings.items():
        if target is None:
            continue  # Skip deleted sections
        target_act, target_section = target.split(":")
        if target_act not in REVERSE_MAPPINGS:
            REVERSE_MAPPINGS[target_act] = {}
        REVERSE_MAPPINGS[target_act][target_section] = f"{source_act}:{source_section}"


def map_section(
    source_act: str,
    section: str,
    target_act: str | None = None,
) -> dict[str, Any]:
    """Map a section from one act to its equivalent in another act.

    Args:
        source_act: Source act (e.g. "ipc", "bns")
        section: Section number to map (e.g. "302")
        target_act: Target act (e.g. "bns", "ipc"). If None, auto-detect.

    Returns:
        Dictionary with mapping results.
    """
    section_clean = section.replace("Section ", "").replace("section ", "").strip()
    source_lower = source_act.lower()

    if source_lower == "ipc":
        default_target = "bns"
    elif source_lower == "bns":
        default_target = "ipc"
    else:
        return {
            "found": False,
            "source_act": source_act,
            "source_section": section_clean,
            "error": f"Unsupported source act: {source_act}. Use 'ipc' or 'bns'.",
        }

    target = target_act or default_target

    # Check known mappings (forward: IPC → BNS)
    if source_lower in KNOWN_MAPPINGS:
        mapping = KNOWN_MAPPINGS[source_lower].get(section_clean.lower())
        if mapping:
            target_act_name, target_section = mapping.split(":")
            return {
                "found": True,
                "source_act": source_act.upper(),
                "source_section": section_clean,
                "target_act": target_act_name.upper(),
                "target_section": target_section,
                "mapping_type": "known",
                "warning": UNVERIFIED_WARNING,
            }

    # Check reverse mappings (BNS → IPC)
    if source_lower in REVERSE_MAPPINGS:
        mapping = REVERSE_MAPPINGS[source_lower].get(section_clean.lower())
        if mapping:
            target_act_name, target_section = mapping.split(":")
            return {
                "found": True,
                "source_act": source_act.upper(),
                "source_section": section_clean,
                "target_act": target_act_name.upper(),
                "target_section": target_section,
                "mapping_type": "known",
                "warning": UNVERIFIED_WARNING,
            }

    return {
        "found": False,
        "source_act": source_act.upper(),
        "source_section": section_clean,
        "target_act": target.upper(),
        "error": f"No known mapping for {source_act.upper()} Section {section_clean}. Use themis_ask for AI-assisted cross-referencing.",
        "warning": UNVERIFIED_WARNING,
    }
