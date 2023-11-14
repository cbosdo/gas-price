package main

import (
	"encoding/xml"
	"fmt"
	"io"
	"log"
	"net/url"
	"os"
	"path/filepath"
)

func getOsmGasStations(location string, dataFile string) error {
	query := fmt.Sprintf("area[name='%s']; nwr(area)['amenity'=fuel]; out;", location)

	if err := post("https://overpass-api.de/api/interpreter", url.Values{"data": {query}}, dataFile); err != nil {
		return fmt.Errorf("Failed to retrieve gas stations using openstreetmap API: %s", err)
	}

	return nil
}

type osmTag struct {
	Key   string `xml:"k,attr"`
	Value string `xml:"v,attr"`
}

type osmStation struct {
	Id   string   `xml:"id,attr"`
	Lat  float32  `xml:"lat,attr"`
	Lng  float32  `xml:"lng,attr"`
	Tags []osmTag `xml:"tag"`
}

func (s *osmStation) getTag(key string) string {
	for _, tag := range s.Tags {
		if tag.Key == key {
			return tag.Value
		}
	}
	return ""
}

func processOsmObjects(filePath string, pricesDir string, dataDir string) error {
	f, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("failed to openstreetmap data file %s for parsing: %s", filePath, err)
	}
	defer f.Close()

	decoder := xml.NewDecoder(f)

	matchedIds := map[string]string{}

	makeDir(filepath.Join(dataDir, "node"), 0755)
	makeDir(filepath.Join(dataDir, "way"), 0755)

	for {
		token, err := decoder.Token()
		if token == nil || err == io.EOF {
			break
		} else if err != nil {
			return fmt.Errorf("error decoding token %s", err)
		}

		switch tokenType := token.(type) {
		case xml.StartElement:
			switch tokenType.Name.Local {
			case "node":
				fallthrough
			case "way":
				var store osmStation
				if err := decoder.DecodeElement(&store, &tokenType); err != nil {
					return fmt.Errorf("failed to parse osm node or way: %s", err)
				}

				prixCarburantsId := checkPrixCarburantTag(&store, pricesDir, tokenType.Name.Local)
				if prixCarburantsId == "" {
					continue
				}
				// Copy the price file to destination and name if after the OSM id
				// We cannot remove it since there could be multiple nodes / way with the same prixCarburantsId
				dstPath := filepath.Join(dataDir, tokenType.Name.Local, store.Id)
				if err := copy(filepath.Join(pricesDir, prixCarburantsId), dstPath); err != nil {
					return err
				}

				// TODO Check if the OSM data are in sync with prix-carburants and report mismatches
				matchedIds[prixCarburantsId] = store.Id
			default:
			}
		default:
		}
	}

	reportUnmatched(matchedIds, pricesDir)

	return nil
}

func checkPrixCarburantTag(osmStore *osmStation, pricesDir string, objectType string) string {
	prixCarburantsId := osmStore.getTag("ref:FR:prix-carburants")
	if prixCarburantsId == "" {
		return ""
	}

	pricesPath := filepath.Join(pricesDir, prixCarburantsId)
	if _, err := os.Stat(pricesPath); err != nil {
		fmt.Printf("openstreetmap %s %s with invalid ref:FR:prix-carburants: %s\n",
			objectType, osmStore.Id, prixCarburantsId)
		return ""
	}
	return prixCarburantsId
}

func copyStationPrices(osmStore *osmStation, prixCarburantsId string, pricesDir string, dataDir string) error {

	return nil
}

func reportUnmatched(matched map[string]string, pricesDir string) {
	files, err := os.ReadDir(pricesDir)
	if err != nil {
		log.Printf("Failed to list prices files: %s\n", err)
	}

	for _, file := range files {
		if _, ok := matched[file.Name()]; !ok {
			// TODO Fix the message
			log.Printf("prix-carburants gas station not found on openstreetmap: %s\n", file.Name())
		}
	}
}
