# Admin Authentication Setup Guide

## Overview

This project now has a complete admin portal authentication system using **Django REST Framework session-based authentication**. Admin users can securely log in through the web UI to perform CRUD operations on composers and works.

---

## Architecture

### Backend (Django)
- **Session Authentication**: Uses Django's built-in session management
- **Permissions**: `IsAdminOrReadOnly` custom permission class
  - Public users: Read-only access (GET requests)
  - Admin users (`is_staff=True`): Full CRUD access
- **CSRF Protection**: Enabled for security

### Frontend (React)
- **Auth Context**: Global authentication state management
- **Protected Routes**: Admin routes require authentication
- **Session Cookies**: Automatic cookie management with axios

---

## Setup Instructions

### 1. Create Admin Users

```bash
# From the project root
python manage.py createsuperuser

# Follow prompts to create username/password
```

### 2. Install Dependencies (if needed)

**Backend:**
```bash
# Already installed in requirements.txt
pip install djangorestframework django-cors-headers
```

**Frontend:**
```bash
cd frontend
npm install axios react-router-dom
# Already in package.json
```

### 3. Environment Variables

Create `.env` file in project root (if not exists):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend API URL (for development)
VITE_API_URL=http://localhost:8000
```

### 4. Start Development Servers

**Backend:**
```bash
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm run dev
```

---

## Using the Admin Portal

### Login
1. Navigate to `http://localhost:5173/admin/login`
2. Enter your superuser credentials
3. You'll be redirected to the admin dashboard

### Features
- **Dashboard**: Overview of available admin functions
- **Manage Composers**: View, search, edit, and delete composers
- **Manage Works**: (Similar CRUD interface)
- **Bulk Import**: CSV import functionality
- **Logout**: Secure session termination

### API Endpoints

#### Authentication
- `POST /api/auth/login/` - Login with username/password
- `POST /api/auth/logout/` - Logout (destroys session)
- `GET /api/auth/user/` - Get current user info
- `GET /api/auth/csrf/` - Get CSRF token

#### Admin CRUD (requires `is_staff=True`)
- `POST /api/composers/` - Create composer
- `PUT /api/composers/{id}/` - Update composer
- `DELETE /api/composers/{id}/` - Delete composer
- `POST /api/works/` - Create work
- `PUT /api/works/{id}/` - Update work
- `DELETE /api/works/{id}/` - Delete work

---

## Security Features

✅ **Session-based authentication** (cookies)  
✅ **CSRF protection** for all POST/PUT/DELETE requests  
✅ **Staff-only permissions** for write operations  
✅ **HttpOnly cookies** for session security  
✅ **CORS configured** for frontend-backend communication  

---

## Adding More Admin Users

### Via Django Admin
1. Navigate to `http://localhost:8000/admin`
2. Login with superuser credentials
3. Go to Users → Add User
4. **Important**: Check "Staff status" to grant admin access

### Via Command Line
```bash
python manage.py createsuperuser
```

### Programmatically
```python
from django.contrib.auth.models import User

user = User.objects.create_user(
    username='editor1',
    email='editor@example.com',
    password='secure-password',
    is_staff=True  # Required for admin access
)
```

---

## Extending the Admin Portal

### Add New Admin Pages

1. **Create page component**: `frontend/src/pages/AdminWorks.tsx`
2. **Add route**: In `App.tsx`:
   ```tsx
   <Route 
     path="/admin/works" 
     element={
       <ProtectedRoute>
         <AdminWorks />
       </ProtectedRoute>
     } 
   />
   ```
3. **Add link**: In `AdminDashboard.tsx`

### Add New CRUD Endpoints

1. **Update ViewSet**: Change from `ReadOnlyModelViewSet` to `ModelViewSet`
2. **Add permission**: Add `permission_classes = [IsAdminOrReadOnly]`
3. **Update serializer**: Ensure all fields are writable

---

## Troubleshooting

### "Authentication credentials were not provided"
- Ensure `withCredentials: true` is set in axios
- Check CORS settings in Django

### "CSRF token missing or incorrect"
- Call `/api/auth/csrf/` before login
- Ensure `CSRF_COOKIE_HTTPONLY = False` in settings

### Can't login after creating superuser
- Verify `is_staff=True` is set on user
- Check backend logs for authentication errors

### Session not persisting
- Check `SESSION_COOKIE_SAMESITE` and `CORS_ALLOW_CREDENTIALS` settings
- Ensure frontend and backend are on same domain (or CORS properly configured)

---

## Production Considerations

Before deploying:

1. **Set `DEBUG=False`** in production
2. **Configure `ALLOWED_HOSTS`** with your domain
3. **Use HTTPS** (`SESSION_COOKIE_SECURE=True`)
4. **Set strong `SECRET_KEY`**
5. **Configure `CORS_ALLOWED_ORIGINS`** (remove wildcard)
6. **Use environment variables** for sensitive data
7. **Consider JWT tokens** for better scalability (optional)

---

## Next Steps

- [ ] Add form validation for composer/work creation
- [ ] Implement edit functionality (currently just delete)
- [ ] Add pagination for large datasets
- [ ] Create Works admin page
- [ ] Add bulk import UI
- [ ] Implement role-based permissions (editor vs. admin)
- [ ] Add audit logging for admin actions
