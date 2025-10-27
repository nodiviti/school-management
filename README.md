# README - School Management System

## 🏫 Comprehensive School Management System

A production-ready, full-featured school management system built with modern technologies.

### ✨ Features

- **Authentication & Authorization**: JWT-based with refresh tokens, 2FA support, RBAC
- **Student Management**: Complete student lifecycle from admission to graduation
- **Teacher & Staff Management**: Employee records, qualifications, schedules
- **Academic Management**: Classes, subjects, curriculum, timetables
- **Attendance System**: QR code check-in, manual marking, reports
- **Grades & Assessments**: Gradebook, transcripts, report cards
- **Finance Management**: Invoicing, payments, expense tracking
- **Dormitory Management**: Room allocation, check-in/out
- **Library Management**: Book cataloging, borrowing, fines
- **LMS Integration**: Moodle sync (configurable)
- **Multi-Gateway Payments**: Midtrans, Xendit, Stripe, Bayarind
- **Object Storage**: MinIO, S3, GCS, Azure Blob support
- **Reporting & Analytics**: Dashboard, exports (PDF, CSV, Excel)
- **Audit Logging**: Complete activity tracking

### 🛠️ Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL 17 / MongoDB (configurable)
- Redis (caching & sessions)
- SQLAlchemy / Motor (database adapters)

**Frontend:**
- React 19
- React Router v7
- Tailwind CSS
- Shadcn/UI components
- Axios

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL, Redis, MinIO
- NGINX (reverse proxy)

### 🚀 Quick Start

#### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

#### 1. Clone and Setup

```bash
git clone <repository-url>
cd school-management-system

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

#### 2. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

#### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/api/docs
- **MinIO Console**: http://localhost:9001
- **MailHog**: http://localhost:8025
- **pgAdmin**: http://localhost:5050

### 📦 Development Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (if using PostgreSQL)
# alembic upgrade head

# Start development server
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

#### Frontend

```bash
cd frontend

# Install dependencies
yarn install

# Start development server
yarn start
```

### 🔧 Configuration

#### Database Selection

In `.env`:

```env
# For PostgreSQL
DATABASE_TYPE=postgresql
POSTGRES_URL=postgresql://user:password@localhost:5432/school_db

# For MongoDB
DATABASE_TYPE=mongodb
MONGO_URL=mongodb://localhost:27017
DB_NAME=school_db
```

#### Payment Gateway

```env
# Select gateway
PAYMENT_GATEWAY=midtrans  # midtrans | xendit | stripe | bayarind

# Add respective credentials
MIDTRANS_SERVER_KEY=your-key
MIDTRANS_CLIENT_KEY=your-key
```

#### Object Storage

```env
# Select provider
STORAGE_PROVIDER=minio  # minio | s3 | gcs | azure

# Add respective credentials
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
yarn test
```

### 📊 API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8001/api/docs
- ReDoc: http://localhost:8001/api/redoc

### 🔐 Default Credentials

Create a superadmin user:

```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@school.com",
    "username": "admin",
    "password": "SecurePass123!",
    "first_name": "Admin",
    "last_name": "User",
    "role": "superadmin"
  }'
```

### 📝 User Roles

1. **Superadmin**: Full system access
2. **Admin**: School administration
3. **Headmaster**: Academic oversight
4. **Teacher**: Teaching & grading
5. **Student**: Student portal access
6. **Parent**: View child's information
7. **Finance**: Financial management
8. **Staff**: General staff access
9. **Librarian**: Library management

### 🎯 Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Current user

#### Students
- `GET /api/students` - List students
- `POST /api/students` - Create student
- `GET /api/students/{id}` - Get student
- `PATCH /api/students/{id}` - Update student

#### Attendance
- `POST /api/attendance` - Mark attendance
- `GET /api/attendance/qr-code/{class_id}` - Generate QR
- `POST /api/attendance/qr-checkin` - QR check-in

#### Finance
- `POST /api/finance/invoices` - Create invoice
- `POST /api/finance/payments` - Process payment
- `POST /api/finance/webhooks/payment` - Payment webhook

### 🔄 LMS Integration (Moodle)

Enable in `.env`:

```env
LMS_ENABLED=true
LMS_PROVIDER=moodle
MOODLE_URL=https://your-moodle.com
MOODLE_TOKEN=your-webservice-token
LMS_SYNC_MODE=push  # push | pull | bidirectional
```

### 📈 Monitoring

```bash
# Health check
curl http://localhost:8001/api/health

# Readiness check
curl http://localhost:8001/api/ready
```

### 🐛 Troubleshooting

#### Database connection issues
```bash
# Check PostgreSQL
docker-compose logs postgres

# Check if database is accessible
docker-compose exec postgres psql -U schooladmin -d school_management_db
```

#### Redis connection issues
```bash
docker-compose logs redis
docker-compose exec redis redis-cli ping
```

### 📄 License

MIT License

### 🤝 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ for educational institutions worldwide**