"""
VPS Panel - License Generator
Run on DEVELOPER machine only. Creates signed license files.
Usage: python license_generator.py --customer "Company" --hardware-id "abc123..." --days 365
"""

import json
import base64
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

PRIVATE_KEY_PATH = Path(__file__).parent / "private_key.pem"


def generate_license(customer: str, hardware_id: str, days: int = 365,
                     features: list = None, max_servers: int = 1, output: str = None):
    """Generate a signed license file."""
    if not PRIVATE_KEY_PATH.exists():
        print("❌ private_key.pem not found! Run generate_keys.py first.")
        return

    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    if features is None:
        features = ["monitoring", "partition", "remote_restart", "services", "processes"]

    now = datetime.now(timezone.utc)
    license_data = {
        "customer": customer,
        "hardware_id": hardware_id,
        "issued_at": now.strftime("%Y-%m-%d"),
        "expires_at": (now + timedelta(days=days)).strftime("%Y-%m-%d"),
        "features": features,
        "max_servers": max_servers,
    }

    # Sign the data
    data_bytes = json.dumps(license_data, sort_keys=True, separators=(",", ":")).encode()
    signature = private_key.sign(
        data_bytes,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )

    license_data["signature"] = base64.b64encode(signature).decode()

    # Save license file
    output_path = Path(output) if output else Path(__file__).parent / "license.lic"
    with open(output_path, "w") as f:
        json.dump(license_data, f, indent=2)

    print(f"✅ License generated: {output_path}")
    print(f"   Customer: {customer}")
    print(f"   Hardware ID: {hardware_id[:16]}...")
    print(f"   Expires: {license_data['expires_at']}")
    print(f"   Features: {', '.join(features)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VPS Panel License Generator")
    parser.add_argument("--customer", "-c", required=True, help="Customer name")
    parser.add_argument("--hardware-id", "-hw", required=True, help="Server hardware ID (from /api/license/hardware)")
    parser.add_argument("--days", "-d", type=int, default=365, help="License validity in days (default: 365)")
    parser.add_argument("--features", "-f", nargs="+", default=None, help="Feature list")
    parser.add_argument("--max-servers", "-m", type=int, default=1, help="Max servers allowed")
    parser.add_argument("--output", "-o", default=None, help="Output file path")
    args = parser.parse_args()
    generate_license(args.customer, args.hardware_id, args.days, args.features, args.max_servers, args.output)
