package main

import (
	"os"
	"portal/boot"
)

func main() {
	if err := boot.Boot(make(chan os.Signal, 1), os.Getenv("B_MODE") == "test"); err != nil {
		panic(err)
	}
}
