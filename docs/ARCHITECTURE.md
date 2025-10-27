# School Management System - Architecture Documentation

## System Overview

The School Management System is a comprehensive SaaS platform designed to manage all aspects of educational institutions, from student enrollment to financial management.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Clients                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Browser  │  │  Mobile  │  │   API    │  │   LMS    │   │
│  │   Web    │  │   App    │  │ Clients  │  │ (Moodle) │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer / Ingress                  │
│                         (NGINX)                              │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌──────────────────┐           ┌──────────────────┐
│   Frontend       │           │    Backend       │
│   (React)        │           │   (FastAPI)      │
│                  │           │                  │
│ - Authentication │           │ - REST API       │
│ - Role-based UI  │           │ - JWT Auth       │
│ - Dashboards     │           │ - RBAC           │
│ - Forms          │◄──────────┤ - Business Logic │
└──────────────────┘           └────────┬─────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
         ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
         │   PostgreSQL    │ │     Redis       │ │   MinIO/S3      │
         │   (Primary DB)  │ │   (Cache)       │ │  (Storage)      │
         │                 │ │                 │ │                 │
         │ - Users         │ │ - Sessions      │ │ - Documents     │
         │ - Students      │ │ - Tokens        │ │ - Images        │
         │ - Classes       │ │ - Query Cache   │ │ - Reports       │
         │ - Grades        │ │                 │ │                 │
         └─────────────────┘ └─────────────────┘ └─────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  External Integrations                       │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Payment  │  │   SMTP   │  │   SMS    │  │   LMS    │  │
│  │ Gateway  │  │ (Email)  │  │ (Twilio) │  │ (Moodle) │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy / Motor (MongoDB)
- **Authentication**: JWT with refresh tokens
- **Validation**: Pydantic v2
- **Task Queue**: Redis (optional: Celery/BullMQ)

### Frontend
- **Framework**: React 19
- **Routing**: React Router v7
- **Styling**: Tailwind CSS
- **Components**: Shadcn/UI
- **State Management**: React Context API
- **HTTP Client**: Axios

### Database
- **Primary**: PostgreSQL 17 (configurable: MongoDB)
- **Cache**: Redis 7
- **Storage**: MinIO (S3-compatible)

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana (optional)
- **Logging**: Structured JSON logs

## Data Models

### Core Entities

#### Users
```
users
├── id (UUID)
├── email (unique)
├── username (unique)
├── password_hash
├── role (enum: superadmin, admin, headmaster, teacher, student, parent, finance, staff, librarian)
├── first_name
├── last_name
├── phone
├── is_active
├── two_factor_enabled
└── timestamps
```

#### Students
```
students
├── id (UUID)
├── user_id (FK -> users)
├── student_number (unique)
├── date_of_birth
├── gender
├── address
├── emergency_contact
├── medical_info
├── enrollment_date
├── current_grade
├── current_class_id (FK -> classes)
└── status (active, inactive, graduated)
```

#### Classes
```
classes
├── id (UUID)
├── name
├── grade_level
├── section
├── academic_year
├── teacher_id (FK -> teachers)
├── room_number
├── capacity
└── student_ids (array)
```

#### Attendance
```
attendance
├── id (UUID)
├── student_id (FK -> students)
├── class_id (FK -> classes)
├── subject_id (FK -> subjects)
├── date
├── status (present, absent, late, excused)
├── qr_code_used
└── marked_by (FK -> users)
```

#### Grades
```
grades
├── id (UUID)
├── student_id (FK -> students)
├── subject_id (FK -> subjects)
├── class_id (FK -> classes)
├── assessment_type
├── score
├── max_score
├── percentage
├── grade_letter
├── academic_year
├── semester
└── teacher_id (FK -> teachers)
```

## API Architecture

### REST API Design

```
/api
├── /auth
│   ├── POST   /register
│   ├── POST   /login
│   ├── POST   /refresh
│   ├── POST   /logout
│   ├── POST   /enable-2fa
│   └── GET    /me
├── /users
│   ├── GET    /
│   ├── GET    /{id}
│   ├── PATCH  /{id}
│   └── DELETE /{id}
├── /students
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PATCH  /{id}
│   └── DELETE /{id}
├── /teachers
│   └── [CRUD operations]
├── /classes
│   └── [CRUD operations]
├── /subjects
│   └── [CRUD operations]
├── /attendance
│   ├── POST   /
│   ├── GET    /
│   ├── GET    /qr-code/{class_id}
│   └── POST   /qr-checkin
├── /grades
│   ├── POST   /
│   ├── GET    /
│   └── GET    /transcript/{student_id}
├── /finance
│   ├── POST   /invoices
│   ├── GET    /invoices
│   ├── POST   /payments
│   └── POST   /webhooks/payment
├── /dormitory
│   ├── POST   /
│   ├── GET    /
│   ├── POST   /rooms
│   └── POST   /allocations
├── /library
│   ├── POST   /books
│   ├── GET    /books
│   ├── POST   /loans
│   └── PATCH  /loans/{id}/return
└── /admin
    ├── GET    /dashboard
    ├── GET    /reports/students/export
    └── GET    /audit-logs
```

