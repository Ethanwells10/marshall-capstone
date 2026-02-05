-- Cross Country Database Schema
-- Created for Marshall Capstone Project

-- Athletes table: stores information about runners
CREATE TABLE IF NOT EXISTS athletes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    grade INTEGER NOT NULL CHECK (grade >= 9 AND grade <= 12),
    personal_record TEXT,  -- Format: MM:SS.MS (e.g., "16:45.30")
    team TEXT DEFAULT 'Jones County',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Meets table: stores information about races/competitions
CREATE TABLE IF NOT EXISTS meets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date DATE NOT NULL,
    location TEXT NOT NULL,
    distance TEXT DEFAULT '5K',  -- e.g., "5K", "3K"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Results table: stores race results (links athletes to meets with their performance)
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id INTEGER NOT NULL,
    meet_id INTEGER NOT NULL,
    time TEXT NOT NULL,  -- Format: MM:SS.MS (e.g., "17:23.45")
    place INTEGER,  -- Overall placement in race
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (athlete_id) REFERENCES athletes(id) ON DELETE CASCADE,
    FOREIGN KEY (meet_id) REFERENCES meets(id) ON DELETE CASCADE,
    UNIQUE(athlete_id, meet_id)  -- Each athlete can only have one result per meet
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_results_athlete ON results(athlete_id);
CREATE INDEX IF NOT EXISTS idx_results_meet ON results(meet_id);
CREATE INDEX IF NOT EXISTS idx_meets_date ON meets(date);
