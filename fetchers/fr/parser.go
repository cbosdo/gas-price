package main

import (
	"encoding/json"
	"encoding/xml"
	"errors"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"time"

	"golang.org/x/net/html/charset"
)

var gasNames = map[string]string{
	"Gazole": "diesel",
	"E10":    "e10",
	"E85":    "e85",
	"SP95":   "octane_95",
	"SP98":   "octane_98",
	"GPLc":   "lpg",
}

type Price struct {
	Name   string     `json:"name"`
	Value  float32    `json:"value"`
	Update *time.Time `json:"update"`
}

type Store struct {
	Id     string  `json:"id"`
	Prices []Price `json:"prices"`
}

type frPriceType struct {
	Name   string  `xml:"nom,attr"`
	Value  float32 `xml:"valeur,attr"`
	Update string  `xml:"maj,attr"`
}

func (fr *frPriceType) convert() Price {
	updateTime, err := time.Parse(time.DateTime, fr.Update)
	if err != nil {
		log.Printf("invalid timestamp %s: %s\n", fr.Update, err)
	}

	gasName, exists := gasNames[fr.Name]
	if !exists {
		log.Printf("invalid gas name: %s\n", gasName)
	}

	return Price{
		Name:   gasName,
		Value:  fr.Value,
		Update: &updateTime,
	}
}

func extractPrices(filePath string, dataDir string) error {
	f, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("failed to open data file %s for parsing: %s", filePath, err)
	}
	defer f.Close()

	var store *Store

	decoder := xml.NewDecoder(f)
	decoder.CharsetReader = charset.NewReaderLabel
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
			case "pdv":
				id := getAttr(tokenType.Attr, "id")
				if id == "" {
					return errors.New("invalid file missing mandatory id for <pdv> element")
				}
				store = &Store{
					Id: id,
				}
			case "prix":
				if store != nil {
					var price frPriceType
					if err = decoder.DecodeElement(&price, &tokenType); err != nil {
						return fmt.Errorf("invalid <prix> element: %s", err)
					}
					store.Prices = append(store.Prices, price.convert())
				}
			default:
			}
		case xml.EndElement:
			if tokenType.Name.Local == "pdv" {
				data, err := json.Marshal(store)
				storePath := filepath.Join(dataDir, store.Id)
				if err != nil {
					return fmt.Errorf("failed to serialize store %s: %s", store.Id, err)
				}
				if err := os.WriteFile(storePath, data, 0600); err != nil {
					return fmt.Errorf("failed to write store data to file %s: %s", storePath, err)
				}
			}
		default:
		}
	}

	return nil
}

type textElement struct {
	Data string `xml:",chardata"`
}

func getAttr(attrs []xml.Attr, key string) string {
	for _, attr := range attrs {
		if attr.Name.Local == key {
			return attr.Value
		}
	}
	return ""
}
