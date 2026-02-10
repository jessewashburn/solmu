# Simplified Admin Portal - User Suggestions System

## Overview

A streamlined admin portal that allows:
- **Public users** to submit suggestions (no login required)
- **Single admin** to review and manage suggestions via hyperlink
- **Environment-based authentication** - credentials stored securely in .env file (not committed to git)

---

## What Was Built

### Backend (Django)
✅ **UserSuggestion Model** - stores user feedback/suggestions  
✅ **Environment-based Admin Auth** - credentials in .env (never committed)  
✅ **API Endpoints** - RESTful API for suggestions (CRUD + approve/reject/merge)  
✅ **Session-based Auth** - secure login with session cookies  

### Frontend (React)  
✅ **Public Suggestion Form** (`/suggest`) - anyone can submit  
✅ **Admin Review UI** (`/admin`) - filter, view, approve, reject, merge  
✅ **Simple Login** (`/admin/login`) - hardcoded credentials  

---

## Quick Start

### 1. Configure Admin Credentials

The admin password is stored in `.env` file (not in git):

```bash
# Copy example file
cp .env.example .env

# Edit .env and set your admin password
# ADMIN_USERNAME=admin
# ADMIN_PASSWORD=your-secure-password-here
```

**Your password is in the `.env` file** - check `ADMIN_PASSWORD` variable.

### 2. Run Migrations
```bash
# Activate virtual environment
source venv/Scripts/activate  # Windows Git Bash
# or
venv\Scripts\activate         # Windows CMD

# Create and run migrations
python manage.py makemigrations
python manage.py migrate
```

### 2. Start Servers

**Backend:**
```bash
python manage.py runserver
```

**Frontend (new terminal):**
```bash
cd frontend
npm run dev
```

### 3. Access Points

- **Public Suggestion Form**: `http://localhost:5173/suggest`  
- **Admin Login**: `http://localhost:5173/admin/login`  
  - Username: `admin` (from .env: ADMIN_USERNAME)  
  - Password: Check your `.env` file (ADMIN_PASSWORD variable)  
- **Admin Dashboard**: `http://localhost:5173/admin` (after login)

---

## How It Works

### Public Users
1. Visit `/suggest` (or share this link)
2. Fill out suggestion form:
   - Type: New Work, New Composer, Correction, etc.
   - Title and description
   - Optional: name and email
3. Submit → stored in database

### Admin Workflow
1. Go to `/admin/login` (you can bookmark this)
2. Login with credentials from your `.env` file
3. Review suggestions:
   - **Pending** - needs review
   - **Approve** - mark as worth adding
   - **Reject** - declined (with notes)
   - **Merged** - added to database
   - **Delete** - remove completely

---

## API Endpoints

### Authentication
```
POST /api/auth/login/
Body: {"username": "admin", "password": "your-password-from-env"}

POST /api/auth/logout/

GET /api/auth/user/
```

### Suggestions
```
POST /api/suggestions/              # Anyone can submit
GET /api/suggestions/               # Admin only - list all
GET /api/suggestions/?status=pending # Filter by status
GET /api/suggestions/{id}/          # Admin only - view one
PUT /api/suggestions/{id}/          # Admin only - edit
DELETE /api/suggestions/{id}/       # Admin only - delete

# Admin actions
POST /api/suggestions/{id}/approve/
POST /api/suggestions/{id}/reject/
POST /api/suggestions/{id}/mark_merged/
```

---

## Files Created/Modified

### Backend
- `music/models.py` - Added `UserSuggestion` model
- `music/serializers.py` - Added `UserSuggestionSerializer`
- `music/views.py` - Added `UserSuggestionViewSet`
- `music/permissions.py` - Updated with hardcoded admin check
- `music/auth_views.py` - Hardcoded authentication
- `music/urls.py` - Registered suggestion routes
- `music/admin.py` - Registered model in Django admin

### Frontend
- `src/components/suggestions/SuggestionForm.tsx` - Public form
- `src/components/suggestions/SuggestionForm.css`
- `src/pages/SuggestionPage.tsx` - Wrapper page for form
- `src/pages/AdminSuggestions.tsx` - Admin review UI
- `src/pages/AdminSuggestions.css`
- `src/App.tsx` - Routes configured

