package pipeline

import (
	"strings"

	"github.com/agent-context-base/canonical-faker-go/internal/domain"
	"github.com/agent-context-base/canonical-faker-go/internal/profiles"
	gofaker "github.com/go-faker/faker/v4"
)

type UserTagged struct {
	ID       string `faker:"uuid_hyphenated"`
	Email    string `faker:"email"`
	FullName string `faker:"name"`
}

// go-faker/faker populates individual struct fields. Relational graph integrity
// (memberships, projects, events) must be handled in the orchestration layer,
// not by struct tags.
func GenerateWithStructTag(profile profiles.Profile) (domain.Dataset, error) {
	dataset, err := GenerateWithGoFakeIt(profile)
	if err != nil {
		return domain.Dataset{}, err
	}
	for index := range dataset.Users {
		tagged := UserTagged{}
		if err := gofaker.FakeData(&tagged); err != nil {
			return domain.Dataset{}, err
		}
		dataset.Users[index].Email = strings.ToLower(tagged.Email)
		dataset.Users[index].FullName = tagged.FullName
	}
	return dataset, nil
}