## Security Architecture

### Authentication Flow
```
1. User submits credentials → /auth/login
2. Backend validates credentials
3. Backend generates:
   - Access Token (JWT, 30 min expiry)
   - Refresh Token (JWT, 7 days expiry)
4. Frontend stores tokens
5. Frontend includes Access Token in all API requests
6. When Access Token expires → use Refresh Token to get new tokens
```

### Role-Based Access Control (RBAC)
```
Role Hierarchy:
superadmin → admin → headmaster → teacher/finance/staff → student/parent

Permissions Matrix:
┌──────────────┬─────────┬───────┬────────────┬─────────┬─────────┐
│ Resource     │ Super   │ Admin │ Headmaster │ Teacher │ Student │
├──────────────┼─────────┼───────┼────────────┼─────────┼─────────┤
│ Users        │ CRUD    │ CRUD  │ R          │ R       │ -       │
│ Students     │ CRUD    │ CRUD  │ CRUD       │ RU      │ R (own) │
│ Teachers     │ CRUD    │ CRUD  │ CRUD       │ R       │ -       │
│ Grades       │ CRUD    │ CRUD  │ RU         │ CRU     │ R (own) │
│ Finance      │ CRUD    │ CRUD  │ R          │ -       │ R (own) │
│ Reports      │ R       │ R     │ R          │ R       │ -       │
└──────────────┴─────────┴───────┴────────────┴─────────┴─────────┘
```

## Deployment Architecture

### Kubernetes Deployment
```yaml
Namespace: school-management

Services:
- frontend (2 replicas)
- backend (3 replicas)
- postgres (StatefulSet, 1 replica with PVC)
- redis (1 replica)
- minio (StatefulSet with PVC)

Ingress:
- TLS termination
- Path-based routing:
  /api/* → backend
  /* → frontend
```

### Scaling Strategy
```
Horizontal Pod Autoscaling (HPA):
- Backend: 3-10 replicas (CPU > 70%)
- Frontend: 2-5 replicas (CPU > 70%)

Vertical Scaling:
- Database: Increase PVC size as data grows
- Redis: Increase memory based on cache hit ratio
```

## Monitoring & Observability

### Metrics
```
Backend Metrics:
- Request rate (req/sec)
- Response time (p50, p95, p99)
- Error rate
- Database query time
- Cache hit ratio

Business Metrics:
- Active users
- Daily attendance rate
- Invoice generation rate
- Payment success rate
```

### Logging
```json
Structured Log Format:
{
  "timestamp": "2024-10-27T05:00:00Z",
  "level": "INFO",
  "logger": "server",
  "message": "Request completed",
  "method": "POST",
  "path": "/api/students",
  "status_code": 201,
  "duration_ms": 45.2,
  "user_id": "uuid",
  "ip": "192.168.1.1"
}
```

## Performance Optimization

### Caching Strategy
```
Redis Cache Layers:
1. Query Cache (TTL: 5 min)
   - Student lists
   - Class schedules
   - Subject lists

2. Session Cache (TTL: 30 min)
   - User sessions
   - JWT token blacklist

3. Object Cache (TTL: 1 hour)
   - User profiles
   - Configuration data
```

### Database Optimization
```
Indexes:
- users: (email), (username), (role)
- students: (user_id), (student_number), (status)
- attendance: (student_id, date), (class_id, date)
- grades: (student_id, academic_year)

Query Optimization:
- Use prepared statements
- Limit result sets with pagination
- Use database-side aggregations
- Implement read replicas for reporting
```

## Disaster Recovery

### Backup Strategy
```
PostgreSQL:
- Daily full backups (3 AM)
- WAL archiving (continuous)
- Retention: 30 days

Files (MinIO):
- Daily snapshots
- Replication to S3 (optional)
- Retention: 90 days

Redis:
- RDB snapshots every 6 hours
- AOF for durability
```

### Recovery Procedures
```
1. Database failure:
   - Promote read replica to primary
   - Restore from latest backup if needed
   
2. Application failure:
   - Kubernetes auto-restart pods
   - Manual intervention if persistent
   
3. Complete datacenter failure:
   - Failover to secondary region (if multi-region)
   - Restore from geo-replicated backups
```

## Future Enhancements

1. **Real-time Features**
   - WebSocket for live attendance
   - Push notifications
   - Live chat support

2. **Advanced Analytics**
   - ML-based student performance prediction
   - Attendance trend analysis
   - Financial forecasting

3. **Mobile Applications**
   - Native iOS/Android apps
   - Offline-first architecture
   - Biometric authentication

4. **Integration Ecosystem**
   - More LMS platforms (Canvas, Blackboard)
   - Video conferencing (Zoom, Teams)
   - Parent communication platforms

---

**Document Version**: 1.0  
**Last Updated**: October 2024  
**Maintained by**: Development Team