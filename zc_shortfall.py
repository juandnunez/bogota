#!/usr/bin/env python3
"""Zona Centro unbacked redemptions: per-user shortfall.

Reconstructs, from the two CSV extracts, the 104 accounts whose redemptions
were backed only by pre-launch (erased) accruals, and the points each one
spent that it never validly held.

Inputs (repo root, or pass paths as argv[1], argv[2]):
  zc_erase.csv   dump of zona_centro_erase_ledger_bak_20260917
  zc_ledger.csv  legacy_transactions rows for every user appearing in the above

Column names are resolved case-insensitively with common aliases, so a dump
whose headers differ slightly still loads. Missing required columns abort.

Output:
  stdout summary + the ranked table
  zona_centro_unbacked_104.csv
"""
from __future__ import annotations

import csv
import os
import sys
from datetime import datetime

# Floor rows written by the 2026-09-17 remediation must not count as valid
# accruals; they are the correction, not evidence of one.
REMEDIATION_START = datetime(2026, 9, 17, 19, 0, 0)

ALIASES = {
    "id_usuario": ("id_usuario", "user_id", "usuario_id", "iduser", "id_cliente"),
    "tipo": ("tipo", "type", "tipo_transaccion", "transaction_type"),
    "puntos": ("puntos", "points", "puntos_transaccion", "valor_puntos"),
    "fecha_negocio": ("fecha_negocio", "fecha", "business_date", "fecha_factura"),
    "created_at": ("created_at", "loaded_at", "fecha_creacion", "inserted_at"),
    "cod_almacen": ("cod_almacen", "store_code", "almacen", "codigo_almacen", "pos"),
}

ACCRUAL = ("acumulacion", "acumulación", "accrual", "earn", "credit")
REDEMPTION = ("redencion", "redención", "redemption", "redeem", "debit", "canje")


def resolve(header, wanted, required=True):
    """Map canonical name -> actual header, case/accent-insensitively."""
    lowered = {h.strip().lower(): h for h in header}
    out = {}
    for key in wanted:
        for alias in ALIASES[key]:
            if alias in lowered:
                out[key] = lowered[alias]
                break
        else:
            if required:
                sys.exit(
                    f"missing column {key!r}; tried {ALIASES[key]}\n"
                    f"  header was: {header}"
                )
            out[key] = None
    return out


def load(path, wanted, optional=()):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            sys.exit(f"{path}: empty file")
        cols = resolve(reader.fieldnames, wanted)
        cols.update(resolve(reader.fieldnames, optional, required=False))
        for row in reader:
            yield {k: (row[c] if c else None) for k, c in cols.items()}


def num(value):
    """Points as float; blank/None -> 0. Negative signs are preserved."""
    if value is None or value.strip() == "":
        return 0.0
    return float(value.strip().replace(",", ""))


def parse_ts(value):
    if not value or not value.strip():
        return None
    text = value.strip().replace("T", " ")
    for cut in (19, 16, 10):
        try:
            return datetime.strptime(text[:cut], "%Y-%m-%d %H:%M:%S"[:cut + 0] if cut == 19
                                     else ("%Y-%m-%d %H:%M" if cut == 16 else "%Y-%m-%d"))
        except ValueError:
            continue
    return None


def kind(tipo):
    t = (tipo or "").strip().lower()
    if any(t.startswith(a) for a in ACCRUAL):
        return "accrual"
    if any(t.startswith(r) for r in REDEMPTION):
        return "redemption"
    return "other"


