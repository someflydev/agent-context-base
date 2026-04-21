package domain

import "time"

type User struct {
	ID          string    `json:"id"`
	Email       string    `json:"email"`
	DisplayName string    `json:"display_name"`
	TenantID    *string   `json:"tenant_id"`
	CreatedAt   time.Time `json:"created_at"`
	IsActive    bool      `json:"is_active"`
	ACLVer      int       `json:"acl_ver"`
}

type Tenant struct {
	ID        string    `json:"id"`
	Slug      string    `json:"slug"`
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"created_at"`
	IsActive  bool      `json:"is_active"`
}

type Membership struct {
	ID         string    `json:"id"`
	UserID     string    `json:"user_id"`
	TenantID   *string   `json:"tenant_id"`
	TenantRole string    `json:"tenant_role"`
	CreatedAt  time.Time `json:"created_at"`
	IsActive   bool      `json:"is_active"`
}

type Group struct {
	ID        string    `json:"id"`
	TenantID  string    `json:"tenant_id"`
	Slug      string    `json:"slug"`
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"created_at"`
}

type Permission struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	CreatedAt   time.Time `json:"created_at"`
}

type GroupPermission struct {
	ID           string    `json:"id"`
	GroupID      string    `json:"group_id"`
	PermissionID string    `json:"permission_id"`
	GrantedAt    time.Time `json:"granted_at"`
}

type UserGroup struct {
	ID       string    `json:"id"`
	UserID   string    `json:"user_id"`
	GroupID  string    `json:"group_id"`
	JoinedAt time.Time `json:"joined_at"`
}
