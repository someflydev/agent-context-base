package cmd

import (
	"github.com/agent-context-base/taskflow-go-bubbletea/internal/core"
	"github.com/spf13/cobra"
)

var fixturesPath string

var rootCmd = &cobra.Command{
	Use:   "taskflow",
	Short: "TaskFlow Monitor",
}

func Execute() error {
	return rootCmd.Execute()
}

func fixtureRoot() string {
	return core.ResolveFixturesPath(fixturesPath)
}

func init() {
	rootCmd.PersistentFlags().StringVar(&fixturesPath, "fixtures-path", "", "Path to shared fixtures")
}
