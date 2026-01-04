#!/usr/bin/env python3
"""
Memory Retrieval Hook for Curator Plugin

INTENT-BASED TRIGGERING:
Only activates for curation-related prompts:
- Research requests ("research X", "find information about", "what do we know")
- Brainstorming/ideas ("idea:", "brainstorm", "what if we")
- Saving references ("save this", "ref:", URLs)
- Updating research ("update:", "note:", "mark completed")

Skips general coding, debugging, or non-curation prompts.

Input (via stdin): JSON with 'prompt' and 'cwd' fields
Output (via stdout): JSON with 'hookSpecificOutput.additionalContext' if matches found
"""

import json
import sys
import re
import os


# =============================================================================
# INTENT DETECTION PATTERNS
# =============================================================================

RESEARCH_PATTERNS = [
    r'\bresearch\b',
    r'\bfind information\b',
    r'\blook up\b',
    r'\bwhat.s the latest\b',
    r'\bcurate\b',
    r'\bwhat do we know\b',
    r'\bwhat have we learned\b',
    r'\binvestigate\b',
    r'\bexplore\b.*\btopic\b',
    r'\bdig into\b',
    r'\blearn about\b',
]

IDEA_PATTERNS = [
    r'\bdocument this idea\b',
    r'\bbrainstorm\b',
    r'\bi.m thinking about\b',
    r'\bi am thinking about\b',
    r'^idea:',
    r'\bwhat if we\b',
    r'\bcapture this\b',
    r'\bnote this\b',
    r'\brecord this\b',
    r'\bjot down\b',
]

REFERENCE_PATTERNS = [
    r'\bsave this\b',
    r'\badd this to research\b',
    r'\bsave.*reference\b',
    r'^ref:',
    r'https?://\S+',  # URLs always trigger (user confirmed)
    r'\btrack this\b',
    r'\bbookmark\b',
    r'\bkeep this\b',
]

UPDATE_PATTERNS = [
    r'\bupdate research\b',
    r'\bmark.*completed\b',
    r'\bmark.*done\b',
    r'^update:',
    r'^note:',
    r'\bupdate.*status\b',
    r'\bcomplete.*research\b',
    r'\bfinish.*research\b',
]


def has_curation_intent(prompt: str) -> bool:
    """
    Check if prompt has curation-related intent.
    Returns True if the prompt matches any curation pattern.
    """
    prompt_lower = prompt.lower().strip()

    all_patterns = (
        RESEARCH_PATTERNS +
        IDEA_PATTERNS +
        REFERENCE_PATTERNS +
        UPDATE_PATTERNS
    )

    for pattern in all_patterns:
        if re.search(pattern, prompt_lower):
            return True

    return False


# =============================================================================
# KEYWORD AND TAG EXTRACTION
# =============================================================================

STOPWORDS = {
    'this', 'that', 'what', 'about', 'with', 'have', 'from', 'they',
    'been', 'were', 'being', 'their', 'there', 'would', 'could', 'should',
    'which', 'these', 'those', 'your', 'into', 'more', 'some', 'such',
    'only', 'other', 'than', 'then', 'them', 'does', 'doing', 'done',
    'will', 'just', 'also', 'like', 'make', 'want', 'need', 'know',
    'think', 'look', 'find', 'help', 'show', 'tell', 'give', 'take',
    'come', 'work', 'first', 'after', 'before', 'because', 'through',
    'research', 'save', 'update', 'note', 'idea', 'curate', 'track',
}


def extract_keywords(text: str, min_length: int = 4) -> list[str]:
    """Extract meaningful keywords from text."""
    words = re.findall(r'\b\w{%d,}\b' % min_length, text.lower())
    return [w for w in words if w not in STOPWORDS]


def extract_tags(text: str) -> list[str]:
    """Extract hashtags from text."""
    return re.findall(r'#(\w+)', text.lower())


# =============================================================================
# RESEARCH.MD SEARCH
# =============================================================================

def search_research_md(content: str, keywords: list[str], tags: list[str]) -> list[tuple[int, str]]:
    """
    Search research.md content for matching sections.
    Returns list of (score, title) tuples sorted by relevance.
    """
    matches = []

    # Split by ### headers (Research Log entries and Active/Completed research items)
    sections = re.split(r'^### ', content, flags=re.MULTILINE)

    for section in sections:
        if not section.strip():
            continue

        section_lower = section.lower()

        # Score based on keyword matches (2 points each)
        keyword_score = sum(2 for kw in keywords if kw in section_lower)

        # Score based on tag matches (3 points each - weighted higher)
        section_tags = extract_tags(section)
        tag_score = sum(3 for tag in tags if tag in section_tags)

        total_score = keyword_score + tag_score

        if total_score > 0:
            # Extract title (first line, truncated)
            title = section.split('\n')[0][:80].strip()
            if title:
                matches.append((total_score, title))

    # Sort by score descending
    matches.sort(reverse=True, key=lambda x: x[0])
    return matches


# =============================================================================
# MAIN
# =============================================================================

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    prompt = input_data.get('prompt', '')
    cwd = input_data.get('cwd', '')

    if not prompt or not cwd:
        sys.exit(0)

    # EARLY EXIT: Skip if no curation intent
    if not has_curation_intent(prompt):
        sys.exit(0)

    # Look for research.md in project directory
    research_path = os.path.join(cwd, 'research.md')
    if not os.path.exists(research_path):
        sys.exit(0)

    # Extract keywords and tags from prompt
    keywords = extract_keywords(prompt)
    tags = extract_tags(prompt)

    if not keywords and not tags:
        sys.exit(0)

    # Read and search research.md
    try:
        with open(research_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (IOError, OSError):
        sys.exit(0)

    matches = search_research_md(content, keywords, tags)

    if not matches:
        sys.exit(0)

    # Take top 3 matches
    top_matches = [m[1] for m in matches[:3]]

    # Output context for Claude
    context = f"[Curator] Related past research found: {', '.join(top_matches)}"

    print(json.dumps({
        "hookSpecificOutput": {
            "additionalContext": context
        }
    }))

    sys.exit(0)


if __name__ == '__main__':
    main()
