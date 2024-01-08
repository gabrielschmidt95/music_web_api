package models

import "go.mongodb.org/mongo-driver/bson/primitive"

type Collection struct {
	ID            primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	ReleaseYear   int                `bson:"RELEASE_YEAR,omitempty" json:"releaseYear"`
	Artist        string             `bson:"ARTIST,omitempty" json:"artist"`
	Title         string             `bson:"TITLE,omitempty" json:"title"`
	Media         string             `bson:"MEDIA,omitempty" json:"media"`
	Purchase      any                `bson:"PURCHASE,omitempty" json:"purchase"`
	Origin        string             `bson:"ORIGIN,omitempty" json:"origin"`
	EditionYear   int                `bson:"EDITION_YEAR,omitempty" json:"editionYear"`
	IfpiMastering any                `bson:"IFPI_MASTERING,omitempty" json:"ifpiMastering"`
	IfpiMould     any                `bson:"IFPI_MOULD,omitempty" json:"ifpiMould"`
	Barcode       string             `bson:"BARCODE,omitempty" json:"barcode"`
	Matriz        string             `bson:"MATRIZ,omitempty" json:"matriz"`
	Lote          string             `bson:"LOTE,omitempty" json:"lote"`
	Discogs       struct {
		Country string `bson:"country,omitempty" json:"country"`
		//Genre   []string `bson:"genre,omitempty" json:"genre"`
		//Format  []string `bson:"format,omitempty" json:"format"`
		//Style []string `bson:"style,omitempty" json:"style"`
		ID int `bson:"id,omitempty" json:"id"`
		//Label    []string `bson:"label,omitempty" json:"label"`
		Type string `bson:"type,omitempty" json:"type"`
		//Barcode  []string `bson:"barcode,omitempty" json:"barcode"`
		// UserData struct {
		// 	InWantlist   bool `bson:"in_wantlist,omitempty" json:"in_wantlist"`
		// 	InCollection bool `bson:"in_collection,omitempty" json:"in_collection"`
		// } `bson:"user_data,omitempty" json:"user_data"`
		MasterID    int    `bson:"master_id,omitempty" json:"master_id"`
		MasterURL   string `bson:"master_url,omitempty" json:"master_url"`
		URI         string `bson:"uri,omitempty" json:"uri"`
		Catno       string `bson:"catno,omitempty" json:"catno"`
		Title       string `bson:"title,omitempty" json:"title"`
		Thumb       string `bson:"thumb,omitempty" json:"thumb"`
		CoverImage  string `bson:"cover_image,omitempty" json:"cover_image"`
		ResourceURL string `bson:"resource_url,omitempty" json:"resource_url"`
		// Community   struct {
		// 	Want int `bson:"want,omitempty" json:"want"`
		// 	Have int `bson:"have,omitempty" json:"have"`
		// } `bson:"community,omitempty" json:"community"`
		FormatQuantity int `bson:"format_quantity,omitempty" json:"format_quantity"`
		// Formats        []struct {
		// 	Name         string   `bson:"name,omitempty" json:"name"`
		// 	Qty          string   `bson:"qty,omitempty" json:"qty"`
		// 	Descriptions []string `bson:"descriptions,omitempty" json:"descriptions"`
		// } `bson:"formats,omitempty" json:"formats"`
		Urls []struct {
			ID  int    `bson:"id,omitempty" json:"id"`
			URI string `bson:"uri,omitempty" json:"uri"`
		} `bson:"urls,omitempty" json:"urls"`
		Len    int `bson:"len,omitempty" json:"len"`
		Tracks []struct {
			Position string `bson:"position,omitempty" json:"position"`
			Type     string `bson:"type_,omitempty" json:"type_"`
			Title    string `bson:"title,omitempty" json:"title"`
			Duration string `bson:"duration,omitempty" json:"duration"`
		} `bson:"tracks,omitempty" json:"tracks"`
	} `bson:"DISCOGS,omitempty" json:"discogs"`
	Spotify struct {
		AlbumType string `bson:"album_type,omitempty" json:"album_type"`
		Artists   []struct {
			ExternalUrls struct {
				Spotify string `bson:"spotify,omitempty" json:"spotify"`
			} `bson:"external_urls,omitempty" json:"external_urls"`
			Href string `bson:"href,omitempty" json:"href"`
			ID   string `bson:"id,omitempty" json:"id"`
			Name string `bson:"name,omitempty" json:"name"`
			Type string `bson:"type,omitempty" json:"type"`
			URI  string `bson:"uri,omitempty" json:"uri"`
		} `bson:"artists,omitempty" json:"artists"`
		//AvailableMarkets []string `bson:"available_markets,omitempty" json:"available_markets"`
		ExternalUrls struct {
			Spotify string `bson:"spotify,omitempty" json:"spotify"`
		} `bson:"external_urls,omitempty" json:"external_urls"`
		Href   string `bson:"href,omitempty" json:"href"`
		ID     string `bson:"id,omitempty" json:"id"`
		Images []struct {
			Height int    `bson:"height,omitempty" json:"height"`
			URL    string `bson:"url,omitempty" json:"url"`
			Width  int    `bson:"width,omitempty" json:"width"`
		} `json:"images"`
		Name                 string `bson:"name,omitempty" json:"name"`
		ReleaseDate          string `bson:"release_date,omitempty" json:"release_date"`
		ReleaseDatePrecision string `bson:"release_date_precision,omitempty" json:"release_date_precision"`
		TotalTracks          int    `bson:"total_tracks,omitempty" json:"total_tracks"`
		Type                 string `bson:"type,omitempty" json:"type"`
		URI                  string `bson:"uri,omitempty" json:"uri"`
	} `bson:"SPOTIFY,omitempty" json:"spotify"`
}
