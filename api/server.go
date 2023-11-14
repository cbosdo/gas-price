package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
)

var urlRegexp = regexp.MustCompile(`^/(?:node|way)/([0-9]+)$`)

type server struct {
	DataDir string
}

func (s *server) serve() {
	http.HandleFunc("/node/", s.nodeHandler)
	http.HandleFunc("/way/", s.wayHandler)

	log.Fatal(http.ListenAndServe(":8080", nil))
}

func (s *server) nodeHandler(resp http.ResponseWriter, request *http.Request) {
	s.getHandler("node", resp, request)
}

func (s *server) wayHandler(resp http.ResponseWriter, request *http.Request) {
	s.getHandler("way", resp, request)
}

func (s *server) getHandler(objectType string, resp http.ResponseWriter, request *http.Request) {
	matches := urlRegexp.FindAllStringSubmatch(request.URL.Path, -1)

	// Get the object id
	if matches == nil || len(matches) != 1 || len(matches[0]) != 2 {
		s.sendError(resp, http.StatusBadRequest, "Invalid query URL")
		return
	}
	objectId := matches[0][1]

	// Search the files if we have one matching the object ID
	folders, err := os.ReadDir(s.DataDir)
	if err != nil {
		log.Printf("Cannot read content of data directory %s: %s\n", s.DataDir, err)
		s.sendError(resp, http.StatusInternalServerError, "Internal server error, contact administrator for more details")
		return
	}

	for _, folder := range folders {
		if folder.IsDir() {
			path := filepath.Join(s.DataDir, folder.Name(), objectType, objectId)
			if _, err := os.Stat(path); err == nil {
				// Read the file and send it back
				data, err := os.ReadFile(path)
				if err != nil {
					log.Printf("Cannot read data file %s: %s\n", path, err)
					s.sendError(resp, http.StatusInternalServerError, "Internal server error, contact administrator for more details")
					return
				}
				resp.Header().Set("Content-Type", "text/json")
				resp.WriteHeader(http.StatusOK)
				resp.Write(data)
				return
			}
		}
	}

	s.sendError(resp, http.StatusNotFound, fmt.Sprintf("Prices for %s %s not known", objectType, objectId))
}

func (s *server) sendError(resp http.ResponseWriter, status int, msg string) {
	resp.Header().Set("Content-Type", "text/json")
	resp.WriteHeader(status)
	io.WriteString(resp, fmt.Sprintf("{\"err\": \"%s\"}", msg))
}
