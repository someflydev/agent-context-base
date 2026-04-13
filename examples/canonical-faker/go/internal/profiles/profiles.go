package profiles

type Profile struct {
	Name     string
	NumOrgs  int
	NumUsers int
	Seed     int
}

var (
	Smoke  = Profile{Name: "smoke", NumOrgs: 3, NumUsers: 10, Seed: 42}
	Small  = Profile{Name: "small", NumOrgs: 20, NumUsers: 200, Seed: 1000}
	Medium = Profile{Name: "medium", NumOrgs: 200, NumUsers: 5000, Seed: 5000}
	Large  = Profile{Name: "large", NumOrgs: 2000, NumUsers: 50000, Seed: 9999}
)

func Resolve(name string, seedOverride int) Profile {
	var profile Profile
	switch name {
	case "small":
		profile = Small
	case "medium":
		profile = Medium
	case "large":
		profile = Large
	default:
		profile = Smoke
	}
	if seedOverride != 0 {
		profile.Seed = seedOverride
	}
	return profile
}
