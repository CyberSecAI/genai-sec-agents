# semsearch

Perform semantic search over security standards using semtools.

## Usage

```
/semsearch <query> [--corpus <path>] [--limit <n>] [--distance <float>]
```

## Parameters

- `query` (required): Search query for semantic matching
- `--corpus <path>`: Corpus directory to search (default: research/search_corpus/owasp)
- `--limit <n>`: Maximum results to return (default: 5, max: 10)  
- `--distance <float>`: Maximum semantic distance (default: 0.32, range: 0.0-1.0)

## Examples

```bash
# Basic search in default OWASP corpus
/semsearch "jwt token validation"

# Search specific corpus
/semsearch "input validation" --corpus research/search_corpus/asvs

# Search with custom parameters
/semsearch "docker security" --limit 3 --distance 0.25

# Search entire security corpus
/semsearch "session management" --corpus research/search_corpus
```

## Output Format

Returns structured results with:
- **File path**: Location in corpus
- **Relevance score**: Semantic similarity (lower = better match)
- **Context**: 5 lines around the match with highlighting
- **Metadata**: Security domains and source information when available

## Security Features

- Input validation prevents injection attacks
- Path validation restricts access to authorized directories
- Query length limits prevent resource exhaustion
- Timeout controls prevent long-running searches

## Performance

- Target response time: <1 second for standard queries
- Configurable result limits for performance control
- Efficient semantic matching using semtools binary

## Available Corpuses

- `research/search_corpus/owasp` - OWASP CheatSheets (101 files)
- `research/search_corpus/asvs` - ASVS verification standards (17 files)  
- `research/search_corpus` - Complete security corpus (219 files)
- Custom corpus directories containing processed markdown files