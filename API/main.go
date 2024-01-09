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

	_ "music-go-api/docs"

	"github.com/go-openapi/runtime/middleware"
	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
)

const albumNotFound = "Album not found"
const invalidInput = "Invalid input"
const contentType = "Content-Type"

// @Summary Query album
// @Description Query album
// @Tags Album
// @Accept  json
// @Produce  json
// @Param album body string true "Album"
// @Success 200 {object} string
// @Security BearerAuth
// @Router /query [post]
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

// @Summary Get albuns by artist
// @Description Get albuns by artist
// @Tags Album
// @Accept  json
// @Produce  json
// @Param artist body string true "Artist"
// @Success 200 {object} string
// @Security BearerAuth
// @Router /album/artist [post]
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

// @Summary Get albuns by year
// @Description Get albuns by year
// @Tags Album
// @Accept  json
// @Produce  json
// @Param year body int true "Year"
// @Param metric body string true "Metric"
// @Success 200 {object} string
// @Security BearerAuth
// @Router /album/year [post]
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

// @Summary Get albuns by ID
// @Description Get albuns by ID
// @Tags Album
// @Accept  json
// @Produce  json
// @Param id body string true "ID"
// @Success 200 {object} string
// @Security BearerAuth
// @Router /album/id [post]
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

// @Summary Get albuns
// @Description Get albuns
// @Tags Album
// @Accept  json
// @Produce  json
// @Param artist body string true "Artist"
// @Param media body string true "Media"
// @Param origin body string true "Origin"
// @Success 200 {object} string
// @Security BearerAuth
// @Router /albuns [post]
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

// @Summary Insert album
// @Description Insert album
// @Tags Album
// @Accept  json
// @Produce  json
// @Param album body string true "Album"
// @Success 200 {object} string
// @Security BearerAuth
// @Router /new/album [post]
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

// @Summary Insert logs
// @Description Insert logs
// @Tags Logs
// @Accept  json
// @Produce  json
// @Param log body string true "Log"
// @Param type body string true "Type"
// @Success 200 {object} string
// @Security BearerAuth
// @Router /logs [post]
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

// @Summary Update album
// @Description Update album
// @Tags Album
// @Accept  json
// @Produce  json
// @Param album body string true "Album"
// @Success 200 {object} string
// @Security BearerAuth
// @Router /update/album [post]
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

// @Summary Delete album
// @Description Delete album
// @Tags Album
// @Accept  json
// @Produce  json
// @Param id body string true "ID"
// @Success 200 {object} string
// @Security BearerAuth
// @Router /delete/album [post]
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

// @Summary Get artists
// @Description Get artists
// @Tags Artist
// @Accept  json
// @Produce  json
// @Success 200 {object} string
// @Security BearerAuth
// @Router /artists [get]
func getArtists(w http.ResponseWriter, rq *http.Request) {
	resp := db.GetArtists()
	json.NewEncoder(w).Encode(resp)
}

// @Summary Get all
// @Description Get all
// @Tags Album
// @Accept  json
// @Produce  json
// @Success 200 {object} string
// @Security BearerAuth
// @Router /all [get]
func getAll(w http.ResponseWriter, rq *http.Request) {
	resp := db.GetAll()
	json.NewEncoder(w).Encode(resp)
}

// @Summary Get medias
// @Description Get medias
// @Tags Aggegation
// @Accept  json
// @Produce  json
// @Success 200 {object} string
// @Security BearerAuth
// @Router /medias [get]
func getMedias(w http.ResponseWriter, rq *http.Request) {
	resp := db.GetMedia()
	json.NewEncoder(w).Encode(resp)
}

// @Summary Get totals
// @Description Get totals
// @Tags Aggegation
// @Accept  json
// @Produce  json
// @Success 200 {object} string
// @Security BearerAuth
// @Router /totals [get]
func getTotals(w http.ResponseWriter, rq *http.Request) {
	resp := db.GetTotals()
	json.NewEncoder(w).Encode(resp)
}

// @Summary Get user
// @Description Get user
// @Tags User
// @Accept  json
// @Produce  json
// @Success 200 {object} string
// @Security BearerAuth
// @Router /user [get]
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

// @Summary Get albuns by title
// @Description Get albuns by title
// @Tags Album
// @Accept  json
// @Produce  json
// @Param title body string true "Title"
// @Success 200 {object} string
// @Security BearerAuth
// @Router /title [post]
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

// @Summary Health check
// @Description Health check
// @Tags Health
// @Accept  json
// @Produce  json
// @Success 200 {object} string
// @Router /health [get]
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

// @title Music API
// @description This is a sample server Music API server.
// @version 1
// @host api.schmidtdev.cloud
// @Schemes https
// @securityDefinitions.apikey BearerAuth
// @in header
// @name Authorization
// @BasePath /
func main() {
	defer db.CloseConn()

	router := mux.NewRouter()

	router.HandleFunc("/health", HealthCheckHandler).Methods("GET")

	router.Handle("/swagger.yaml", http.FileServer(http.Dir("./docs")))
	opts := middleware.SwaggerUIOpts{SpecURL: "swagger.yaml"}
	sh := middleware.SwaggerUI(opts, nil)
	router.Handle("/docs", sh)

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