---

##Configuration

### Auth Context (frontend/src/contexts/AuthContext.tsx)

The auth system checks for `is_staff` in the user object. The login endpoint reads credentials from environment variables and returns:
```json
{
  "username": "admin",
  "is_staff": true,
  "is_admin": true
}
```

### Permissions (music/permissions.py)

```python
class IsHardcodedAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.session.get('is_admin', False)
```

---

## Security Notes

### Environment Variables
- **Password location**: `.env` file (never committed to git)
- **.gitignore**: Already configured to exclude `.env`
- **.env.example**: Template file (safe to commit) shows required variables
- **Session-based**: Uses Django sessions for authentication

### Credentials
Admin credentials are stored in `.env`:
```bash
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password-here  # Set your own password!
```

### Recommendations for Production
1. **Change the password** in `.env` file (not in code!)
2. **Never commit .env** to git (already in .gitignore)
3. **Use HTTPS** (`SESSION_COOKIE_SECURE=True`)
4. **Set strong SECRET_KEY** in .env
5. **Enable CSRF** (already configured)
6. **Consider rate limiting** for the suggestion form

---

## Customization

### Change Admin Password
Edit `.env` file (NOT code):
```bash
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-new-secure-password
```

Restart the Django server for changes to take effect.

### Add More Suggestion Types
Edit `music/models.py`:
```python
SUGGESTION_TYPE_CHOICES = [
    ('new_composer', 'New Composer'),
    ('new_work', 'New Work'),
    # Add more types here
]
```

### Customize Form Fields
Edit `frontend/src/components/suggestions/SuggestionForm.tsx`

---

## Database Schema

```sql
CREATE TABLE user_suggestions (
    id INTEGER PRIMARY KEY,
    suggestion_type VARCHAR(20),  -- new_work, correction, etc.
    status VARCHAR(20),            -- pending, approved, rejected, merged
    title VARCHAR(200),
    description TEXT,
    submitter_name VARCHAR(100),
    submitter_email VARCHAR(254),
    suggested_data JSONB,          -- Structured data if needed
    related_composer_id INTEGER,   -- Optional FK to composers
    related_work_id INTEGER,       -- Optional FK to works
    admin_notes TEXT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Testing

### Test Public Submission
```bash
curl -X POST http://localhost:8000/api/suggestions/ \
  -H "Content-Type: application/json" \
  -d '{
    "suggestion_type": "new_work",
    "title": "Missing Guitar Piece",
    "description": "Barrios - Las Abejas is not in the database",
    "submitter_name": "John Doe",
    "submitter_email": "john@example.com"
  }'
```

### Test Admin Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password-from-env"}' \
  --cookie-jar cookies.txt

curl http://localhost:8000/api/suggestions/ \
  --cookie cookies.txt
```

---

## Sharing the Suggestion Link

Give users this link to submit suggestions:
```
https://yourdomain.com/suggest
```

Keep the admin link private (bookmark it):
```
https://yourdomain.com/admin/login
```

---

## Next Steps

- [ ] Run migrations to create the `user_suggestions` table
- [ ] Test the suggestion form at `/suggest`
- [ ] Test admin login at `/admin/login`
- [ ] Bookmark the admin portal
- [ ] Share the `/suggest` link with users

---

## Troubleshooting

### "No module named 'whitenoise'"
```bash
pip install whitenoise
```

### "CSRF token missing"
- Ensure `/api/auth/csrf/` is called before login
- Check `CORS_ALLOW_CREDENTIALS = True` in settings

### Suggestions not showing in admin
- Check filter (try "All" button)
- Verify backend is running and connected

### Can't login
- Check your `.env` file has ADMIN_USERNAME and ADMIN_PASSWORD set
- Verify you're using the exact password from `.env` (case-sensitive)
- Restart Django server after changing `.env`
- Check browser console for errors

---

**You now have a simple, single-admin suggestion management system!** 🎉
