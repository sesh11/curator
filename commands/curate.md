---
description: Curate knowledge and maintain research.md using the curator agent
argument-hint: [topic or query]
---

# Curate Command

Use the curator agent to investigate the following topic and update the project's research.md file.

**Topic/Query**: $ARGUMENTS

## Instructions for curator:

### Memory Retrieval First
Before any action, search research.md for related past entries:
- Look for matching tags and keywords
- Surface relevant past findings
- Identify knowledge gaps

### Then, based on the query:

1. **If $ARGUMENTS is empty**:
   - Show current research status from research.md
   - Summarize Active Research topics
   - List recent Research Log entries

2. **If $ARGUMENTS is a topic/question**:
   - Search for related past research first
   - Present related findings to user
   - Conduct new research focusing on gaps
   - Cross-reference with past entries

3. **If $ARGUMENTS starts with "note:"**:
   - Add as quick research log entry
   - Search for related past entries
   - Add Related links if applicable

4. **If $ARGUMENTS starts with "ref:"**:
   - Add as reference only
   - Categorize appropriately
   - Link to related research entries

5. **If $ARGUMENTS starts with "idea:"**:
   - Add to Ideas & Future Research
   - Tag appropriately
   - Note connections to existing research

6. **If $ARGUMENTS starts with "update:"**:
   - Update existing research entry
   - Maintain cross-references
   - Log the update in Research Log

7. **If $ARGUMENTS starts with "recall:" or "what do we know about"**:
   - Pure memory retrieval mode
   - Search and present all related past entries
   - No new research, just surface existing knowledge

8. **If $ARGUMENTS starts with "extend:" or "build on"**:
   - Find the referenced past research
   - Conduct new research that extends it
   - Add explicit Builds On reference
   - Update original entry with forward link

Provide a clear summary of:
- What related past research was found
- What was added/updated in research.md
- How new findings connect to existing knowledge
