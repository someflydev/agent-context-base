package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"

	"github.com/agent-context-base/canonical-faker-go/internal/domain"
	"github.com/agent-context-base/canonical-faker-go/internal/pipeline"
	"github.com/agent-context-base/canonical-faker-go/internal/pools"
	"github.com/agent-context-base/canonical-faker-go/internal/profiles"
	"github.com/agent-context-base/canonical-faker-go/internal/validate"
)

func main() {
	profileName := flag.String("profile", "smoke", "smoke|small|medium|large")
	pipelineName := flag.String("pipeline", "gofakeit", "gofakeit|structtag")
	outputDir := flag.String("output", "./output", "output directory")
	format := flag.String("format", "jsonl", "jsonl|csv")
	seedOverride := flag.Int("seed", 0, "optional seed override")
	flag.Parse()

	profile := profiles.Resolve(*profileName, *seedOverride)
	var (
		generated domain.Dataset
		err       error
	)
	switch *pipelineName {
	case "structtag":
		generated, err = pipeline.GenerateWithStructTag(profile)
	default:
		generated, err = pipeline.GenerateWithGoFakeIt(profile)
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	report := validate.Dataset(generated)
	reportJSON, _ := json.MarshalIndent(report, "", "  ")
	fmt.Println(string(reportJSON))
	if !report.OK {
		os.Exit(1)
	}
	targetDir := filepath.Join(*outputDir, profile.Name)
	if *format == "csv" {
		if err := pools.WriteCSV(generated, targetDir, report.Counts, report.OK, report.Seed, report.Profile); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		return
	}
	if err := pools.WriteJSONL(generated, targetDir, report); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
