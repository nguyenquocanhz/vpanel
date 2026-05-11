"""
VPS Panel - RSA Keypair Generator
Run ONCE to generate keys. Keep private_key.pem SECRET.
Usage: python generate_keys.py
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pathlib import Path
import sys

def generate_keypair(bits=4096):
    """Generate RSA keypair and save to files."""
    output_dir = Path(__file__).parent
    priv_path = output_dir / "private_key.pem"
    pub_path_tools = output_dir / "public_key.pem"
    pub_path_agent = output_dir.parent / "agent" / "license" / "public_key.pem"

    if priv_path.exists():
        confirm = input("⚠ private_key.pem already exists. Overwrite? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)

    print(f"Generating {bits}-bit RSA keypair...")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
    public_key = private_key.public_key()

    # Save private key
    with open(priv_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    print(f"✓ Private key saved: {priv_path}")
    print("  ⚠ NEVER distribute this file!")

    # Save public key (tools copy)
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(pub_path_tools, "wb") as f:
        f.write(pub_bytes)
    print(f"✓ Public key saved: {pub_path_tools}")

    # Save public key (agent copy)
    pub_path_agent.parent.mkdir(parents=True, exist_ok=True)
    with open(pub_path_agent, "wb") as f:
        f.write(pub_bytes)
    print(f"✓ Public key copied to agent: {pub_path_agent}")
    print("\n🎉 Keypair generated! Now use license_generator.py to create licenses.")

if __name__ == "__main__":
    generate_keypair()
