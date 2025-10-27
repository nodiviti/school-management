# API Testing with curl

## Base URL
```bash
export API_URL="https://schoolpro-6.preview.emergentagent.com/api"
```

## Health Check
```bash
curl $API_URL/health
```

## Authentication

### Register User
```bash
curl -X POST $API_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@school.com",
    "username": "admin",
    "password": "SecurePass123!",
    "first_name": "Admin",
    "last_name": "User",
    "role": "superadmin",
    "phone": "+1234567890"
  }'
```

### Login
```bash
RESPONSE=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@school.com",
    "password": "SecurePass123!"
  }')

export TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

### Get Current User
```bash
curl -H "Authorization: Bearer $TOKEN" $API_URL/auth/me
```

## Students Management

### Create Student
```bash
curl -X POST $API_URL/students \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-id-here",
    "student_number": "STU2024001",
    "date_of_birth": "2005-01-15",
    "gender": "male",
    "address": "123 Main St",
    "emergency_contact_name": "John Doe",
    "emergency_contact_phone": "+1234567890",
    "enrollment_date": "2024-09-01",
    "current_grade": "10"
  }'
```

### List Students
```bash
curl -H "Authorization: Bearer $TOKEN" "$API_URL/students?limit=10"
```

### Get Student by ID
```bash
curl -H "Authorization: Bearer $TOKEN" $API_URL/students/{student_id}
```

## Classes Management

### Create Class
```bash
curl -X POST $API_URL/classes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "10-A",
    "grade_level": "10",
    "section": "A",
    "academic_year": "2024-2025",
    "capacity": 40
  }'
```

### List Classes
```bash
curl -H "Authorization: Bearer $TOKEN" "$API_URL/classes?academic_year=2024-2025"
```

## Attendance

### Mark Attendance
```bash
curl -X POST $API_URL/attendance \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student-id-here",
    "class_id": "class-id-here",
    "date": "2024-10-27T08:00:00Z",
    "status": "present"
  }'
```

### Generate QR Code for Attendance
```bash
curl -H "Authorization: Bearer $TOKEN" "$API_URL/attendance/qr-code/{class_id}"
```

## Grades

### Create Grade
```bash
curl -X POST $API_URL/grades \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student-id-here",
    "subject_id": "subject-id-here",
    "class_id": "class-id-here",
    "assessment_type": "midterm",
    "assessment_name": "Midterm Exam",
    "score": 85,
    "max_score": 100,
    "academic_year": "2024-2025",
    "semester": "1",
    "date": "2024-10-27T00:00:00Z"
  }'
```

### Get Student Transcript
```bash
curl -H "Authorization: Bearer $TOKEN" "$API_URL/grades/transcript/{student_id}?academic_year=2024-2025"
```

## Finance

### Create Invoice
```bash
curl -X POST $API_URL/finance/invoices \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student-id-here",
    "academic_year": "2024-2025",
    "semester": "1",
    "items": [
      {"fee_type_id": "tuition", "amount": 5000000, "description": "Tuition Fee"}
    ],
    "subtotal": 5000000,
    "total_amount": 5000000,
    "due_date": "2024-11-30T00:00:00Z"
  }'
```

### Create Payment
```bash
curl -X POST $API_URL/finance/payments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "invoice-id-here",
    "student_id": "student-id-here",
    "amount": 5000000,
    "payment_method": "bank_transfer"
  }'
```

## Library

### Add Book
```bash
curl -X POST $API_URL/library/books \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "isbn": "978-0-123456-78-9",
    "title": "Introduction to Computer Science",
    "author": "John Smith",
    "publisher": "Tech Publishers",
    "category": "textbook",
    "total_copies": 5,
    "available_copies": 5
  }'
```

### Borrow Book
```bash
curl -X POST $API_URL/library/loans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": "book-id-here",
    "borrower_id": "user-id-here",
    "borrower_type": "student"
  }'
```

## Admin

### Get Dashboard Stats
```bash
curl -H "Authorization: Bearer $TOKEN" $API_URL/admin/dashboard
```

### Export Students Report
```bash
curl -H "Authorization: Bearer $TOKEN" \
  $API_URL/admin/reports/students/export \
  -o students_report.csv
```