#!/usr/bin/env python3
"""Generate an iOS configuration profile (.mobileconfig) that pins the ETB
Colombia LTE APN on an iPhone.

Usage:
    python3 make_profile.py            # writes ETB-LTE.mobileconfig next to this file
    python3 make_profile.py --check    # re-parses the written profile and prints it

Install: AirDrop / email the .mobileconfig to the iPhone, open it, then
Settings > General > VPN & Device Management > ETB LTE (Colombia) > Install.
"""
from __future__ import annotations

import argparse
import plistlib
import sys
import uuid
from pathlib import Path

APN = "internetmovil.etb.net.co"          # current ETB data APN, no user/pass
LEGACY_APN = "moviletb.net.co"            # older ETB APN, user "etb" / pass "etb"
MCC, MNC = "732", "187"                   # ETB PLMN (Colombia)

OUT = Path(__file__).with_name("ETB-LTE.mobileconfig")

# Namespace-derived UUIDs keep the profile identity stable across regenerations
# so re-installing replaces the old copy instead of stacking a duplicate.
_NS = uuid.UUID("6f1c3a52-3b5e-4e3d-9a2a-0c5e7b1d2e44")


def _uid(name: str) -> str:
    return str(uuid.uuid5(_NS, name)).upper()


DNS_PROVIDERS = {
    "cloudflare": {
        "url": "https://cloudflare-dns.com/dns-query",
        "addresses": ["1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001"],
    },
    "quad9": {
        "url": "https://dns.quad9.net/dns-query",
        "addresses": ["9.9.9.9", "149.112.112.112", "2620:fe::fe", "2620:fe::9"],
    },
}


def dns_payload(provider: str) -> dict:
    """DNS-over-HTTPS payload (iOS 14+). Applies on cellular and Wi-Fi."""
    p = DNS_PROVIDERS[provider]
    return {
        "PayloadType": "com.apple.dnsSettings.managed",
        "PayloadVersion": 1,
        "PayloadIdentifier": f"co.net.etb.lte.dns.{provider}",
        "PayloadUUID": _uid(f"dns-{provider}"),
        "PayloadDisplayName": f"Encrypted DNS ({provider})",
        "PayloadDescription": "Pins DNS-over-HTTPS instead of carrier DNS.",
        "DNSSettings": {
            "DNSProtocol": "HTTPS",
            "ServerURL": p["url"],
            "ServerAddresses": p["addresses"],
        },
        "ProhibitDisablement": False,
    }


def build_profile(apn: str = APN, legacy: bool = False, dns: str | None = None) -> dict:
    apn_entry: dict = {
        "Name": apn,
        "AuthenticationType": "PAP",
        # 3 = IPv4 + IPv6 (bitmask: 1 = IPv4, 2 = IPv6)
        "AllowedProtocolMask": 3,
        "AllowedProtocolMaskInRoaming": 3,
        "AllowedProtocolMaskInDomesticRoaming": 3,
    }
    if legacy:
        apn_entry["Username"] = "etb"
        apn_entry["Password"] = "etb"

    attach_entry = {k: v for k, v in apn_entry.items()
                    if k in ("Name", "AuthenticationType", "Username", "Password")}

    cellular_payload = {
        "PayloadType": "com.apple.cellular",
        "PayloadVersion": 1,
        "PayloadIdentifier": "co.net.etb.lte.cellular",
        "PayloadUUID": _uid("cellular"),
        "PayloadDisplayName": "ETB APN",
        "PayloadDescription": f"Data APN {apn} for ETB (PLMN {MCC}{MNC}).",
        "AttachAPN": attach_entry,
        "APNs": [apn_entry],
    }

    content = [cellular_payload]
    if dns:
        content.append(dns_payload(dns))

    return {
        "PayloadType": "Configuration",
        "PayloadVersion": 1,
        "PayloadIdentifier": "co.net.etb.lte",
        "PayloadUUID": _uid("root"),
        "PayloadDisplayName": "ETB LTE (Colombia)",
        "PayloadDescription": "Sets the ETB mobile-data APN so LTE data works on iPhone.",
        "PayloadOrganization": "ETB (self-managed)",
        "PayloadRemovalDisallowed": False,
        "PayloadContent": content,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--legacy", action="store_true",
                    help=f"use legacy APN {LEGACY_APN} with etb/etb credentials")
    ap.add_argument("--dns", choices=sorted(DNS_PROVIDERS), default=None,
                    help="also pin encrypted DNS (DoH) to this provider")
    ap.add_argument("--check", action="store_true",
                    help="re-read the generated file and dump it")
    ap.add_argument("-o", "--out", type=Path, default=OUT)
    args = ap.parse_args(argv)

    profile = build_profile(LEGACY_APN if args.legacy else APN,
                            legacy=args.legacy, dns=args.dns)
    with args.out.open("wb") as fh:
        plistlib.dump(profile, fh, sort_keys=False)
    print(f"wrote {args.out}")

    if args.check:
        with args.out.open("rb") as fh:
            back = plistlib.load(fh)
        assert back["PayloadContent"][0]["APNs"][0]["Name"] == profile["PayloadContent"][0]["APNs"][0]["Name"]
        print(plistlib.dumps(back, sort_keys=False).decode())
    return 0


if __name__ == "__main__":
    sys.exit(main())
