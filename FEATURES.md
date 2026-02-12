# Marshall Capstone Project - Feature List

## Project Overview
Full-stack web application for Jones County Cross Country team management, deployed on AWS Lightsail with custom domain and HTTPS.

**Live Site:** https://marshallcapew.xyz
**GitHub Repository:** https://github.com/Ethanwells10/marshall-capstone

---

## Module 1: Hello World Deployment

### Infrastructure & Deployment
- AWS Lightsail instance setup (Ubuntu 22.04)
- Static IP allocation to prevent IP changes on reboot
- Custom domain configuration (marshallcapew.xyz via Namecheap)
- DNS A record configuration
- SSL certificate installation with Let's Encrypt/Certbot
- Nginx reverse proxy configuration
- Systemd service for Go backend auto-restart

### Tech Stack Initialized
- **Frontend:** React 19 with Vite build tool
- **Backend:** Go (Golang) web server
- **Server:** Nginx on Ubuntu
- **Domain:** marshallcapew.xyz with HTTPS

---

## Module 2: Database Layer & REST API

### Database Architecture
- **Database:** SQLite with pure Go driver (modernc.org/sqlite)
- **Schema:** 3 tables with foreign key relationships
  - `athletes`: id, name, grade, personal_record, team, timestamps
  - `meets`: id, name, date, location, distance, timestamps
  - `results`: id, athlete_id, meet_id, time, place, timestamps

### Sample Data
- 8 cross country athletes (grades 9-12)
- 5 meets with dates and locations
- 32 race results linking athletes to meets

### REST API Endpoints

#### Athletes
- `GET /api/athletes` - List all athletes
- `GET /api/athletes/:id` - Get single athlete by ID
- `POST /api/athletes` - Create new athlete
- `PUT /api/athletes/:id` - Update athlete
- `DELETE /api/athletes/:id` - Delete athlete

#### Meets
- `GET /api/meets` - List all meets
- `GET /api/meets/:id` - Get single meet by ID
- `POST /api/meets` - Create new meet

#### Results
- `GET /api/results` - List all results with athlete and meet names
- `POST /api/results` - Create new result

### Backend Features
- CORS enabled for cross-origin requests
- JSON API responses
- Automatic timestamps (created_at, updated_at)
- Database initialization script (init_db.sh)
- Health check endpoint
- SQL JOIN queries for results with related data

---

## Module 3: React Frontend & Admin Dashboard

### Frontend Architecture
- **Routing:** React Router DOM v7 with client-side navigation
- **State Management:** TanStack Query (React Query) for server state
- **HTTP Client:** Axios with request interceptors
- **Styling:** Tailwind CSS with custom configuration
- **Build Tool:** Vite for fast development and optimized production builds

### Public Pages

#### Home Page
- Hero section with team name and tagline
- Welcome card with team description
- Three quick-link cards (Athletes, Schedule, Results)
- Fully responsive design

#### Athletes Page
- Grid layout (3 columns on large screens, responsive)
- Data fetched from `/api/athletes` endpoint
- Displays: name, grade, personal record, team
- Loading spinner during data fetch
- Error handling with user-friendly messages

#### Meets/Schedule Page
- List view of upcoming and past meets
- Data fetched from `/api/meets` endpoint
- Formatted dates with full weekday, month, day, year
- Displays: meet name, date, location, distance
- Distance badge highlighting
- Hover effects and transitions

#### Results Page
- Table view with sortable columns
- Data fetched from `/api/results` endpoint
- Displays: athlete name, meet name, time, place
- Color-coded place badges:
  - Gold for 1st place
  - Silver for 2nd-3rd place
  - Blue for 4th-10th place
  - Gray for 11th+
- Responsive table with horizontal scroll on mobile

### Authentication System
- Login page with password form
- Simple password validation (demo: "admin123")
- LocalStorage-based session management
- Protected route wrapper component
- Automatic redirect to login for unauthorized access
- Logout functionality in navigation

### Admin Dashboard (Protected)

#### Athlete Management (Full CRUD)
- **Read:** Table view of all athletes with sortable columns
- **Create:** Add new athlete form with validation
  - Fields: name, grade, personal record, team
  - Form opens in-page (no modal)
- **Update:** Edit athlete inline
  - Pre-populates form with existing data
  - Updates via PUT request
