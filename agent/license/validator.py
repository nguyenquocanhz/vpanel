"""
VPS Panel - License Validator
Verifies RSA-signed license files against public key.
"""

import json
import base64
import os
from datetime import datetime, timezone
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from agent.license.hardware_id import get_hardware_id
from agent.config import settings

# Public key is embedded in the agent
PUBLIC_KEY_PATH = Path(__file__).parent / "public_key.pem"


class LicenseError(Exception):
    """Raised when license validation fails."""
    pass


class LicenseInfo:
    """Parsed and validated license information."""

    def __init__(self, data: dict):
        self.customer = data.get("customer", "Unknown")
        self.hardware_id = data.get("hardware_id", "")
        self.issued_at = data.get("issued_at", "")
        self.expires_at = data.get("expires_at", "")
        self.features = data.get("features", [])
        self.max_servers = data.get("max_servers", 1)
        self.is_valid = True

    def to_dict(self) -> dict:
        return {
            "customer": self.customer,
            "hardware_id": self.hardware_id[:12] + "...",  # Partial display
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "features": self.features,
            "max_servers": self.max_servers,
            "is_valid": self.is_valid,
        }


def validate_license(license_path: str = None) -> LicenseInfo:
    """
    Validate license file:
    1. Read and parse license.lic
    2. Verify RSA signature with public key
    3. Compare hardware_id with current machine
    4. Check expiration date
    """
    license_path = license_path or settings["license"]["license_file"]

    # Step 1: Read license file
    if not os.path.exists(license_path):
        raise LicenseError("License file not found. Please install a valid license.")

    try:
        with open(license_path, "r") as f:
            license_data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise LicenseError(f"Invalid license file format: {e}")

    # Extract signature and data
    signature_b64 = license_data.pop("signature", None)
    if not signature_b64:
        raise LicenseError("License file is missing signature")

    # Step 2: Verify RSA signature
    if not PUBLIC_KEY_PATH.exists():
        raise LicenseError("Public key not found. Agent installation may be corrupted.")

    try:
        with open(PUBLIC_KEY_PATH, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        # Recreate the signed data (sorted JSON without signature)
        data_bytes = json.dumps(license_data, sort_keys=True, separators=(",", ":")).encode()
        signature = base64.b64decode(signature_b64)

        public_key.verify(
            signature,
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except Exception as e:
        raise LicenseError(f"License signature verification failed: {e}")

    # Step 3: Verify hardware ID
    current_hw_id = get_hardware_id()
    if license_data.get("hardware_id") != current_hw_id:
        raise LicenseError(
            "License is bound to different hardware. "
            f"Expected: {license_data.get('hardware_id', '')[:12]}..., "
            f"Current: {current_hw_id[:12]}..."
        )

    # Step 4: Check expiration
    expires_at = license_data.get("expires_at", "")
    if expires_at:
        try:
            expiry_date = datetime.fromisoformat(expires_at).replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expiry_date:
                raise LicenseError(f"License expired on {expires_at}")
        except ValueError:
            raise LicenseError("Invalid expiration date format in license")

    # All checks passed
    return LicenseInfo(license_data)


def get_license_status() -> dict:
    """Get current license status (for dashboard display)."""
    try:
        info = validate_license()
        return {
            "valid": True,
            "info": info.to_dict(),
            "error": None,
        }
    except LicenseError as e:
        return {
            "valid": False,
            "info": None,
            "error": str(e),
        }
