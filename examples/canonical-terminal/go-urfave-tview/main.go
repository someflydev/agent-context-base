package main

import (
	"fmt"
	"os"

	"github.com/agent-context-base/taskflow-go-tview/internal/cli"
)

func main() {
	app := cli.NewApp()
	if err := app.Run(normalizeArgs(os.Args)); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func normalizeArgs(args []string) []string {
	if len(args) < 2 {
		return args
	}

	commandIndex := -1
	for index := 1; index < len(args); index++ {
		switch args[index] {
		case "--fixtures-path":
			index++
		case "list", "inspect", "stats", "watch":
			commandIndex = index
			index = len(args)
		}
	}
	if commandIndex == -1 || args[commandIndex] != "inspect" {
		return args
	}

	prefix := append([]string{}, args[:commandIndex+1]...)
	options := make([]string, 0)
	positionals := make([]string, 0)
	for index := commandIndex + 1; index < len(args); index++ {
		token := args[index]
		if token == "--output" {
			options = append(options, token)
			if index+1 < len(args) {
				options = append(options, args[index+1])
				index++
			}
			continue
		}
		if len(token) > 0 && token[0] == '-' {
			options = append(options, token)
			continue
		}
		positionals = append(positionals, token)
	}
	return append(append(prefix, options...), positionals...)
}
