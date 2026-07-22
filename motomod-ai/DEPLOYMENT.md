# MotoMod AI — Production Deployment Guide

This guide outlines deployment patterns, security configurations, and monitoring topologies to scale MotoMod AI in a cloud production environment.

---

## 1. Nginx Gateway Configuration
Deploy Nginx as the primary reverse proxy and SSL terminator. Place the following block under `/etc/nginx/sites-available/motomod`:

```nginx
server {
    listen 80;
    server_name api.motomod.ai;

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name api.motomod.ai;

    ssl_certificate /etc/letsencrypt/live/api.motomod.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.motomod.ai/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSockets for real-time build updates
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## 2. Production Docker Stack (`docker-compose.prod.yml`)
To build and deploy in production, use the production compose override:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## 3. Database Maintenance and Backups
Configure a cron task to dump database backups to MinIO/S3 daily:

```bash
0 2 * * * pg_dump -U motomod -d motomod_ai | gzip > /backups/db_$(date +\%F).sql.gz
```

---

## 4. Scaling Policies
- **API Backend**: Horizontal scaling (HPA) using Kubernetes with CPU utilization target of **75%**.
- **Celery Workers**: Scale worker instances independently depending on the queue size (e.g. scale prediction workers under heavy compute load).
