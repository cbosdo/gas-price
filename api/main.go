package main

import (
	"log"
	"os"
)

func main() {
	if len(os.Args) != 2 {
		log.Fatalf("Missing path to the fetched data as parameter")
	}

	srv := server{DataDir: os.Args[1]}
	srv.serve()
}
