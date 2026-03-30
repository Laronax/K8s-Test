# K8s Pentest Exercise Toolkit

> **Intentionally Vulnerable** -- Built for authorized red team exercises only.

## Legal Disclaimer

```
THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
USE OR OTHER DEALINGS IN THE SOFTWARE.

THIS TOOLKIT CONTAINS INTENTIONALLY VULNERABLE COMPONENTS DESIGNED SOLELY
FOR AUTHORIZED SECURITY TESTING, EDUCATION, AND RED TEAM / BLUE TEAM
EXERCISES. BY USING THIS SOFTWARE, YOU ACKNOWLEDGE AND AGREE THAT:

1. You have obtained proper written authorization before deploying this
   toolkit in any environment.
2. You assume full responsibility for any consequences resulting from the
   use or misuse of this software.
3. The authors are not responsible for any damage, data loss, unauthorized
   access, or legal consequences arising from the use of this toolkit.
4. This software must NOT be deployed in production environments, public-
   facing networks, or any system without explicit authorization from the
   system owner.
5. Unauthorized use of this toolkit may violate local, state, national,
   and international laws including but not limited to the Computer Fraud
   and Abuse Act (CFAA), General Data Protection Regulation (GDPR), and
   equivalent legislation in your jurisdiction.
6. You are solely responsible for ensuring compliance with all applicable
   laws and regulations.

USE AT YOUR OWN RISK.
```

## What Is This?

A deliberately vulnerable container toolkit designed to test SOC (Security Operations Center) team detection and response capabilities on **Google Anthos (on-prem) Kubernetes** clusters. It provides:

- An **encrypted interactive web shell** (AES-256-GCM) running inside a container
- Two distinct **container escape scenarios** for red team exercises
- Pre-built **Kubernetes manifests** with intentional security misconfigurations

| Scenario | Vector | Compose File |
|----------|--------|--------------|
| 1 -- Privileged | `privileged: true` grants full host access | `docker-compose-privileged.yml` |
| 2 -- Socket | Docker socket mount enables spawning host-level containers | `docker-compose-socket.yml` |

## Vulnerabilities by Design

| Category | Detail | Risk |
|----------|--------|------|
| Web Shell | Remote command execution via encrypted HTTP channel | Critical |
| Privileged Container | Full host device/namespace access | Critical |
| Docker Socket Mount | Ability to create arbitrary containers on the host | Critical |
| RBAC | `cluster-admin` bound to pod ServiceAccount | Critical |
| Hardcoded Key | AES key embedded in frontend JavaScript source | High |
| Root User | Container runs as root (UID 0) | High |
| hostPID / hostNetwork | Pod shares host PID and network namespace | High |

## Prerequisites

- Docker & Docker Compose
- kubectl configured for your Anthos cluster
- Google Anthos on-prem cluster (or any local Kubernetes cluster)

## Quick Start

### Build the Image

```bash
docker build -t pentest-webshell:latest .
```

### Scenario 1 -- Privileged Container

```bash
docker compose -f docker-compose-privileged.yml up -d
```

### Scenario 2 -- Docker Socket Mount

```bash
docker compose -f docker-compose-socket.yml up -d
```

### Access the Web Shell

Open `http://<HOST_IP>:8080` in a browser. All command input/output is AES-256-GCM encrypted over HTTP.

## Kubernetes Deployment (Anthos)

```bash
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/rbac.yml

# Choose one scenario:
kubectl apply -f k8s/deployment-privileged.yml   # Scenario 1
kubectl apply -f k8s/deployment-socket.yml        # Scenario 2
```

Web shell is accessible at `http://<NODE_IP>:30080`.

## Encryption

All shell I/O is encrypted in transit using **AES-256-GCM** (authenticated encryption). The key is intentionally hardcoded in the frontend JavaScript -- this is a deliberate weakness for the exercise. SOC analysts inspecting browser traffic or source code should be able to extract it.

| Component | Implementation |
|-----------|---------------|
| Frontend | Web Crypto API (native browser) |
| Backend | PyCryptodome (Python) |
| Key Size | 256-bit (32 bytes, 64 hex chars) |
| Nonce | 12 bytes, randomly generated per request |
| Format | `{"nonce": "<b64>", "ciphertext": "<b64>", "tag": "<b64>"}` |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBSHELL_AES_KEY` | (hardcoded) | 64 hex character AES-256 key |
| `WEBSHELL_HOST` | `0.0.0.0` | Listen address |
| `WEBSHELL_PORT` | `8080` | Listen port |
| `WEBSHELL_SHELL` | `/bin/bash` | Shell binary |
| `WEBSHELL_TIMEOUT` | `30` | Command timeout in seconds |

## Cleanup

**Remove all resources immediately after the exercise.**

### Docker Compose

```bash
docker compose -f docker-compose-privileged.yml down
docker compose -f docker-compose-socket.yml down
docker rmi pentest-webshell:latest
```

### Kubernetes

```bash
kubectl delete -f k8s/deployment-privileged.yml
kubectl delete -f k8s/deployment-socket.yml
kubectl delete -f k8s/rbac.yml
kubectl delete -f k8s/service.yml
```

## Project Structure

```
├── Dockerfile                         # Ubuntu 22.04 + kubectl + ssh + web shell
├── docker-compose-privileged.yml      # Scenario 1: Privileged container escape
├── docker-compose-socket.yml          # Scenario 2: Docker socket mount escape
├── k8s/
│   ├── deployment-privileged.yml      # Privileged pod (hostPID, hostNetwork)
│   ├── deployment-socket.yml          # Docker socket hostPath mount
│   ├── service.yml                    # Namespace + NodePort (30080)
│   └── rbac.yml                       # ServiceAccount + cluster-admin binding
├── app/
│   ├── server.py                      # Flask backend (AES-256-GCM + subprocess)
│   ├── requirements.txt               # Python dependencies
│   └── templates/
│       └── index.html                 # Terminal UI (Web Crypto API)
├── senaryo.md                         # Attack scenarios & usage guide (Turkish)
└── README.md                          # This file
```

## Warning

> **Do NOT leave this toolkit running in any environment after the exercise is complete.**
> It contains critical vulnerabilities that provide full host and cluster access.
> Ensure all containers, pods, services, and RBAC bindings are removed immediately.

## License

This project is provided for educational and authorized security testing purposes only. No license is granted for malicious use.
