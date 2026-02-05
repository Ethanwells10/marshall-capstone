package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"

	_ "modernc.org/sqlite"
)

var db *sql.DB

// Database models
type Athlete struct {
	ID             int    `json:"id"`
	Name           string `json:"name"`
	Grade          int    `json:"grade"`
	PersonalRecord string `json:"personal_record"`
	Team           string `json:"team"`
	CreatedAt      string `json:"created_at"`
	UpdatedAt      string `json:"updated_at"`
}

type Meet struct {
	ID        int    `json:"id"`
	Name      string `json:"name"`
	Date      string `json:"date"`
	Location  string `json:"location"`
	Distance  string `json:"distance"`
	CreatedAt string `json:"created_at"`
	UpdatedAt string `json:"updated_at"`
}

type Result struct {
	ID         int    `json:"id"`
	AthleteID  int    `json:"athlete_id"`
	MeetID     int    `json:"meet_id"`
	Time       string `json:"time"`
	Place      int    `json:"place"`
	CreatedAt  string `json:"created_at"`
	AthleteName string `json:"athlete_name,omitempty"`
	MeetName    string `json:"meet_name,omitempty"`
}

// Initialize database connection
func initDB() error {
	var err error
	dbPath := os.Getenv("DB_PATH")
	if dbPath == "" {
		dbPath = "./xc_database.db"
	}

	db, err = sql.Open("sqlite", dbPath)
	if err != nil {
		return fmt.Errorf("error opening database: %v", err)
	}

	// Test connection
	if err = db.Ping(); err != nil {
		return fmt.Errorf("error connecting to database: %v", err)
	}

	log.Println("Database connection established")
	return nil
}

// Enable CORS for frontend communication
func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
}

// Health check endpoint
func healthHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprint(w, `{"status":"ok"}`)
}

// GET /api/athletes - Get all athletes
func getAthletesHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")

	rows, err := db.Query("SELECT id, name, grade, personal_record, team, created_at, updated_at FROM athletes ORDER BY name")
	if err != nil {
		http.Error(w, `{"error":"Failed to query athletes"}`, http.StatusInternalServerError)
		log.Printf("Query error: %v", err)
		return
	}
	defer rows.Close()

	athletes := []Athlete{}
	for rows.Next() {
		var a Athlete
		if err := rows.Scan(&a.ID, &a.Name, &a.Grade, &a.PersonalRecord, &a.Team, &a.CreatedAt, &a.UpdatedAt); err != nil {
			log.Printf("Scan error: %v", err)
			continue
		}
		athletes = append(athletes, a)
	}

	json.NewEncoder(w).Encode(athletes)
}

// GET /api/athletes/:id - Get single athlete
func getAthleteHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")

	id := strings.TrimPrefix(r.URL.Path, "/api/athletes/")
	athleteID, err := strconv.Atoi(id)
	if err != nil {
		http.Error(w, `{"error":"Invalid athlete ID"}`, http.StatusBadRequest)
		return
	}

	var a Athlete
	err = db.QueryRow("SELECT id, name, grade, personal_record, team, created_at, updated_at FROM athletes WHERE id = ?", athleteID).
		Scan(&a.ID, &a.Name, &a.Grade, &a.PersonalRecord, &a.Team, &a.CreatedAt, &a.UpdatedAt)

	if err == sql.ErrNoRows {
		http.Error(w, `{"error":"Athlete not found"}`, http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, `{"error":"Database error"}`, http.StatusInternalServerError)
		log.Printf("Query error: %v", err)
		return
	}

	json.NewEncoder(w).Encode(a)
}

// POST /api/athletes - Create new athlete
func createAthleteHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")

	if r.Method == "OPTIONS" {
		return
	}

	var a Athlete
	if err := json.NewDecoder(r.Body).Decode(&a); err != nil {
		http.Error(w, `{"error":"Invalid request body"}`, http.StatusBadRequest)
		return
	}

	result, err := db.Exec("INSERT INTO athletes (name, grade, personal_record, team) VALUES (?, ?, ?, ?)",
		a.Name, a.Grade, a.PersonalRecord, a.Team)
	if err != nil {
		http.Error(w, `{"error":"Failed to create athlete"}`, http.StatusInternalServerError)
		log.Printf("Insert error: %v", err)
		return
	}

	id, _ := result.LastInsertId()
	a.ID = int(id)

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(a)
}

// GET /api/meets - Get all meets
func getMeetsHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")

	rows, err := db.Query("SELECT id, name, date, location, distance, created_at, updated_at FROM meets ORDER BY date DESC")
	if err != nil {
		http.Error(w, `{"error":"Failed to query meets"}`, http.StatusInternalServerError)
		log.Printf("Query error: %v", err)
		return
	}
	defer rows.Close()

	meets := []Meet{}
	for rows.Next() {
		var m Meet
		if err := rows.Scan(&m.ID, &m.Name, &m.Date, &m.Location, &m.Distance, &m.CreatedAt, &m.UpdatedAt); err != nil {
			log.Printf("Scan error: %v", err)
			continue
		}
		meets = append(meets, m)
	}

	json.NewEncoder(w).Encode(meets)
}

// POST /api/meets - Create new meet
func createMeetHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")

	if r.Method == "OPTIONS" {
		return
	}

	var m Meet
	if err := json.NewDecoder(r.Body).Decode(&m); err != nil {
		http.Error(w, `{"error":"Invalid request body"}`, http.StatusBadRequest)
		return
	}

	result, err := db.Exec("INSERT INTO meets (name, date, location, distance) VALUES (?, ?, ?, ?)",
		m.Name, m.Date, m.Location, m.Distance)
	if err != nil {
		http.Error(w, `{"error":"Failed to create meet"}`, http.StatusInternalServerError)
		log.Printf("Insert error: %v", err)
		return
	}

	id, _ := result.LastInsertId()
	m.ID = int(id)

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(m)
}

// GET /api/results - Get all results with athlete and meet names
func getResultsHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")

	query := `
		SELECT r.id, r.athlete_id, r.meet_id, r.time, r.place, r.created_at,
		       a.name as athlete_name, m.name as meet_name
		FROM results r
		JOIN athletes a ON r.athlete_id = a.id
		JOIN meets m ON r.meet_id = m.id
		ORDER BY r.created_at DESC
	`

	rows, err := db.Query(query)
	if err != nil {
		http.Error(w, `{"error":"Failed to query results"}`, http.StatusInternalServerError)
		log.Printf("Query error: %v", err)
		return
	}
	defer rows.Close()

	results := []Result{}
	for rows.Next() {
		var r Result
		if err := rows.Scan(&r.ID, &r.AthleteID, &r.MeetID, &r.Time, &r.Place, &r.CreatedAt, &r.AthleteName, &r.MeetName); err != nil {
			log.Printf("Scan error: %v", err)
			continue
		}
		results = append(results, r)
	}

	json.NewEncoder(w).Encode(results)
}

// POST /api/results - Create new result
func createResultHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")

	if r.Method == "OPTIONS" {
		return
	}

	var result Result
	if err := json.NewDecoder(r.Body).Decode(&result); err != nil {
		http.Error(w, `{"error":"Invalid request body"}`, http.StatusBadRequest)
		return
	}

	res, err := db.Exec("INSERT INTO results (athlete_id, meet_id, time, place) VALUES (?, ?, ?, ?)",
		result.AthleteID, result.MeetID, result.Time, result.Place)
	if err != nil {
		http.Error(w, `{"error":"Failed to create result"}`, http.StatusInternalServerError)
		log.Printf("Insert error: %v", err)
		return
	}

	id, _ := res.LastInsertId()
	result.ID = int(id)

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(result)
}

// DELETE /api/athletes/:id - Delete athlete
func deleteAthleteHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")

	if r.Method == "OPTIONS" {
		return
	}

	id := strings.TrimPrefix(r.URL.Path, "/api/athletes/")
	athleteID, err := strconv.Atoi(id)
	if err != nil {
		http.Error(w, `{"error":"Invalid athlete ID"}`, http.StatusBadRequest)
		return
	}

	result, err := db.Exec("DELETE FROM athletes WHERE id = ?", athleteID)
	if err != nil {
		http.Error(w, `{"error":"Failed to delete athlete"}`, http.StatusInternalServerError)
		log.Printf("Delete error: %v", err)
		return
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		http.Error(w, `{"error":"Athlete not found"}`, http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, `{"message":"Athlete deleted successfully"}`)
}

func main() {
	// Initialize database
	if err := initDB(); err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	mux := http.NewServeMux()

	// Health check
	mux.HandleFunc("/health", healthHandler)

	// Athletes endpoints
	mux.HandleFunc("/api/athletes", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case "GET":
			getAthletesHandler(w, r)
		case "POST":
			createAthleteHandler(w, r)
		case "OPTIONS":
			enableCORS(w)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	mux.HandleFunc("/api/athletes/", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case "GET":
			getAthleteHandler(w, r)
		case "DELETE":
			deleteAthleteHandler(w, r)
		case "OPTIONS":
			enableCORS(w)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	// Meets endpoints
	mux.HandleFunc("/api/meets", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case "GET":
			getMeetsHandler(w, r)
		case "POST":
			createMeetHandler(w, r)
		case "OPTIONS":
			enableCORS(w)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	// Results endpoints
	mux.HandleFunc("/api/results", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case "GET":
			getResultsHandler(w, r)
		case "POST":
			createResultHandler(w, r)
		case "OPTIONS":
			enableCORS(w)
		default:
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	addr := ":" + port
	log.Printf("Backend listening on %s\n", addr)
	log.Printf("Database: %s\n", os.Getenv("DB_PATH"))
	log.Fatal(http.ListenAndServe(addr, mux))
}
