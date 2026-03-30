FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    openssh-client \
    curl \
    net-tools \
    iputils-ping \
    iproute2 \
    dnsutils \
    vim \
    wget \
    docker.io \
    apt-transport-https \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | \
    gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /" \
    > /etc/apt/sources.list.d/kubernetes.list && \
    apt-get update && apt-get install -y kubectl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app/ .

RUN echo "================================================" > /DISCLAIMER && \
    echo "  THIS IMAGE IS FOR SECURITY EXERCISE ONLY" >> /DISCLAIMER && \
    echo "  Bu imaj yalnizca guvenlik tatbikati icindir." >> /DISCLAIMER && \
    echo "  Yetkisiz kullanim yasaktir." >> /DISCLAIMER && \
    echo "================================================" >> /DISCLAIMER

EXPOSE 8080

CMD ["python3", "server.py"]
