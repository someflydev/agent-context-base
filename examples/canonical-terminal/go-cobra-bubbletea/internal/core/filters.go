package core

import "sort"

func FilterJobs(jobs []Job, status string, tag string) []Job {
	filtered := make([]Job, 0, len(jobs))
	for _, job := range jobs {
		if status != "" && string(job.Status) != status {
			continue
		}
		if tag != "" {
			found := false
			for _, item := range job.Tags {
				if item == tag {
					found = true
					break
				}
			}
			if !found {
				continue
			}
		}
		filtered = append(filtered, job)
	}
	return filtered
}

func SortJobs(jobs []Job) []Job {
	sorted := append([]Job(nil), jobs...)
	sort.SliceStable(sorted, func(i, j int) bool {
		left := ""
		right := ""
		if sorted[i].StartedAt != nil {
			left = *sorted[i].StartedAt
		}
		if sorted[j].StartedAt != nil {
			right = *sorted[j].StartedAt
		}
		if left == right {
			return sorted[i].Name < sorted[j].Name
		}
		return left > right
	})
	return sorted
}

func FindJob(jobs []Job, id string) *Job {
	for i := range jobs {
		if jobs[i].ID == id {
			return &jobs[i]
		}
	}
	return nil
}
