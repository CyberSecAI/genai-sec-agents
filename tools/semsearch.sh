#!/usr/bin/env bash
# Secure semantic search wrapper for OWASP corpus
# Implements comprehensive security controls and validation

set -euo pipefail

# Configuration
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORPUS="$ROOT/research/search_corpus"
SEARCH_TIMEOUT=${SEARCH_TIMEOUT:-10}
MAX_QUERY_LENGTH=${MAX_QUERY_LENGTH:-200}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[semsearch]${NC} $*" >&2
}

error() {
    echo -e "${RED}[semsearch ERROR]${NC} $*" >&2
}

warning() {
    echo -e "${YELLOW}[semsearch WARNING]${NC} $*" >&2
}

success() {
    echo -e "${GREEN}[semsearch]${NC} $*" >&2
}

# Security validation functions
validate_query() {
    local query="$1"
    
    # Check if query is empty
    if [[ -z "${query}" ]]; then
        error "Query cannot be empty"
        return 1
    fi
    
    # Check query length to prevent resource exhaustion
    if [[ ${#query} -gt $MAX_QUERY_LENGTH ]]; then
        error "Query too long (${#query} chars, max $MAX_QUERY_LENGTH)"
        return 1
    fi
    
    # Prevent directory traversal attempts
    if [[ "$query" == *".."* ]] || [[ "$query" == *"/"* ]] || [[ "$query" == *"\\"* ]]; then
        error "Invalid query: directory traversal patterns detected"
        return 1
    fi
    
    # Check for suspicious characters that might indicate injection attempts
    if [[ "$query" =~ [\;\|\&\`\$\(\)] ]]; then
        warning "Query contains potentially unsafe characters, proceeding with caution"
    fi
    
    # Sanitize query by removing or escaping dangerous characters
    # Allow only alphanumeric, spaces, hyphens, underscores, and dots
    if [[ ! "$query" =~ ^[a-zA-Z0-9[:space:]._-]+$ ]]; then
        error "Query contains invalid characters. Allowed: letters, numbers, spaces, dots, hyphens, underscores"
        return 1
    fi
    
    log "Query validation passed: '$query'"
    return 0
}

check_search_binary() {
    # Check if search binary is available
    if ! command -v ~/.cargo/bin/search >/dev/null 2>&1 && ! command -v search >/dev/null 2>&1; then
        error "semtools 'search' binary not found"
        error "Please install with: cargo install semtools --no-default-features --features=search"
        return 1
    fi
    
    # Use the correct search binary
    if command -v search >/dev/null 2>&1; then
        SEARCH_BINARY="search"
    else
        SEARCH_BINARY="~/.cargo/bin/search"
    fi
    
    return 0
}

build_corpus_if_needed() {
    # Check if corpus exists and is not empty
    if [[ ! -d "$CORPUS/owasp" ]] || [[ -z "$(ls -A "$CORPUS/owasp" 2>/dev/null)" ]]; then
        log "OWASP corpus not found or empty, building..."
        
        # Check if normalization script exists
        if [[ ! -f "$ROOT/tools/render_owasp_for_search.py" ]]; then
            error "Normalization script not found: $ROOT/tools/render_owasp_for_search.py"
            return 1
        fi
        
        # Build corpus with error handling
        if ! python3 "$ROOT/tools/render_owasp_for_search.py" --output "$CORPUS/owasp"; then
            error "Failed to build OWASP corpus"
            return 1
        fi
        
        success "OWASP corpus built successfully"
    else
        log "Using existing OWASP corpus"
    fi
    
    # Verify corpus has files
    local file_count=$(find "$CORPUS/owasp" -name "*.md" | wc -l)
    if [[ $file_count -eq 0 ]]; then
        error "No markdown files found in corpus directory"
        return 1
    fi
    
    log "Corpus contains $file_count files"
    return 0
}

execute_search() {
    local query="$1"
    local corpus_path="$CORPUS/owasp"
    
    # Security: Use absolute paths and validate corpus directory
    if [[ ! -d "$corpus_path" ]]; then
        error "Corpus directory not found: $corpus_path"
        return 1
    fi
    
    # Ensure we're searching only within the allowed corpus directory
    local real_corpus_path=$(realpath "$corpus_path")
    local expected_path=$(realpath "$ROOT/research/search_corpus/owasp")
    
    if [[ "$real_corpus_path" != "$expected_path" ]]; then
        error "Security violation: corpus path mismatch"
        error "Expected: $expected_path"
        error "Actual: $real_corpus_path"
        return 1
    fi
    
    log "Searching corpus at: $real_corpus_path"
    log "Query: '$query'"
    
    # Execute search with timeout and resource limits
    # Parameters aligned with story requirements:
    # --top-k 5: Return top 5 results (≤5 as per security requirements)
    # --max-distance 0.32: Distance threshold for relevance
    # --n-lines 5: Show 5 lines of context (manageable token count)
    local search_cmd
    if [[ "$SEARCH_BINARY" == *"~"* ]]; then
        search_cmd="$HOME/.cargo/bin/search"
    else
        search_cmd="$SEARCH_BINARY"
    fi
    
    # Use timeout to prevent resource exhaustion and capture output
    local search_output
    local exit_code=0
    
    search_output=$(timeout "${SEARCH_TIMEOUT}s" "$search_cmd" \
        "$query" \
        "$real_corpus_path"/*.md \
        --top-k 5 \
        --max-distance 0.32 \
        --n-lines 5 2>&1) || exit_code=$?
    
    if [[ $exit_code -ne 0 ]]; then
        if [[ $exit_code -eq 124 ]]; then
            error "Search timeout after ${SEARCH_TIMEOUT}s - query may be too complex"
        else
            error "Search failed with exit code $exit_code"
        fi
        
        log "Falling back to graceful degradation - check corpus manually"
        return 1
    fi
    
    # Display search results
    if [[ -n "$search_output" ]]; then
        echo "$search_output"
    else
        log "No results found for query: '$query'"
    fi
    
    success "Search completed successfully"
    return 0
}

show_usage() {
    cat << EOF
Usage: $0 <query>

Secure semantic search for OWASP security guidance corpus.

Arguments:
    query    Search query (max $MAX_QUERY_LENGTH characters)
             Allowed characters: letters, numbers, spaces, dots, hyphens, underscores

Environment Variables:
    SEARCH_TIMEOUT      Timeout in seconds (default: 10)
    MAX_QUERY_LENGTH    Maximum query length (default: 200)

Examples:
    $0 "jwt token validation"
    $0 "docker container security"
    $0 "session fixation prevention"
    
Security Features:
    - Input validation and sanitization
    - Directory traversal prevention
    - Resource limits (timeout, result count)
    - Path validation and access control

EOF
}

main() {
    # Parse arguments
    if [[ $# -eq 0 ]] || [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        show_usage
        return 0
    fi
    
    local query="$1"
    
    # Security validation
    if ! validate_query "$query"; then
        return 1
    fi
    
    # Check dependencies
    if ! check_search_binary; then
        return 1
    fi
    
    # Ensure corpus is available
    if ! build_corpus_if_needed; then
        return 1
    fi
    
    # Execute search
    if ! execute_search "$query"; then
        return 1
    fi
    
    return 0
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi