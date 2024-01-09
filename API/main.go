package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	db "music-go-api/database"
	"music-go-api/jwt"
	"music-go-api/models"

	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
)

const albumNotFound = "Album not found"
const invalidInput = "Invalid input"
const contentType = "Content-Type"

func queryAlbum(w http.ResponseWriter, rq *http.Request) {
	var m map[string]interface{}

	err := json.NewDecoder(rq.Body).Decode(&m)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	value := db.QueryAlbum(m)
	if len(value) == 0 {
		json.NewEncoder(w).Encode(map[string]string{})
		return
	}
	json.NewEncoder(w).Encode(value)
}

func getAlbunsbyArtist(w http.ResponseWriter, rq *http.Request) {
	type Artist struct {
		Name string `json:"artist"`
	}
	var p Artist
	err := json.NewDecoder(rq.Body).Decode(&p)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	value := db.GetAlbunsbyArtist(strings.ToUpper(p.Name))
	if len(value) == 0 {
		json.NewEncoder(w).Encode(map[string]string{"Message": "Artist not found"})
		return
	}
	json.NewEncoder(w).Encode(value)
}

func getAlbunsYear(w http.ResponseWriter, rq *http.Request) {
	type Year struct {
		Year   int    `json:"year"`
		Metric string `json:"metric"`
	}
	var p Year
	err := json.NewDecoder(rq.Body).Decode(&p)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	value := db.GetAlbunsbyYear(p.Year, strings.ToUpper(p.Metric))

	if len(value) == 0 {
		json.NewEncoder(w).Encode(map[string]string{})
		return
	}
	json.NewEncoder(w).Encode(value)
}

func getAlbunsId(w http.ResponseWriter, rq *http.Request) {
	type ID struct {
		ID string `json:"id"`
	}
	var p ID
	err := json.NewDecoder(rq.Body).Decode(&p)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	value := db.GetAlbunsbyID(p.ID)

	json.NewEncoder(w).Encode(value)
}

func getAlbuns(w http.ResponseWriter, rq *http.Request) {
	type Album struct {
		Artist string `json:"artist"`
		Media  string `json:"media"`
		Origin string `json:"origin"`
	}

	var alb Album
	err := json.NewDecoder(rq.Body).Decode(&alb)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	value := db.GetAlbuns(strings.ToUpper(alb.Artist), strings.ToUpper(alb.Media), strings.ToUpper(alb.Origin))

	if len(value) == 0 {
		json.NewEncoder(w).Encode(map[string]string{})
		return
	}
	json.NewEncoder(w).Encode(value)
}

func insertAlbum(w http.ResponseWriter, rq *http.Request) {
	var p models.Collection
	err := json.NewDecoder(rq.Body).Decode(&p)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"Message": invalidInput})
		return
	}
	if p.Artist == "" || p.Title == "" {
		json.NewEncoder(w).Encode(map[string]string{"Message": "Missing fields"})
		return
	}
	resp := db.InsertAlbum(p)
	json.NewEncoder(w).Encode(map[string]string{"Message": resp})
}

func insertLogs(w http.ResponseWriter, rq *http.Request) {
	type Logs struct {
		Log  interface{} `json:"log"`
		Type string      `json:"type"`
	}
	var p Logs
	err := json.NewDecoder(rq.Body).Decode(&p)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"Message": invalidInput})
		return
	}
	resp := db.InsertLogs(p)
	json.NewEncoder(w).Encode(map[string]string{"Message": resp})
}

func updateAlbum(w http.ResponseWriter, rq *http.Request) {
	var p models.Collection
	err := json.NewDecoder(rq.Body).Decode(&p)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"Message": invalidInput, "err": err.Error()})
		return
	}
	resp := db.UpdateAlbum(p)
	if resp == -1 {
		json.NewEncoder(w).Encode(map[string]string{"Message": "Invalid ID"})
		return
	} else if resp == 0 {
		json.NewEncoder(w).Encode(map[string]string{"Message": albumNotFound})
		return
	}
	json.NewEncoder(w).Encode(map[string]int64{"Message": resp})
}

func deleteAlbum(w http.ResponseWriter, rq *http.Request) {
	type ID struct {
		ID string `json:"id"`
	}
	var p ID
	err := json.NewDecoder(rq.Body).Decode(&p)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	resp := db.DeleteAlbumByID(p.ID)
	if resp == -1 {
		json.NewEncoder(w).Encode(map[string]string{"Message": "Invalid ID"})
		return
	} else if resp == 0 {
		json.NewEncoder(w).Encode(map[string]string{"Message": albumNotFound})
		return
	}
	json.NewEncoder(w).Encode(map[string]int64{"Message": resp})
}

func getArtists(w http.ResponseWriter, rq *http.Request) {
	resp := db.GetArtists()
	json.NewEncoder(w).Encode(resp)
}

func getAll(w http.ResponseWriter, rq *http.Request) {
	resp := db.GetAll()
	json.NewEncoder(w).Encode(resp)
}

func getMedias(w http.ResponseWriter, rq *http.Request) {
	resp := db.GetMedia()
	json.NewEncoder(w).Encode(resp)
}

func getTotals(w http.ResponseWriter, rq *http.Request) {
	resp := db.GetTotals()
	json.NewEncoder(w).Encode(resp)
}

func getUser(w http.ResponseWriter, rq *http.Request) {
	type USER struct {
		User string `json:"user"`
	}
	var p USER
	err := json.NewDecoder(rq.Body).Decode(&p)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	resp := db.GetUser(p.User)

	if resp == "" {
		json.NewEncoder(w).Encode(map[string]string{})
		return
	}
	json.NewEncoder(w).Encode(resp)
}

func getAlbunsbyTitle(w http.ResponseWriter, rq *http.Request) {
	type TITLE struct {
		Title string `json:"title"`
	}
	var p TITLE
	err := json.NewDecoder(rq.Body).Decode(&p)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	resp := db.GetAlbunsbyTitle(p.Title)

	if resp == nil {
		json.NewEncoder(w).Encode(map[string]string{"Message": albumNotFound})
		return
	}
	json.NewEncoder(w).Encode(resp)
}

func HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set(contentType, "application/json")
	w.WriteHeader(http.StatusOK)

	json.NewEncoder(w).Encode(map[string]bool{"alive": true})
}

func enableCors(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Credentials", "true")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Headers", "Authorization, Content-Type")
	w.Header().Set(contentType, "application/json")
}

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Println("Executing middleware", r.Method)

		if r.Method == "OPTIONS" {
			w.Header().Set("Access-Control-Allow-Origin", "*")
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Origin, Content-Type, X-Auth-Token, Authorization")
			w.Header().Set(contentType, "application/json; charset=UTF-8")
			return
		}
		enableCors(w)
		next.ServeHTTP(w, r)
		log.Println("Executing middleware again")
	})
}

func main() {
	defer db.CloseConn()

	router := mux.NewRouter()

	router.HandleFunc("/health", HealthCheckHandler).Methods("GET")
	router.Handle("/artists", jwt.EnsureValidToken()(http.HandlerFunc(getArtists))).Methods("GET")
	router.Handle("/medias", jwt.EnsureValidToken()(http.HandlerFunc(getMedias))).Methods("GET")
	router.Handle("/totals", jwt.EnsureValidToken()(http.HandlerFunc(getTotals))).Methods("GET")
	router.Handle("/user", jwt.EnsureValidToken()(http.HandlerFunc(getUser))).Methods("GET")
	router.Handle("/all", jwt.EnsureValidToken()(http.HandlerFunc(getAll))).Methods("GET")

	router.Handle("/album/artist", jwt.EnsureValidToken()(http.HandlerFunc(getAlbunsbyArtist))).Methods("POST")
	router.Handle("/album/year", jwt.EnsureValidToken()(http.HandlerFunc(getAlbunsYear))).Methods("POST")
	router.Handle("/album/id", jwt.EnsureValidToken()(http.HandlerFunc(getAlbunsId))).Methods("POST")
	router.Handle("/albuns", jwt.EnsureValidToken()(http.HandlerFunc(getAlbuns))).Methods("POST")
	router.Handle("/title", jwt.EnsureValidToken()(http.HandlerFunc(getAlbunsbyTitle))).Methods("POST")
	router.Handle("/new/album", jwt.EnsureValidToken()(http.HandlerFunc(insertAlbum))).Methods("POST")
	router.Handle("/update/album", jwt.EnsureValidToken()(http.HandlerFunc(updateAlbum))).Methods("POST")
	router.Handle("/delete/album", jwt.EnsureValidToken()(http.HandlerFunc(deleteAlbum))).Methods("POST")
	router.Handle("/query", jwt.EnsureValidToken()(http.HandlerFunc(queryAlbum))).Methods("POST")

	router.Handle("/logs", jwt.EnsureValidToken()(http.HandlerFunc(insertLogs))).Methods("POST")

	fmt.Println("Server running on port 3000")
	http.ListenAndServe(":3000", handlers.LoggingHandler(os.Stdout, corsMiddleware(router)))

}
