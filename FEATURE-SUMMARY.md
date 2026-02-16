# Marshall Capstone - Feature List Summary

**Project:** Jones County Cross Country Team Management System
**Live Site:** https://marshallcapew.xyz
**Repository:** https://github.com/Ethanwells10/marshall-capstone

---

## Module 1: Deployment & Infrastructure

**Goal:** Deploy a "Hello World" full-stack application with custom domain and HTTPS

### Features Delivered:
- AWS Lightsail instance deployment (Ubuntu 22.04)
- Custom domain setup (marshallcapew.xyz via Namecheap)
- SSL certificate with Let's Encrypt
- Nginx reverse proxy configuration
- Static IP allocation
- React 19 + Vite frontend
- Go backend server
- Systemd service for auto-restart

**Tech Stack:** React, Go, Nginx, AWS Lightsail, Let's Encrypt

---

## Module 2: Database & REST API

**Goal:** Add SQLite database with REST API endpoints

### Features Delivered:
- SQLite database with 3 tables:
  - Athletes (id, name, grade, personal_record, team)
  - Meets (id, name, date, location, distance)
  - Results (id, athlete_id, meet_id, time, place)
- Full REST API:
  - **Athletes:** GET all, GET by id, POST, PUT, DELETE
  - **Meets:** GET all, GET by id, POST
  - **Results:** GET all (with JOIN queries), POST
- Pure Go SQLite driver (modernc.org/sqlite) - no CGO required
- Sample data: 8 athletes, 5 meets, 36 results
- Database initialization script
- CORS enabled for frontend

**API Endpoints:** 9 total endpoints serving JSON responses over HTTPS

---

## Module 3: React Frontend & Admin Dashboard

**Goal:** Build public pages and admin CRUD interface

### Public Pages:
1. **Home** - Hero section, welcome card, quick links to other pages
2. **Athletes** - Grid view of all athletes with PRs and grades
3. **Meets** - Schedule list with formatted dates and locations
4. **Results** - Table view with color-coded place badges (1st = gold, 2nd-3rd = silver, etc.)

### Authentication:
- Username/password login system
- Protected routes using React Router
- LocalStorage session management
- Credentials: `ethanwells / admin123`

### Admin Dashboard (Full CRUD):
- **View** all athletes in sortable table
- **Create** new athletes via form
- **Update** existing athletes (inline editing)
- **Delete** athletes with confirmation dialog
- Real-time cache invalidation with TanStack Query

### Technical Features:
- React Router DOM for client-side routing
- TanStack Query for data fetching & caching
- Axios HTTP client with request interceptors
- Tailwind CSS for responsive styling
- Form validation
- Loading states & error handling
- Optimistic UI updates

**Frontend Dependencies:** React 19, React Router 7, TanStack Query 5, Axios, Tailwind CSS 4

---

## Summary Statistics

- **Total Commits:** 5
- **Lines of Code Added:** ~2,200+
- **Files Created:** 20+
- **API Endpoints:** 9
- **Frontend Pages:** 6 (Home, Athletes, Meets, Results, Login, Admin)
- **Database Tables:** 3
- **Development Time:** ~6.75 hours total across all 3 modules

---

## Key Technical Decisions

1. **SQLite over MySQL** - Chose SQLite due to 512MB RAM constraint on smallest Lightsail instance
2. **Pure Go driver** - Used modernc.org/sqlite instead of mattn/go-sqlite3 to avoid CGO cross-compilation issues
3. **TanStack Query** - Implemented for automatic caching, reducing unnecessary API calls
4. **Tailwind CSS** - Used utility-first CSS for rapid UI development
5. **LocalStorage auth** - Simple demo authentication (production would use JWT with backend validation)

---

## Deployment Architecture

```
User Request (HTTPS)
    ↓
Nginx Reverse Proxy (marshallcapew.xyz)
    ├─→ Static Files (/var/www/hello-frontend/) - React SPA
    └─→ API Proxy (/api/*) → Go Backend (localhost:8080)
                                    ↓
                              SQLite Database (xc_database.db)
```

---

**Generated with Claude Code**
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
