package domain

type Organization struct {
	ID         string `json:"id"`
	Name       string `json:"name"`
	Slug       string `json:"slug"`
	Plan       string `json:"plan"`
	Region     string `json:"region"`
	CreatedAt  string `json:"created_at"`
	OwnerEmail string `json:"owner_email"`
}

type User struct {
	ID        string `json:"id"`
	Email     string `json:"email"`
	FullName  string `json:"full_name"`
	Locale    string `json:"locale"`
	Timezone  string `json:"timezone"`
	CreatedAt string `json:"created_at"`
}

type Membership struct {
	ID        string  `json:"id"`
	OrgID     string  `json:"org_id"`
	UserID    string  `json:"user_id"`
	Role      string  `json:"role"`
	JoinedAt  string  `json:"joined_at"`
	InvitedBy *string `json:"invited_by"`
}

type Project struct {
	ID        string `json:"id"`
	OrgID     string `json:"org_id"`
	Name      string `json:"name"`
	Status    string `json:"status"`
	CreatedBy string `json:"created_by"`
	CreatedAt string `json:"created_at"`
}

type AuditEvent struct {
	ID           string `json:"id"`
	OrgID        string `json:"org_id"`
	UserID       string `json:"user_id"`
	ProjectID    string `json:"project_id"`
	Action       string `json:"action"`
	ResourceType string `json:"resource_type"`
	ResourceID   string `json:"resource_id"`
	TS           string `json:"ts"`
}

type APIKey struct {
	ID         string  `json:"id"`
	OrgID      string  `json:"org_id"`
	CreatedBy  string  `json:"created_by"`
	Name       string  `json:"name"`
	KeyPrefix  string  `json:"key_prefix"`
	CreatedAt  string  `json:"created_at"`
	LastUsedAt *string `json:"last_used_at"`
}

type Invitation struct {
	ID           string  `json:"id"`
	OrgID        string  `json:"org_id"`
	InvitedEmail string  `json:"invited_email"`
	Role         string  `json:"role"`
	InvitedBy    string  `json:"invited_by"`
	ExpiresAt    string  `json:"expires_at"`
	AcceptedAt   *string `json:"accepted_at"`
}

type Dataset struct {
	ProfileName   string
	Seed          int
	Organizations []Organization
	Users         []User
	Memberships   []Membership
	Projects      []Project
	AuditEvents   []AuditEvent
	APIKeys       []APIKey
	Invitations   []Invitation
}
