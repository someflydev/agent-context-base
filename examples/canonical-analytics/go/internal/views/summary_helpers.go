package views

import "encoding/json"

func formatSummary(summary any) string {
    b, err := json.MarshalIndent(summary, "", "  ")
    if err != nil {
        return ""
    }
    return string(b)
}
