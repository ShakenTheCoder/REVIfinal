# REVI Deployment Guide

This guide covers deploying REVI to production environments.

## 🐳 Docker Deployment (Recommended)

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM
- 20GB+ disk space
- Domain name (optional)

### Step 1: Clone and Configure

```bash
git clone <repository-url>
cd revi
cp .env.example .env
```

### Step 2: Configure Environment Variables

Edit `.env` file:

```env
# Production Database
DATABASE_URL=postgresql://revi_user:STRONG_PASSWORD_HERE@postgres:5432/revi_db

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email (optional, for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Step 3: Update docker-compose.yml for Production

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: revi_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: revi_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: always
    networks:
      - revi-network

  backend:
    build: ./backend
    environment:
      DATABASE_URL: ${DATABASE_URL}
    depends_on:
      - postgres
    restart: always
    networks:
      - revi-network

  frontend:
    build: ./frontend
    depends_on:
      - backend
    restart: always
    networks:
      - revi-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: always
    networks:
      - revi-network

networks:
  revi-network:
    driver: bridge

volumes:
  postgres_data:
```

### Step 4: SSL Configuration

1. Obtain SSL certificate (Let's Encrypt recommended):
   ```bash
   sudo apt-get install certbot
   sudo certbot certonly --standalone -d yourdomain.com
   ```

2. Copy certificates:
   ```bash
   mkdir -p nginx/ssl
   sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
   sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
   ```

### Step 5: Deploy

```bash
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
docker-compose up -d --build
```

## 🔧 Manual Deployment

### Backend Setup

1. **Install Python 3.11+**
   ```bash
   sudo apt-get update
   sudo apt-get install python3.11 python3.11-venv python3-pip
   ```

2. **Create virtual environment**
   ```bash
   cd backend
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/revi_db"
   ```

5. **Run with Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
   ```

### Frontend Setup

1. **Install Node.js 20+**
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

2. **Build frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

3. **Serve with nginx**
   ```bash
   sudo cp -r dist/* /var/www/revi/
   ```

### Database Setup

1. **Install PostgreSQL**
   ```bash
   sudo apt-get install postgresql postgresql-contrib
   ```

2. **Create database and user**
   ```sql
   sudo -u postgres psql
   CREATE DATABASE revi_db;
   CREATE USER revi_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE revi_db TO revi_user;
   \q
   ```

3. **Initialize schema**
   ```bash
   psql -U revi_user -d revi_db -f database/init.sql
   ```

## 🔒 Security Checklist

- [ ] Change default database passwords
- [ ] Enable SSL/TLS
- [ ] Configure firewall (UFW)
- [ ] Set up fail2ban
- [ ] Implement rate limiting
- [ ] Enable CORS only for specific origins
- [ ] Add authentication to admin endpoints
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor logs for suspicious activity

## 📊 Monitoring

### Health Checks

- Backend: `curl http://localhost:8000/health`
- Database: `pg_isready -h localhost -U revi_user`

### Logging

1. **Application logs**
   ```bash
   docker-compose logs -f backend
   ```

2. **Database logs**
   ```bash
   docker-compose logs -f postgres
   ```

3. **Setup log rotation**
   ```bash
   sudo nano /etc/logrotate.d/revi
   ```

   Add:
   ```
   /var/log/revi/*.log {
       daily
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 www-data www-data
       sharedscripts
   }
   ```

## 🔄 Updates and Maintenance

### Update Application

```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

### Database Backup

```bash
docker exec revi-postgres pg_dump -U revi_user revi_db > backup_$(date +%Y%m%d).sql
```

### Database Restore

```bash
docker exec -i revi-postgres psql -U revi_user revi_db < backup_20240101.sql
```

## 🚀 Performance Optimization

### Backend

1. **Enable caching**
   - Redis for session storage
   - Cache AI model predictions

2. **Database optimization**
   - Add indexes for frequently queried columns
   - Use connection pooling

3. **AI Model optimization**
   - Use quantized models for faster inference
   - Batch process reviews
   - Consider GPU acceleration

### Frontend

1. **Enable compression**
   ```nginx
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   ```

2. **Cache static assets**
   ```nginx
   location /static/ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

## 🐛 Troubleshooting

### Backend won't start

```bash
docker-compose logs backend
# Check for port conflicts, database connection issues
```

### Database connection failed

```bash
docker exec -it revi-postgres psql -U revi_user -d revi_db
# Verify database is accessible
```

### AI models not loading

```bash
# Increase Docker memory limit
# Edit ~/.docker/daemon.json
{
  "memory": "8g"
}
```

### Frontend can't reach backend

```bash
# Check nginx configuration
docker exec -it revi-frontend cat /etc/nginx/conf.d/default.conf
```

## 📞 Support

For production deployment support, please contact your DevOps team or open an issue in the repository.

---

**Note**: This is a demonstration system. For production use, additional security hardening and scalability considerations are required.
