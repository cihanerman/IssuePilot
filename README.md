# GitHub Issue Tracker

This is a Django application that tracks GitHub issues.

## Prerequisites

Before running the application, make sure you have the following installed:

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:

    ```bash
    git clone https://github.com/cihanerman/IssuePilot.git
    ```

2. Navigate to the project directory:

    ```bash
    cd IssuePilot
    ```

3. Build and run the Docker containers:

    ```bash
    docker-compose up -d --build
    ```

    
# Business Requirements

Github Issue Takip Sistemi
Kullanıcıların istedikleri Github repolarının issue'larını takip etmelerini sağlayan bir proje.
Kullanıcı tarafından belirtilen repoda yeni bir issue açıldığında veya mevcut bir issue'un durumu güncellendiğinde, kullanıcıya bir e-posta gönderilmelidir. Ayrıca istenilen repo için API üzerinden issue'ların geçmişini de görebilmelidir.
Adımlar:
1. Kullanıcı öncelikle Github reposunu takip eder. Kullanıcı birden fazla repo'yu takip edebilir. 2. Kullanıcının belirttiği repo Github'da mevcutsa, sistem bunu kaydeder.
3. Saatte bir Github kontrol mekanizması yazılır.
4. Herhangi bir issue'da bir güncelleme olduğunda, kullanıcıya e-posta gönderilir.
Kullanılacak Teknolojiler:
- Django / Fastapi - Docker
- PostgreSQL
- Celery
- Redis
- MailHog - Pytest