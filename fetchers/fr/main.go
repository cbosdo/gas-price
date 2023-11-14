package main

import (
	"log"
	"os"
	"path/filepath"
)

func main() {
	if len(os.Args) == 1 {
		log.Fatal("Path to the folder where to generate the data required")
	}
	outDir := os.Args[1]

	dir, err := os.MkdirTemp("", "gasprice")
	if err != nil {
		log.Fatalf("Failed to create temporary folder: %s\n", err)
	}
	defer os.RemoveAll(dir)

	if err := downloadPriceFile(dir); err != nil {
		log.Fatal(err)
	}

	const dataFile = "PrixCarburants_instantane.xml"

	// Parse the data file into a file for each station named after its ID
	storesDir := filepath.Join(dir, "prices")
	if err = os.Mkdir(storesDir, 0700); err != nil {
		log.Fatalf("Failed to create temporary prices folder")
	}

	dataPath := filepath.Join(dir, dataFile)
	if err := extractPrices(dataPath, storesDir); err != nil {
		log.Fatal(err)
	}

	// Get all the gas stations from OSM
	osmFilePath := filepath.Join(dir, "osm_gasstations.xml")
	if err := getOsmGasStations("France", osmFilePath); err != nil {
		log.Fatal(err)
	}

	// Clean the output directory before populating it again
	outContent, err := os.ReadDir(outDir)
	if err != nil {
		log.Fatalf("failed to list content of output directory %s for cleaning: %s", outDir, err)
	}
	for _, file := range outContent {
		filePath := filepath.Join(outDir, file.Name())
		if err := os.RemoveAll(filePath); err != nil {
			log.Fatalf("Failed to remove file %s: %s", filePath, err)
		}
	}

	// Parse the result and split in individual files named after the osm id
	if err := processOsmObjects(osmFilePath, storesDir, outDir); err != nil {
		log.Fatal(err)
	}
}

func downloadPriceFile(dir string) error {
	file := filepath.Join(dir, "data.zip")
	const url = "http://donnees.roulez-eco.fr/opendata/instantane"

	if err := download(url, file); err != nil {
		return err
	}

	if err := unzip(file, dir); err != nil {
		return err
	}

	return nil
}
