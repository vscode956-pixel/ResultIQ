import re
from typing import Dict, List, Optional

def extract_program_code(program: Optional[str]) -> str:
    if not program or not isinstance(program, str):
        return 'BBA'
    cleaned = program.strip()
    if not cleaned:
        return 'BBA'

    # Check for parentheses like "Bachelor of Business Administration (BBA)"
    match = re.search(r'\(([^)]+)\)', cleaned)
    if match:
        return match.group(1).strip().upper()

    norm = cleaned.lower()
    if 'business' in norm or 'administration' in norm or 'bba' in norm:
        return 'BBA'
    if 'computer' in norm or 'application' in norm or 'bca' in norm:
        return 'BCA'
    if 'commerce' in norm or 'bcom' in norm:
        return 'BCOM'
    if 'hotel' in norm or 'bhm' in norm:
        return 'BHM'
    if 'science' in norm or 'bsc' in norm:
        return 'BSC'
    if 'arts' in norm or 'ba' in norm:
        return 'BA'

    if len(cleaned) <= 6 and cleaned.isalnum():
        return cleaned.upper()

    return cleaned


# Report groups we support
REPORT_GROUPS = [
    'General',
    'EWS',
    'OBC',
    'SC',
    'ST',
]

# Mapping from lowercase tokens to report groups
DEFAULT_CATEGORY_MAP: Dict[str, str] = {
    # General
    'general': 'General',
    'gm': 'General',
    # EWS
    'ews': 'EWS',
    'economically weaker section': 'EWS',
    # OBC variations
    'obc': 'OBC',
    'category i': 'OBC',
    'category ii(a)': 'OBC',
    'category ii(b)': 'OBC',
    'category iii(a)': 'OBC',
    'category iii(b)': 'OBC',
    # SC/ST
    'sc': 'SC',
    'scheduled caste': 'SC',
    'st': 'ST',
    'scheduled tribe': 'ST',
}

# PWD, MM (Muslim Minority), OM (Other Minority) identification lists
# By default keep these empty to avoid guessing institution-specific mappings.
PWD_KEYS: List[str] = []
MM_KEYS: List[str] = []
OM_KEYS: List[str] = []

# Attempt to load `demographics_config.json` from project root to override defaults.
try:
    CONFIG_PATH = Path(__file__).resolve().parent / 'demographics_config.json'
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as fh:
            cfg = json.load(fh)
            # category mapping
            cat_map = cfg.get('category_mapping') or {}
            for k, v in cat_map.items():
                DEFAULT_CATEGORY_MAP[k.strip().lower()] = v
            # override keys lists if provided
            mm = cfg.get('muslim_minority_castes')
            if isinstance(mm, list):
                MM_KEYS = [x.strip().lower() for x in mm if x]
            om = cfg.get('other_minority_castes')
            if isinstance(om, list):
                OM_KEYS = [x.strip().lower() for x in om if x]
            mm_religions = cfg.get('muslim_minority_religions')
            if isinstance(mm_religions, list):
                MM_KEYS += [x.strip().lower() for x in mm_religions if x]
            om_religions = cfg.get('other_minority_religions')
            if isinstance(om_religions, list):
                OM_KEYS += [x.strip().lower() for x in om_religions if x]
            pwd = cfg.get('pwd_keys')
            if isinstance(pwd, list):
                PWD_KEYS = [x.strip().lower() for x in pwd if x]
except Exception:
    # silent fallback to defaults
    pass

def map_category(raw: str) -> str:
    if not raw:
        return 'General'
    key = raw.strip().lower()
    return DEFAULT_CATEGORY_MAP.get(key, 'General')

def is_pwd(raw: str) -> bool:
    if not raw:
        return False
    v = raw.strip().lower()
    # check configured exact keys or substrings
    return any(k in v for k in PWD_KEYS)

def is_mm(raw: str) -> bool:
    if not raw:
        return False
    v = raw.strip().lower()
    return any(k in v for k in MM_KEYS)

def is_om(raw: str) -> bool:
    if not raw:
        return False
    v = raw.strip().lower()
    return any(k in v for k in OM_KEYS)