def main():
    erase_path = sys.argv[1] if len(sys.argv) > 1 else "zc_erase.csv"
    ledger_path = sys.argv[2] if len(sys.argv) > 2 else "zc_ledger.csv"
    for p in (erase_path, ledger_path):
        if not os.path.exists(p):
            sys.exit(f"not found: {p}")

    # --- erased (invalid, pre-launch) accruals -------------------------------
    erased = {}
    erased_rows = 0
    for row in load(erase_path, ("id_usuario", "puntos", "fecha_negocio"),
                    optional=("cod_almacen",)):
        u = row["id_usuario"].strip()
        e = erased.setdefault(u, {"rows": 0, "pts": 0.0, "first": None,
                                  "last": None, "stores": set()})
        e["rows"] += 1
        e["pts"] += num(row["puntos"])
        d = (row["fecha_negocio"] or "")[:10]
        if d:
            e["first"] = d if e["first"] is None else min(e["first"], d)
            e["last"] = d if e["last"] is None else max(e["last"], d)
        if row.get("cod_almacen"):
            e["stores"].add(row["cod_almacen"].strip())
        erased_rows += 1

    # --- surviving ledger ----------------------------------------------------
    valid = {}
    red = {}
    skipped_floor = 0
    unknown_tipo = 0
    for row in load(ledger_path,
                    ("id_usuario", "tipo", "puntos", "fecha_negocio"),
                    optional=("created_at",)):
        u = row["id_usuario"].strip()
        if u not in erased:
            continue
        ts = parse_ts(row.get("created_at"))
        k = kind(row["tipo"])
        if k == "accrual":
            if ts is not None and ts >= REMEDIATION_START:
                skipped_floor += 1      # remediation floor row, not an accrual
                continue
            valid[u] = valid.get(u, 0.0) + num(row["puntos"])
        elif k == "redemption":
            if ts is not None and ts >= REMEDIATION_START:
                continue
            r = red.setdefault(u, {"pts": 0.0, "n": 0, "first": None, "last": None})
            r["pts"] += abs(num(row["puntos"]))
            r["n"] += 1
            d = (row["fecha_negocio"] or "")[:10]
            if d:
                r["first"] = d if r["first"] is None else min(r["first"], d)
                r["last"] = d if r["last"] is None else max(r["last"], d)
        else:
            unknown_tipo += 1

    # --- shortfall -----------------------------------------------------------
    out = []
    for u, e in erased.items():
        v = valid.get(u, 0.0)
        r = red.get(u, {"pts": 0.0, "n": 0, "first": "", "last": ""})
        shortfall = r["pts"] - v
        if shortfall > 0:
            out.append({
                "id_usuario": u,
                "shortfall": round(shortfall),
                "points_redeemed": round(r["pts"]),
                "points_valid": round(v),
                "points_erased": round(e["pts"]),
                "rows_erased": e["rows"],
                "redemptions": r["n"],
                "stores": len(e["stores"]),
                "first_invalid": e["first"] or "",
                "last_invalid": e["last"] or "",
                "first_redemption": r["first"] or "",
                "last_redemption": r["last"] or "",
            })
    out.sort(key=lambda d: -d["shortfall"])

    total = sum(d["shortfall"] for d in out)
    print(f"erased rows read      : {erased_rows:,}")
    print(f"users with erased rows: {len(erased):,}")
    if skipped_floor:
        print(f"floor rows excluded   : {skipped_floor:,} (>= 2026-09-17 19:00)")
    if unknown_tipo:
        print(f"unclassified tipo     : {unknown_tipo:,}  <-- check ACCRUAL/REDEMPTION")
    print(f"users underwater      : {len(out):,}   (expected 104)")
    print(f"points given away     : {total:,.0f}   (expected 27,198)")
    if len(out) != 104 or round(total) != 27198:
        print("MISMATCH vs remediation record - do not publish without reconciling")

    with open("zona_centro_unbacked_104.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()) if out else ["id_usuario"])
        w.writeheader()
        w.writerows(out)

    print()
    hdr = f"{'#':>4}  {'user':<38} {'short':>7} {'redeem':>7} {'valid':>7} {'erased':>7} {'red':>4} {'invalid window':<24}"
    print(hdr)
    print("-" * len(hdr))
    for i, d in enumerate(out, 1):
        print(f"{i:>4}  {d['id_usuario']:<38} {d['shortfall']:>7,} "
              f"{d['points_redeemed']:>7,} {d['points_valid']:>7,} "
              f"{d['points_erased']:>7,} {d['redemptions']:>4} "
              f"{d['first_invalid']} -> {d['last_invalid']}")


if __name__ == "__main__":
    main()
