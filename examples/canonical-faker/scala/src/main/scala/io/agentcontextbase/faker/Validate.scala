package io.agentcontextbase.faker

object Validate {

  def check(dataset: Dataset): ValidationReport = {
    var violations = Vector.empty[String]

    val orgsById = dataset.organizations.map(o => o.id -> o).toMap
    val projectsById = dataset.projects.map(p => p.id -> p).toMap
    val usersById = dataset.users.map(u => u.id -> u).toMap
    val membershipsByOrgAndUser = dataset.memberships.map(m => (m.org_id, m.user_id) -> m).toMap
    val memberEmailsByOrg = dataset.memberships.groupBy(_.org_id).view.mapValues { members =>
      members.flatMap(m => usersById.get(m.user_id).map(_.email)).toSet
    }.toMap

    // Rule A: membership.joined_at >= organization.created_at
    dataset.memberships.foreach { m =>
      orgsById.get(m.org_id).foreach { o =>
        if (m.joined_at < o.created_at) {
          violations = violations :+ s"Rule A failed for membership ${m.id}"
        }
      }
    }

    // Rule B: project.created_at >= organization.created_at
    dataset.projects.foreach { p =>
      orgsById.get(p.org_id).foreach { o =>
        if (p.created_at < o.created_at) {
          violations = violations :+ s"Rule B failed for project ${p.id}"
        }
      }
    }

    // Rule C: project.created_by must be a member of project.org_id
    dataset.projects.foreach { p =>
      if (!membershipsByOrgAndUser.contains((p.org_id, p.created_by))) {
        violations = violations :+ s"Rule C failed for project ${p.id}"
      }
    }

    // Rule D: audit_event.user_id must be a member of audit_event.org_id
    dataset.audit_events.foreach { a =>
      if (!membershipsByOrgAndUser.contains((a.org_id, a.user_id))) {
        violations = violations :+ s"Rule D failed for audit_event ${a.id}"
      }
    }

    // Rule E: audit_event.project_id must belong to audit_event.org_id
    dataset.audit_events.foreach { a =>
      projectsById.get(a.project_id) match {
        case Some(p) if p.org_id != a.org_id =>
          violations = violations :+ s"Rule E failed for audit_event ${a.id}"
        case None =>
          violations = violations :+ s"Rule E (missing project) failed for audit_event ${a.id}"
        case _ =>
      }
    }

    // Rule F: audit_event.ts >= project.created_at for that project
    dataset.audit_events.foreach { a =>
      projectsById.get(a.project_id).foreach { p =>
        if (a.ts < p.created_at) {
          violations = violations :+ s"Rule F failed for audit_event ${a.id}"
        }
      }
    }

    // Rule G: api_key.created_by must be a member of api_key.org_id
    dataset.api_keys.foreach { k =>
      if (!membershipsByOrgAndUser.contains((k.org_id, k.created_by))) {
        violations = violations :+ s"Rule G failed for api_key ${k.id}"
      }
    }

    // Rule H: invitation.invited_by must be a member of invitation.org_id
    dataset.invitations.foreach { i =>
      if (!membershipsByOrgAndUser.contains((i.org_id, i.invited_by))) {
        violations = violations :+ s"Rule H failed for invitation ${i.id}"
      }
    }

    // Rule I: invitation.invited_email must not match any member email for that org
    dataset.invitations.foreach { i =>
      memberEmailsByOrg.get(i.org_id).foreach { emails =>
        if (emails.contains(i.invited_email)) {
          violations = violations :+ s"Rule I failed for invitation ${i.id}"
        }
      }
    }

    val counts = Map(
      "organizations" -> dataset.organizations.size,
      "users" -> dataset.users.size,
      "memberships" -> dataset.memberships.size,
      "projects" -> dataset.projects.size,
      "audit_events" -> dataset.audit_events.size,
      "api_keys" -> dataset.api_keys.size,
      "invitations" -> dataset.invitations.size
    )

    ValidationReport(
      ok = violations.isEmpty,
      violations = violations,
      counts = counts,
      seed = 0L, // will be overwritten in Main
      profileName = "" // will be overwritten in Main
    )
  }
}
