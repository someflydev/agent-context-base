base = defined?(Data) ? Data : Struct

Organization = base.define(:id, :name, :slug, :plan, :region, :created_at, :owner_email)
User         = base.define(:id, :email, :full_name, :locale, :timezone, :created_at)
Membership   = base.define(:id, :org_id, :user_id, :role, :joined_at, :invited_by)
Project      = base.define(:id, :org_id, :name, :status, :created_by, :created_at)
AuditEvent   = base.define(:id, :org_id, :user_id, :project_id, :action, :resource_type, :resource_id, :ts)
ApiKey       = base.define(:id, :org_id, :created_by, :name, :key_prefix, :created_at, :last_used_at)
Invitation   = base.define(:id, :org_id, :invited_email, :role, :invited_by, :expires_at, :accepted_at)

def entity_to_hash(entity)
  (entity.respond_to?(:members) ? entity.members : entity.class.members).zip(entity.deconstruct).to_h
      .transform_keys { |k| k.to_s }
end