# Add Local RAG Indexing

Purpose: add or change local indexing and retrieval flows.

Sequence:

1. define source documents and metadata contract
2. define chunking, indexing, and retrieval surfaces
3. keep dev and test indexes isolated
4. add smoke coverage for index and retrieval happy paths

Pitfalls:

- shared index directories
- retrieval behavior with no fixture coverage
