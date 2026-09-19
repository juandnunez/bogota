#!/usr/bin/env python3
"""Generate an iOS hardening profile (.mobileconfig) for an unsupervised,
personally owned iPhone.

Separate from the APN/DNS profile so it can be removed independently.
Only uses restriction keys that Apple honors on non-supervised devices.

Usage:
    python3 make_hardening.py            # writes iPhone-Hardening.mobileconfig
    python3 make_hardening.py --check    # re-parses the written profile and prints it

Effects once installed:
  Passcode  : 6+ digits, no simple/repeating/sequential codes, required
              immediately on lock, auto-lock after 2 minutes idle.
  Lock screen: Control Center, Today view, Siri, and voice dialing are
              blocked while locked (stops an attacker toggling Airplane Mode
              to defeat Find My, or using Siri to leak data).
  TLS       : the "trust this certificate?" prompt is disabled, so a rogue
              hotspot cannot talk you into accepting a fake cert.
  Backups   : local (Finder/iTunes) backups must be encrypted.
  Telemetry : diagnostic submission off, ad tracking forced to limited.
  Safari    : fraudulent-website warning forced on.

No key here wipes the device on failed attempts.
"""
from __future__ import annotations

import argparse
import plistlib
import sys
from pathlib import Path

from make_profile import _uid

OUT = Path(__file__).with_name("iPhone-Hardening.mobileconfig")


def passcode_payload() -> dict:
    return {
        "PayloadType": "com.apple.mobiledevice.passwordpolicy",
        "PayloadVersion": 1,
        "PayloadIdentifier": "co.net.etb.hardening.passcode",
        "PayloadUUID": _uid("hardening-passcode"),
        "PayloadDisplayName": "Passcode policy",
        "forcePIN": True,
        "allowSimple": False,     # rejects 000000, 123456, repeating patterns
        "minLength": 6,
        "maxGracePeriod": 0,      # passcode required immediately after lock
        "maxInactivity": 2,       # minutes before auto-lock
    }


def restrictions_payload() -> dict:
    return {
        "PayloadType": "com.apple.applicationaccess",
        "PayloadVersion": 1,
        "PayloadIdentifier": "co.net.etb.hardening.restrictions",
        "PayloadUUID": _uid("hardening-restrictions"),
        "PayloadDisplayName": "Lock screen and network restrictions",
        # Lock-screen attack surface
        "allowLockScreenControlCenter": False,
        "allowLockScreenTodayView": False,
        "allowAssistantWhileLocked": False,
        "allowVoiceDialing": False,
        # Network / MITM
        "allowUntrustedTLSPrompt": False,
        "safariForceFraudWarning": True,
        # Data at rest / telemetry
        "forceEncryptedBackup": True,
        "allowDiagnosticSubmission": False,
        "forceLimitAdTracking": True,
    }


def build_profile() -> dict:
    return {
        "PayloadType": "Configuration",
        "PayloadVersion": 1,
        "PayloadIdentifier": "co.net.etb.hardening",
        "PayloadUUID": _uid("hardening-root"),
        "PayloadDisplayName": "iPhone Hardening",
        "PayloadDescription": (
            "Passcode policy, lock-screen lockdown, no untrusted-TLS prompt, "
            "encrypted backups, telemetry off."
        ),
        "PayloadOrganization": "Self-managed",
        "PayloadRemovalDisallowed": False,
        "PayloadContent": [passcode_payload(), restrictions_payload()],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="re-read the generated file and dump it")
    ap.add_argument("-o", "--out", type=Path, default=OUT)
    args = ap.parse_args(argv)

    profile = build_profile()
    with args.out.open("wb") as fh:
        plistlib.dump(profile, fh, sort_keys=False)
    print(f"wrote {args.out}")

    if args.check:
        with args.out.open("rb") as fh:
            back = plistlib.load(fh)
        assert [p["PayloadType"] for p in back["PayloadContent"]] == [
            "com.apple.mobiledevice.passwordpolicy",
            "com.apple.applicationaccess",
        ]
        print(plistlib.dumps(back, sort_keys=False).decode())
    return 0


if __name__ == "__main__":
    sys.exit(main())
