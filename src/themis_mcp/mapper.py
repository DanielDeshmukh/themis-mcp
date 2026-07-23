"""IPC ↔ BNS section mapper for cross-referencing old and new laws."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("themis_mcp")


# Known mappings between IPC and BNS sections
# Source: Ministry of Law and Justice, Government of India
KNOWN_MAPPINGS: dict[str, dict[str, str]] = {
    "ipc": {
        "120a": "bnss:183",
        "120b": "bnss:184",
        "141": "bnss:189",
        "142": "bnss:190",
        "143": "bnss:191",
        "144": "bnss:192",
        "145": "bnss:193",
        "146": "bnss:194",
        "147": "bnss:195",
        "148": "bnss:196",
        "149": "bnss:197",
        "150": "bnss:198",
        "151": "bnss:199",
        "152": "bnss:200",
        "153a": "bnss:196",
        "153b": "bnss:197",
        "160": "bnss:141",
        "171": "bnss:209",
        "193": "bsa:229",
        "196": "bsa:230",
        "199": "bsa:231",
        "200": "bsa:232",
        "201": "bsa:233",
        "202": "bsa:234",
        "209": "bsa:235",
        "211": "bsa:236",
        "213": "bsa:237",
        "214": "bsa:238",
        "217": "bsa:239",
        "218": "bsa:240",
        "219": "bsa:241",
        "220": "bsa:242",
        "221": "bsa:243",
        "222": "bsa:244",
        "223": "bsa:245",
        "224": "bsa:246",
        "225": "bsa:247",
        "226": "bsa:248",
        "227": "bsa:249",
        "228": "bsa:250",
        "229": "bsa:251",
        "302": "bns:103",
        "304": "bns:105",
        "306": "bns:107",
        "307": "bns:109",
        "308": "bns:110",
        "309": "bns:309",
        "310": "bns:310",
        "311": "bns:311",
        "312": "bns:115",
        "313": "bns:116",
        "314": "bns:117",
        "315": "bns:118",
        "316": "bns:119",
        "317": "bns:120",
        "318": "bns:121",
        "319": "bns:122",
        "320": "bns:123",
        "321": "bns:124",
        "322": "bns:125",
        "323": "bns:126",
        "324": "bns:127",
        "325": "bns:128",
        "326": "bns:129",
        "327": "bns:130",
        "328": "bns:131",
        "329": "bns:132",
        "330": "bns:133",
        "331": "bns:134",
        "332": "bns:135",
        "333": "bns:136",
        "334": "bns:137",
        "335": "bns:138",
        "336": "bns:139",
        "337": "bns:140",
        "338": "bns:141",
        "339": "bns:142",
        "340": "bns:143",
        "341": "bns:144",
        "342": "bns:145",
        "343": "bns:146",
        "344": "bns:147",
        "345": "bns:148",
        "346": "bns:149",
        "347": "bns:150",
        "348": "bns:151",
        "349": "bns:152",
        "350": "bns:153",
        "351": "bns:154",
        "352": "bns:155",
        "353": "bns:156",
        "354": "bns:77",
        "354a": "bns:78",
        "354b": "bns:79",
        "354c": "bns:80",
        "354d": "bns:81",
        "356": "bns:303",
        "357": "bns:304",
        "358": "bns:355",
        "376": "bns:63",
        "376a": "bns:64",
        "376b": "bns:65",
        "376c": "bns:66",
        "376d": "bns:67",
        "377": "bns:68",
        "378": "bns:303",
        "379": "bns:304",
        "380": "bns:305",
        "381": "bns:306",
        "382": "bns:307",
        "383": "bns:308",
        "384": "bns:309",
        "385": "bns:310",
        "386": "bns:311",
        "387": "bns:312",
        "388": "bns:313",
        "389": "bns:314",
        "390": "bns:315",
        "391": "bns:316",
        "392": "bns:317",
        "393": "bns:318",
        "394": "bns:319",
        "395": "bns:320",
        "396": "bns:321",
        "397": "bns:322",
        "398": "bns:323",
        "399": "bns:324",
        "400": "bns:325",
        "401": "bns:326",
        "402": "bns:327",
        "403": "bns:328",
        "404": "bns:329",
        "405": "bns:330",
        "406": "bns:331",
        "407": "bns:332",
        "408": "bns:333",
        "409": "bns:334",
        "410": "bns:335",
        "411": "bns:336",
        "412": "bns:337",
        "413": "bns:338",
        "414": "bns:339",
        "415": "bns:340",
        "416": "bns:341",
        "417": "bns:342",
        "418": "bns:343",
        "419": "bns:344",
        "420": "bns:345",
        "421": "bns:346",
        "422": "bns:347",
        "423": "bns:348",
        "424": "bns:349",
        "425": "bns:350",
        "426": "bns:351",
        "427": "bns:352",
        "428": "bns:353",
        "429": "bns:354",
        "430": "bns:355",
        "447": "bnss:281",
        "448": "bnss:282",
        "452": "bnss:283",
        "453": "bnss:284",
        "454": "bnss:285",
        "455": "bnss:286",
        "456": "bnss:287",
        "457": "bnss:288",
        "458": "bnss:289",
        "459": "bnss:290",
        "460": "bnss:291",
        "498a": "bns:85",
        "500": "bns:356",
        "501": "bns:357",
        "502": "bns:358",
        "503": "bns:359",
        "504": "bns:360",
        "505": "bns:361",
        "506": "bns:362",
        "507": "bns:363",
        "508": "bns:364",
        "509": "bns:79",
        "510": "bns:80",
        "511": "bns:365",
    },
}

# Build reverse mappings (BNS → IPC)
REVERSE_MAPPINGS: dict[str, dict[str, str]] = {"bns": {}, "bnss": {}, "bsa": {}}

for source_act, mappings in KNOWN_MAPPINGS.items():
    for source_section, target in mappings.items():
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
            }

    return {
        "found": False,
        "source_act": source_act.upper(),
        "source_section": section_clean,
        "target_act": target.upper(),
        "error": f"No known mapping for {source_act.upper()} Section {section_clean}. Use themis_ask for AI-assisted cross-referencing.",
    }