- **Delete:** Delete athlete with confirmation dialog
  - Prevents accidental deletions

#### Features
- TanStack Query automatic cache invalidation
- Optimistic UI updates
- Loading states during mutations
- Error handling for failed operations
- Form validation (required fields)
- Cancel button to close form

### UI/UX Features
- Responsive navigation bar with conditional rendering (Login/Logout/Admin)
- Sticky footer
- Loading spinners for all async operations
- Error messages in red alert boxes
- Success feedback through cache updates
- Smooth transitions and hover effects
- Tailwind utility classes for consistent design
- Mobile-first responsive breakpoints

### API Integration
- Axios instance with base URL configuration
- Automatic environment detection (dev vs production)
- Auth token interceptor on all requests
- Centralized API functions for all endpoints
- Error handling with user-friendly messages

---

## Technical Highlights

### Performance Optimizations
- Vite for fast HMR (Hot Module Replacement) in development
- Code splitting with React Router
- TanStack Query caching reduces unnecessary API calls
- Gzipped production build (101.56 KB JS, 4.18 KB CSS)
- Static asset caching

### Security Considerations
- HTTPS enforced via Let's Encrypt SSL
- CORS configuration on backend
- Auth token validation on protected routes
- SQL parameterized queries prevent injection
- Input validation on forms

### Cross-Platform Compatibility
- Pure Go SQLite driver (no CGO) enables cross-compilation
- Responsive design works on mobile, tablet, desktop
- Modern browser support (ES6+)

### Development Workflow
- Git version control with descriptive commits
- Separate development and production builds
- Environment-based API URL configuration
- Modular component architecture
- Clean separation of concerns (API, components, pages)

---

## Deployment Details

### Production Environment
- **Hosting:** AWS Lightsail (Ubuntu 22.04)
- **Instance Type:** Smallest tier (512MB RAM, optimized for low resource usage)
- **Domain:** marshallcapew.xyz
- **SSL:** Let's Encrypt with automatic renewal
- **Web Server:** Nginx reverse proxy
- **Backend Service:** systemd with auto-restart

### Build & Deploy Process
1. Local development with `npm run dev`
2. Production build with `npm run build`
3. Compress dist folder: `tar -czf dist.tar.gz dist/`
4. SCP to server: `scp dist.tar.gz ubuntu@server:~/`
5. Extract to web root: `/var/www/hello-frontend/`
6. Nginx serves static files, proxies `/api/*` to Go backend

---

## File Structure

```
marshall-capstone/
├── backend/
│   ├── main.go                 # Go server with SQLite
│   ├── go.mod                  # Go dependencies
│   ├── schema.sql              # Database schema
│   ├── sample_data.sql         # Sample data
│   └── init_db.sh             # DB initialization script
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.jsx     # Navigation + footer
│   │   │   └── ProtectedRoute.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx       # Landing page
│   │   │   ├── Athletes.jsx   # Athletes grid
│   │   │   ├── Meets.jsx      # Schedule list
│   │   │   ├── Results.jsx    # Results table
│   │   │   ├── Login.jsx      # Auth page
│   │   │   └── Admin.jsx      # CRUD dashboard
│   │   ├── lib/
│   │   │   └── api.js         # Axios client
│   │   ├── App.jsx            # Router setup
│   │   └── index.css          # Tailwind config
│   ├── package.json           # Dependencies
│   ├── vite.config.js         # Build config
│   └── tailwind.config.js     # Tailwind config
└── FEATURES.md                # This file
```

---

## Future Enhancements (Not Implemented)

Potential improvements for future iterations:
- User registration and role-based access control
- Photo uploads for athletes
- Race time analytics and charts
- Email notifications for new meets
- Mobile app with React Native
- Export results to CSV/PDF
- Meet registration system
- Team statistics dashboard

---

## Technologies Used

### Frontend
- React 19.2.0
- React Router DOM 7.1.3
- TanStack Query 5.66.3
- Axios 1.7.9
- Tailwind CSS 4.1.7
- Vite 7.2.4

### Backend
- Go 1.22
- modernc.org/sqlite (pure Go SQLite driver)
- Gorilla Mux router

### Infrastructure
- AWS Lightsail
- Ubuntu 22.04 LTS
- Nginx 1.24.0
- Let's Encrypt SSL
- Namecheap DNS

---

**Generated with Claude Code**
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
