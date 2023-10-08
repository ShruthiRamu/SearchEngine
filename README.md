# Text-Based Dataset Search Engine

Welcome to the Text-Based Dataset Search Engine project! This search engine is designed to handle large-scale text-based datasets using positional inverted indexing and ranked retrievals. It offers powerful features to efficiently search and retrieve information from your dataset.

## Key Features

### 1. Indexing Documents
- **User-Friendly**: Our search engine is user-friendly and easy to use. It starts by asking the user for the name of the directory to index.
- **Document Loading**: Once the directory is provided, the search engine loads all the documents in that directory.
- **Index Construction**: It then constructs a positional inverted index with the contents of these documents. This index allows for fast and efficient searching.

### 2. Boolean Search Queries
- **Boolean Queries**: Users can input Boolean search queries, allowing them to find documents that match specific criteria.
- **Powerful Filtering**: This feature enables powerful filtering and retrieval of documents based on Boolean logic.

### 3. Ranked Retrieval Queries
- **Ranked Retrieval**: The search engine also supports ranked retrieval queries.
- **Relevance Ranking**: Users can search for documents based on relevance, and the engine will return results ranked by relevance.
- **Disk-Based Index**: Ranked retrieval queries are processed on the disk-based inverted index, ensuring efficient performance even for large datasets.
