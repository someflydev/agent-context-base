package pipeline

import (
	"math/rand"
	"strings"
	"sync"

	"github.com/agent-context-base/canonical-faker-go/internal/domain"
	"github.com/agent-context-base/canonical-faker-go/internal/profiles"
	gofaker "github.com/go-faker/faker/v4"
)

type UserTagged struct {
	Email     string `faker:"email"`
	FirstName string `faker:"first_name"`
	LastName  string `faker:"last_name"`
}

// go-faker/faker populates individual struct fields. Relational graph integrity
// (memberships, projects, events) must be handled in the orchestration layer,
// not by struct tags.
func GenerateWithStructTag(profile profiles.Profile) (domain.Dataset, error) {
	dataset, err := GenerateWithGoFakeIt(profile)
	if err != nil {
		return domain.Dataset{}, err
	}
	configureStructTagSources(profile.Seed)
	for index := range dataset.Users {
		tagged := UserTagged{}
		if err := gofaker.FakeData(&tagged); err != nil {
			return domain.Dataset{}, err
		}
		dataset.Users[index].Email = strings.ToLower(tagged.Email)
		dataset.Users[index].FullName = strings.TrimSpace(tagged.FirstName + " " + tagged.LastName)
	}
	return dataset, nil
}

func configureStructTagSources(seed int) {
	gofaker.SetRandomSource(gofaker.NewSafeSource(rand.NewSource(int64(seed))))
	gofaker.SetCryptoSource(&lockedReader{
		rng: rand.New(rand.NewSource(int64(seed) + 1)),
	})
}

type lockedReader struct {
	mu  sync.Mutex
	rng *rand.Rand
}

func (reader *lockedReader) Read(p []byte) (int, error) {
	reader.mu.Lock()
	defer reader.mu.Unlock()
	return reader.rng.Read(p)
}
