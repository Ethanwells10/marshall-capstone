# Module 4 Reflection

## How did you decide on your independent project idea? What problem are you solving, and for whom?

I chose Market Monitor because I have a genuine interest in finance and investing, and I've always wanted a simple, free tool to track stocks without the bloat of platforms like Bloomberg or TradingView Pro. The idea came from a previous project I had started exploring, so I already had a rough outline of what I wanted to build. The app solves the problem of retail investors and finance students needing a lightweight, centralized dashboard to manage watchlists, view price charts, and organize their stock research — all without paying for expensive subscriptions.

## Describe how you approached planning your database schema. What tables did you identify, and how do they relate to each other?

I started by thinking about the core entities in the app: users need accounts, they create watchlists, watchlists contain stock tickers, and users write notes about those tickers. This led to five core tables — `users`, `tickers`, `watchlists`, `watchlist_items` (a junction table for the many-to-many relationship between watchlists and tickers), and `user_notes`. I also added an `api_cache` table to store API responses since the free-tier APIs have strict rate limits. The relationships use CASCADE deletes so that when a user is removed, all their watchlists, items, and notes are cleaned up automatically.

## What was the most difficult part of moving from a guided project to planning your own? How did you handle that uncertainty?

The hardest part was figuring out the right scope — it's tempting to add every feature you can think of, but that leads to a project you'll never finish. I handled it by being explicit about what I was NOT building (no portfolio tracking, no real-time streaming, no social features, no mobile app) which was just as important as defining what I was building. Having the structured proposal format with must-haves and out-of-scope sections forced me to make those decisions upfront rather than getting lost in feature creep later.

## How has your approach to working with Claude Code evolved since Module 1? What do you do differently now?

In Module 1, I was mostly just following prompts and accepting whatever Claude Code generated without much thought. Now I come in with a clear idea of what I want and treat Claude Code more like a collaborative partner — I provide the vision and outline, and Claude Code helps me execute it efficiently. I've also learned to break things into steps rather than asking for everything at once, and I'm more comfortable reviewing and understanding the code and documentation it produces rather than blindly trusting it.

## How did creating GitHub Issues change the way you think about implementing your project?

Creating GitHub Issues forced me to break the project down from one overwhelming idea into nine specific, manageable tasks with clear acceptance criteria. Instead of thinking "I need to build a stock tracking app," I now think "I need to set up Flask config, then create the database schema, then build auth" — each one a concrete, completable unit of work. It also gave me a natural order of operations, since some issues clearly depend on others (you can't build watchlists without the database schema, and you can't protect routes without auth).
