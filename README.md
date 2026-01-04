# Claude Curator Plugin

A knowledge curation agent for Claude Code with **memory retrieval** that surfaces past learnings based on current context.

## Acknowledgments

This plugin was inspired by [claude-diary](https://github.com/rlancemartin/claude-diary) by Lance Martin, which demonstrates long-term memory management through diary entries and reflection. The curator plugin adapts similar concepts for research curation with intent-based triggering and cross-referenced knowledge building.

## Overview

The Curator plugin helps you maintain organized, searchable research logs across your projects. Unlike simple note-taking, it builds a knowledge graph through cross-references and always consults past research before conducting new investigations.

### Key Features

- **Memory Retrieval**: Automatically surfaces relevant past research before new investigations
- **Hooks**: Optional hooks for passive memory retrieval and session summaries
- **Cross-Referencing**: Links related entries with `Related` and `Builds On` fields
- **Structured Knowledge**: Maintains `research.md` with Active Research, Completed Research, Research Log, Ideas, and References
- **Tag-Based Organization**: Consistent tagging for easy retrieval
- **Gap Detection**: Identifies what's known vs what needs new research

## Architecture

```
curator/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── agents/
│   └── curator.md           # Curator agent with memory retrieval
├── commands/
│   └── curate.md            # /curate slash command
├── hooks/
│   ├── pre-compact.sh       # Session summary before compaction
│   ├── memory-retrieval.py  # Intent-based memory retrieval
│   └── settings.json        # Example hook configuration
├── examples/
│   └── sample-research.md   # Example research.md structure
├── README.md
├── INSTALL.md
└── LICENSE
```

## How It Works

### Memory Retrieval Flow

```
User: /curate agent coordination patterns

                    ↓

┌─────────────────────────────────────────────────────────┐
│ 1. MEMORY RETRIEVAL (Always First)                      │
│    - Extract concepts: [agent, coordination, patterns]  │
│    - Search research.md by tags and keywords            │
│    - Rank by: tag match > keyword > recency             │
│    - Surface top 3-5 related entries                    │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ 2. GAP IDENTIFICATION                                   │
│    - What's already known from past research?           │
│    - What knowledge gaps remain?                        │
│    - Present to user for confirmation                   │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ 3. FOCUSED RESEARCH                                     │
│    - WebSearch targeting identified gaps                │
│    - WebFetch for detailed extraction                   │
│    - Synthesize with awareness of past findings         │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ 4. CROSS-REFERENCED UPDATE                              │
│    - Add new entry with Related links                   │
│    - Include Builds On references                       │
│    - Update past entries with forward links             │
│    - Maintain tag index                                 │
└─────────────────────────────────────────────────────────┘
```

### Example Session

```
User: /curate agent coordination patterns

Curator:
I found related research in your knowledge base:

1. **Context Engineering for Multi-Agent Systems** (2025-12-15) - Active Research
   Key insight: Context passing can replace explicit coordination in some cases
   Tags: #agent #context #architecture

2. **Stateless Agent Design** (2025-12-10) - Completed Research
   Key insight: Stateless agents with shared context eliminate coordination overhead
   Tags: #agent #architecture #stateless

Based on this, I'll focus new research on:
- Explicit coordination mechanisms (not covered by past research)
- Cases where context-passing isn't sufficient
- Hybrid approaches

[Conducts focused research...]

Added to Active Research:
- **Explicit Agent Coordination Mechanisms** (2026-01-02)
- Related: Context Engineering, Stateless Agents
- Builds On: Past work showed context-passing works for shared state;
  this covers cases where explicit coordination is still needed
```

## Usage

### Basic Commands

When loaded via `--plugin-dir`, commands are namespaced as `/curator:curate`:

```bash
# Research a topic (with memory retrieval)
/curator:curate agent coordination patterns

# Show current research status
/curator:curate

# Quick note (auto-links to related research)
/curator:curate note: context engineering eliminates coordination in some cases

# Save a reference
/curator:curate ref: https://example.com/paper - great overview of patterns

# Capture an idea for later
/curator:curate idea: explore graph-based knowledge representation

# Update existing research
/curator:curate update: mark context engineering as completed

# Pure memory retrieval (no new research)
/curator:curate recall: what do we know about stateless agents

# Extend past research
/curator:curate extend: stateless agents - what about hybrid approaches?
```

> **Note**: If installed globally to `~/.claude/plugins/`, the command may be available as just `/curate`.

### Natural Language Triggers

The curator activates automatically for:
- "Research [topic]"
- "Find information about [topic]"
- "What's the latest on [topic]?"
- "What do we know about [topic]?"
- "Build on [past topic]"
- "Document this idea"

## research.md Structure

Each project maintains a `research.md` with:

```markdown
# Research Log

> Project: my-project
> Started: 2025-12-01
> Last Updated: 2026-01-02

## Active Research
[Ongoing investigations with status, findings, next steps]

## Completed Research
[Archived research with conclusions and key insights]

## Research Log
[Chronological record of all activities - newest first]

## Ideas & Future Research
[Parking lot for future exploration]

## References Library
[Categorized references with By Category and By Tag indices]
```

### Cross-Reference Fields

New in this version:

```markdown
### 2026-01-02 10:30 - Agent Coordination Patterns
**Tags**: #agent #coordination #patterns
**Type**: Research
**Related**: [Context Engineering](#2025-12-15), [Stateless Agents](#2025-12-10)
**Builds On**: Previous research on context-passing; extends to explicit coordination cases

[Content...]
```

## Hooks (Optional)

The plugin includes two hooks for **automatic memory retrieval** without explicit commands:

### PreCompact Hook

**Trigger**: Before conversation compaction (200+ messages or manual `/compact`)

**Behavior**: Prompts Claude to add a session summary to research.md, preserving:
- Topics researched this session
- Key insights discovered
- References added
- Open questions to continue next session

### UserPromptSubmit Hook

**Trigger**: Only prompts with **curation intent** (not every prompt)

**Intent patterns that trigger the hook**:

| Category | Patterns |
|----------|----------|
| **Research** | "research X", "find information about", "look up", "what's the latest", "curate", "what do we know" |
| **Ideas** | "idea:", "brainstorm", "I'm thinking about", "what if we", "document this idea" |
| **References** | "save this", "ref:", any URL, "add this to research", "track this" |
| **Updates** | "update:", "note:", "mark completed", "update research" |

**Non-triggers** (examples):
- "Fix the bug in main.py" - coding task
- "Run the tests" - command
- "What does this function do?" - code question

**Behavior when triggered**:
1. Extracts keywords from your prompt
2. Searches research.md for matching entries (by tags and content)
3. Injects top 3 matches as context: `[Curator] Related past research found: ...`

### Example

```
You: "Research agent coordination patterns"

[Hook detects "research" intent, searches research.md, finds matches]

Claude sees: "[Curator] Related past research found: Agent Coordination Patterns,
Context Engineering for Multi-Agent Systems, Stateless Agent Design"

Claude: "Based on your past research on agent coordination..."
```

```
You: "Fix the authentication bug"

[Hook detects NO curation intent, exits silently]

Claude: Proceeds with bug fix without curator context
```

See [INSTALL.md](INSTALL.md) for hook installation instructions.

---

## Technical Details

### Memory Retrieval Algorithm

1. **Concept Extraction**: Parse query into key terms and related concepts
2. **Tag Search**: Grep for exact and related tag matches
3. **Keyword Search**: Search titles and content
4. **Relevance Ranking**:
   - Exact tag match: highest weight
   - Related tag match: high weight
   - Keyword in title: medium weight
   - Keyword in content: lower weight
   - Recency bonus for fast-moving topics
5. **Threshold**: Surface entries with relevance score above threshold

### Tag Taxonomy

**Universal**: `#research`, `#reference`, `#idea`, `#insight`, `#note`

**Domain**: `#architecture`, `#security`, `#performance`, `#api`, `#ml`, `#agents`, `#context`, `#devops`, `#testing`, `#ux`

**Technology**: `#python`, `#typescript`, `#claude`, etc.

**Status**: `#active`, `#completed`, `#blocked`, `#validated`

## Comparison: Before vs After

| Aspect | Before (Basic Curator) | After (With Memory Retrieval) |
|--------|------------------------|------------------------------|
| **Research Start** | Fresh search every time | Search past research first |
| **Knowledge Building** | Isolated entries | Cross-referenced graph |
| **Duplicate Prevention** | Manual | Automatic gap detection |
| **Context Awareness** | None | Surfaces relevant past work |
| **Entry Structure** | Basic | Related + Builds On fields |

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

### Quick Start (Local Testing)

```bash
claude --plugin-dir /path/to/curator
```

### Global Installation

```bash
cd ~/.claude/plugins
git clone https://github.com/sesh11/curator
```

## Limitations

- **Single Project Scope**: research.md is per-project by design
- **Tag Fragmentation**: No automatic consolidation of similar tags (#ml vs #machine-learning)
- **Flat Structure**: Markdown-based, not a true knowledge graph
- **Manual Archiving**: Large files require manual archive decision

## Future Improvements

- **Cross-Project Memory**: Optional global research index
- **Tag Normalization**: Automatic consolidation of similar tags
- **Confidence Scoring**: Weight sources by credibility
- **Contradiction Detection**: Flag conflicting findings
- **Knowledge Graph Backend**: Graph structure rendered as markdown

## License

MIT
