package main

import (
	"fmt"
	"os"

	"github.com/agent-context-base/taskflow-go-bubbletea/cmd"
)

func main() {
	if err := cmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
