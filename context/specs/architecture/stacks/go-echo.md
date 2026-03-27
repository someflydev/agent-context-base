## Go + Echo Constraints

Handlers should stay explicit and small. Serialization, validation, and persistence should live behind named functions or packages instead of accumulating in one large handler chain.

Keep transport details separate from domain logic so tests can prove handler behavior and business logic independently.
