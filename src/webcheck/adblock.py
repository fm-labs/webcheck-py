from adblockparser import AdblockRules

from webcheck.conf import WEBCHECK_DATA_DIR

def load_easylist(name: str = "easylist"):
    rules = []
    try:
        with open(f"{WEBCHECK_DATA_DIR}/adblock/{name}.txt", 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('!'):
                    rules.append(line)
    except FileNotFoundError:
        pass
    return rules

raw_rules = load_easylist()
adblock_rules = AdblockRules(load_easylist("easylist"))
privacy_rules = AdblockRules(load_easylist("easyprivacy"))
cookiemonster_rules = AdblockRules(load_easylist("cookiemonster"))
