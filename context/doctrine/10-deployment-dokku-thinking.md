# Deployment And Dokku-Oriented Thinking

Purpose: keep deployment simple and service-shaped.

Rules:

- Favor single-service deployability when it meets the need.
- Treat Dokku-friendly packaging as the default deployment posture.
- Add infrastructure only when it clearly improves the project.
- Keep local Compose ergonomics aligned with likely deployment boundaries.

Prevents:

- premature platform complexity
- local setups that do not resemble deployable units
