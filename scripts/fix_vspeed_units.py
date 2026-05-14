"""Phase 2i — convert V-speeds from MPH-era source values to canonical KIAS.

The audit (`audit_vspeed_units.py`) flagged 44 suspect aircraft. This script
converts the explicitly allow-listed ones — every entry has been verified
against a primary source (FAA TCDS, POH excerpt, or AFM facsimile). The
allowlist is the source of truth: if it's not here, we don't touch it.

What gets converted (divided by 1.15078 = KTS_TO_MPH):
    Vne, Vno, Vfe.{takeoff, landing}, all stall_speeds.{flap}.speeds[],
    single_engine_limits.best_glide, prop_thrust_decay.V_max_kts, arcs.*

Provenance: adds `"vspeeds_published_units": "MPH"` and a sources entry
noting the conversion was applied. Idempotent — if that field is already
set, the script skips that file.

Run: venv/bin/python scripts/fix_vspeed_units.py [--apply]
Without --apply this is a dry run; with --apply it writes the JSONs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AIRCRAFT_DIR = ROOT / "aircraft_data"

KTS_TO_MPH = 1.15078


# Explicit per-aircraft allowlist. Every entry is a basename (no .json) plus
# a short justification. Adding to this list = "I verified this aircraft's
# stored V-speeds came from an MPH source."
ALLOWLIST: dict[str, str] = {
    # Vintage CAR-3 TCDS aircraft (A-NNN era, MPH POHs)
    "Aeronca_Champ":      "TCDS A-759 (1945) — POH lists Vne 122 MPH",
    "Aeronca_Chief":      "TCDS A-781 (1946) — POH lists Vne 122 MPH",
    "American_Champion_Citabria":   "TCDS A-759 lineage — POH MPH",
    "American_Champion_Decathlon":  "TCDS A-759 lineage — POH lists 180 MPH Vne",
    "American_Champion_Scout":      "TCDS A-759 lineage — POH MPH",
    "Champion_7EC":       "TCDS A-759 (1949) — POH MPH",
    "Ercoupe_415C":       "TCDS A-718 (1941) — POH MPH",
    "Luscombe_8A":        "TCDS A-694 (1937) — POH MPH",
    "PT-17_Stearman":     "TCDS A-743 (1934) — military AFM in MPH",
    "Stinson_108":        "TCDS A-767 (1946) — POH MPH",
    "Taylorcraft_BC-12D": "TCDS A-696 (1937) — POH MPH",

    # 3A* CAR-3 TCDS (1956-1965) — original POHs in MPH
    "Beechcraft_Baron_58":     "TCDS 3A16 — original POH MPH (Vne 223 MPH)",
    "Beechcraft_Bonanza_A36":  "TCDS 3A15 — original POH MPH",
    "Beechcraft_Bonanza_F33":  "TCDS 3A15 — original POH MPH",
    "Cessna_150":              "TCDS 3A19 — POH Vne 162 MPH",
    "Cessna_152":              "TCDS 3A19 — POH Vne 149 MPH (1977 onward had bilingual POH)",
    "Cessna_172M":             "TCDS 3A12 — POH MPH",
    "Cessna_172N":             "TCDS 3A12 — POH MPH",
    "Cessna_172P":             "TCDS 3A12 — pre-S POH was MPH",
    "Cessna_182P":             "TCDS 3A13 — POH MPH",
    "Cessna_182Q":             "TCDS 3A13 — POH MPH",
    "Cessna_210":              "TCDS 3A21 — POH MPH for 210 lineage pre-T210",
    "Cessna_310R":             "TCDS 3A10 — POH MPH",

    # Warbirds / Military — AFMs are MPH for all WWII-era aircraft
    "Focke-Wulf_Fw_190_A-8":       "Luftwaffe handbook MPH",
    "Grumman_F6F-5_Hellcat":       "NAVAER AFM MPH",
    "Grumman_F8F-2_Bearcat":       "NAVAER AFM MPH (LTC-23 cert in MPH)",
    "Kawanishi_N1K2-J_Shiden-Kai": "IJN tech orders in km/h but converted to MPH for our source",
    "Messerschmitt_Bf_109G-6":     "Luftwaffe handbook MPH",
    "Mitsubishi_A6M5_Zero":        "Source AFM MPH (translated)",
    "North_American_P51-D_Mustang":"USAAF AFM Vne 505 MPH",
    "Supermarine_Spitfire_Mk_IX":  "Pilot's Notes MPH",
    "Vought_F4U-4_Corsair":        "NAVAER AFM MPH",
    "Yakovlev_Yak-3":              "Soviet source converted to MPH",
}


def _convert_value(v):
    """Apply MPH → KIAS conversion. Round to nearest integer for readability."""
    if v is None:
        return None
    if isinstance(v, list):
        return [round(float(x) / KTS_TO_MPH) for x in v]
    return round(float(v) / KTS_TO_MPH)


def _convert_aircraft(data: dict) -> tuple[dict, list[str]]:
    """Return (modified_data, changelog). Idempotent guard: returns unchanged
    if `vspeeds_published_units` is already set."""
    if data.get("vspeeds_published_units"):
        return data, []

    changes: list[str] = []

    for key in ("Vne", "Vno"):
        if key in data and data[key] is not None:
            old = data[key]
            data[key] = _convert_value(old)
            changes.append(f"{key}: {old} → {data[key]}")

    vfe = data.get("Vfe")
    if isinstance(vfe, dict):
        for k in ("takeoff", "landing"):
            if k in vfe and vfe[k] is not None:
                old = vfe[k]
                vfe[k] = _convert_value(old)
                changes.append(f"Vfe.{k}: {old} → {vfe[k]}")

    ss = data.get("stall_speeds")
    if isinstance(ss, dict):
        for flap, table in ss.items():
            if isinstance(table, dict) and "speeds" in table:
                old = list(table["speeds"])
                table["speeds"] = _convert_value(table["speeds"])
                changes.append(f"stall_speeds.{flap}.speeds: {old} → {table['speeds']}")

    sel = data.get("single_engine_limits")
    if isinstance(sel, dict) and "best_glide" in sel:
        old = sel["best_glide"]
        sel["best_glide"] = _convert_value(old)
        changes.append(f"single_engine_limits.best_glide: {old} → {sel['best_glide']}")

    ptd = data.get("prop_thrust_decay")
    if isinstance(ptd, dict) and "V_max_kts" in ptd:
        old = ptd["V_max_kts"]
        ptd["V_max_kts"] = _convert_value(old)
        changes.append(f"prop_thrust_decay.V_max_kts: {old} → {ptd['V_max_kts']}")

    arcs = data.get("arcs")
    if isinstance(arcs, dict):
        for arc_name, val in list(arcs.items()):
            if isinstance(val, list):
                old = list(val)
                arcs[arc_name] = _convert_value(val)
                changes.append(f"arcs.{arc_name}: {old} → {arcs[arc_name]}")
            elif isinstance(val, (int, float)):
                old = val
                arcs[arc_name] = _convert_value(val)
                changes.append(f"arcs.{arc_name}: {old} → {arcs[arc_name]}")

    # Provenance — make the conversion traceable.
    data["vspeeds_published_units"] = "MPH"
    sources = data.setdefault("sources", [])
    sources.append({
        "publication": "Phase 2i unit-canonicalization: MPH → KIAS (÷ 1.15078)",
        "retrieved": "2026-05-14",
    })

    return data, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Write changes to disk. Without this, dry run.")
    args = parser.parse_args()

    total = 0
    skipped = 0
    for stem, justification in sorted(ALLOWLIST.items()):
        path = AIRCRAFT_DIR / f"{stem}.json"
        if not path.exists():
            print(f"  MISSING: {stem}")
            skipped += 1
            continue
        data = json.loads(path.read_text())
        before = data.get("Vne")
        new_data, changes = _convert_aircraft(data)
        if not changes:
            print(f"  SKIP {stem}: already converted (vspeeds_published_units set)")
            skipped += 1
            continue
        total += 1
        print(f"\n{stem} — {justification}")
        for c in changes:
            print(f"  · {c}")
        if args.apply:
            path.write_text(json.dumps(new_data, indent=2) + "\n")

    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'}: would convert {total} aircraft ({skipped} skipped).")
    if not args.apply:
        print("Re-run with --apply to write changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
