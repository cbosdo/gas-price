package main

import (
	"archive/zip"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
)

func download(url string, file string) error {
	resp, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("failed to get URL %s: %s", url, err)
	}
	defer resp.Body.Close()

	return saveResponseToFile(resp, file)
}

func post(url string, data url.Values, file string) error {

	resp, err := http.PostForm(url, data)
	if err != nil {
		return fmt.Errorf("failed to send POST request to URL %s: %s", url, err)
	}
	defer resp.Body.Close()

	return saveResponseToFile(resp, file)
}

func saveResponseToFile(response *http.Response, file string) error {
	out, err := os.Create(file)
	if err != nil {
		return fmt.Errorf("failed to create %s file: %s", file, err)
	}
	defer out.Close()

	if response.StatusCode != http.StatusOK {
		return fmt.Errorf("got %d http status", response.StatusCode)
	}

	_, err = io.Copy(out, response.Body)
	if err != nil {
		return fmt.Errorf("failed to copy HTTP response to disk: %s", err)
	}
	return nil
}

func unzip(file string, dst string) error {
	archive, err := zip.OpenReader(file)
	if err != nil {
		return fmt.Errorf("failed to open zip file %s: %s", file, err)
	}
	defer archive.Close()

	for _, f := range archive.File {
		filePath := filepath.Join(dst, f.Name)

		if !strings.HasPrefix(filePath, filepath.Clean(dst)+string(os.PathSeparator)) {
			fmt.Errorf("skipping unzip of invalid path: %s", f.Name)
			continue
		}

		folderPath := filepath.Dir(filePath)
		if f.FileInfo().IsDir() {
			folderPath = filePath
		}

		if err := os.MkdirAll(folderPath, os.ModePerm); err != nil {
			return fmt.Errorf("failed to create folder : %s", err)
		}

		if !f.FileInfo().IsDir() {
			dstFile, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, f.Mode())
			if err != nil {
				return fmt.Errorf("failed to open file %s for writing: %s", filePath, err)
			}

			fileInArchive, err := f.Open()
			if err != nil {
				return fmt.Errorf("failed to read %s file in zip archive: %s", f.Name, err)
			}

			if _, err := io.Copy(dstFile, fileInArchive); err != nil {
				return fmt.Errorf("failed to extract %s file: %s", f.Name, err)
			}

			dstFile.Close()
			fileInArchive.Close()
		}
	}
	return nil
}

func copy(src string, dst string) error {
	srcFile, err := os.Open(src)
	if err != nil {
		return fmt.Errorf("failed to copy %s to %s: %s", src, dst, err)
	}
	defer srcFile.Close()

	dstFile, err := os.Create(dst)
	if err != nil {
		return fmt.Errorf("failed to copy %s to %s: %s", src, dst, err)
	}
	defer dstFile.Close()

	_, err = dstFile.ReadFrom(srcFile)
	if err != nil {
		return fmt.Errorf("failed to copy %s to %s: %s", src, dst, err)
	}
	return nil
}

func makeDir(path string, perm os.FileMode) {
	if err := os.MkdirAll(path, perm); err != nil {
		log.Fatalf("Failed to create directory %s: %s", path, err)
	}
}
