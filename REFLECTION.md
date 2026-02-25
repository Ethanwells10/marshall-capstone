# Module 3 Reflection: Working with Claude Code

**Name:** Ethan Wells
**Project:** Jones County Cross Country Team Management System
**Repository:** https://github.com/Ethanwells10/marshall-capstone

---

## What prompts worked well? What didn't? Include examples.

Prompts that gave complete context worked exceptionally well. For example, when I pasted the entire Module 3 assignment with all requirements (*"Alright lets tackle the next assignment for our next module, 3. Here are the requirements..."*), Claude immediately broke it into 14 specific tasks and executed each one systematically. Simple, direct problem descriptions were also effective - when CRUD operations weren't working, I just said *"When I go to add new athletes/records and/or update existing records, it doesn't seem to work correctly. Can you confirm this and help?"* and Claude diagnosed the missing UPDATE endpoint within seconds. The only inefficiency was when I asked vague questions about timing (*"Should this be a relatively easy assignment?"*) instead of just starting the work - being direct and action-oriented consistently produced the best results.

## How did you communicate component structure and styling to Claude?

I primarily communicated structure through requirements rather than specifications. The assignment document mentioned "professional styling with Tailwind CSS and Shadcn," so I included that in my initial prompt and let Claude handle all architectural decisions. Claude automatically chose React Router for navigation, TanStack Query for data fetching, and implemented a Layout component with nested routes - I never had to explicitly request these patterns. For styling, I simply said the pages should look "professional" and Claude applied consistent Tailwind utility classes across all components, creating color-coded badges for race results and responsive grid layouts without me specifying exact classnames or breakpoints.

## What did you need to understand vs. what could you delegate?

I delegated essentially all code implementation to Claude: writing React components, setting up the Go backend, configuring SQLite, implementing CRUD operations, and handling deployment scripts. Claude handled architectural decisions like switching from MySQL to SQLite due to memory constraints and choosing the pure Go SQLite driver to avoid cross-compilation issues. What I needed to understand was the operational side: when to reboot the server (which happened multiple times when it became unresponsive), how to test the live application to catch bugs, and following Claude's deployment instructions by pasting commands into my terminal. I also had to manage the GitHub repository - sending the collaborator invite to my professor and updating GitHub Actions secrets - tasks that required my manual intervention through web interfaces.

## Brief technical overview of your frontend architecture.

The frontend is a React 19 single-page application built with Vite, using React Router DOM for client-side navigation across six pages (Home, Athletes, Meets, Results, Login, Admin). TanStack Query manages all server state with automatic caching and invalidation, eliminating the need for manual refetching after mutations. An Axios instance with base URL configuration handles all HTTP requests, automatically adding auth tokens via interceptors for protected routes. The Layout component wraps all pages with a responsive navigation bar and footer, while the ProtectedRoute component checks localStorage for authentication tokens before rendering the admin dashboard. All styling uses Tailwind CSS utility classes for a consistent design system, and the entire application is served as static files from Nginx with `try_files` configured to support client-side routing.

## What is the most important thing you learned about building a full-stack web application?

The most important lesson was understanding how resource constraints drive architectural decisions in production environments. When MySQL installation failed due to OOM on our 512MB Lightsail instance, I learned that "just use the standard solution" doesn't work in constrained environments - we had to pivot to SQLite. Similarly, when the Go build kept crashing on the server, we couldn't just "build on deploy" like typical CI/CD - we had to cross-compile on GitHub Actions runners with more memory. These real-world limitations taught me that infrastructure constraints shape your entire tech stack, from database choice to deployment strategy, and that flexibility and problem-solving matter more than following tutorials perfectly.

## How did your understanding of the codebase change from Module 1 to now?

In Module 1, I understood the project as two separate pieces: a React "hello world" served by Nginx and a Go "hello world" at an API endpoint. The connection between them was abstract - just "the frontend calls the backend." By Module 3, I understand the complete data flow: users interact with React components that trigger TanStack Query, which calls Axios, which hits Nginx, which proxies to Go handlers, which query SQLite, which returns JSON that bubbles back through the stack to update the UI via cache invalidation. I now see how authentication flows from localStorage to request headers, how CORS enables cross-origin requests, and how React Router's client-side navigation requires nginx's `try_files` directive. The codebase transformed from isolated files into an interconnected system where each layer depends on configuration details I didn't even know existed in Module 1.

---

**Total Project Time:**
- Module 1: ~4 hours (deployment and SSL configuration)
- Module 2: ~2 hours (database design and API implementation)
- Module 3: ~45 minutes (frontend development)
- Bug fixes and GitHub Actions: ~30 minutes

**Key Takeaway:** Clear requirements and systematic testing enabled rapid development with AI assistance. The majority of time was spent on infrastructure and debugging deployment issues rather than writing code.
