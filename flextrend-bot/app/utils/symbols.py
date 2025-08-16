def normalize_symbol_from_tv(tv: str) -> str:
    tv = tv.strip()
    if ":" in tv:
        tv = tv.split(":", 1)[1]
    tv = tv.replace(".P", "").upper()
    if tv.endswith("USDT") and "/" not in tv:
        return f"{tv[:-4]}/USDT"
    return tv
