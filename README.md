# Building a Knowledge Curation Agent in Claude Code

## Overview

The curator agent is a custom AI agent built on Claude Code's extensible agent framework, designed to solve a fundamental problem in AI-assisted research: **how to maintain coherent, searchable knowledge across evolving research projects without manual knowledge management overhead**.

## Architecture

### Component Breakdown

The system consists of three interconnected components:

1. **Custom Agent Definition** (`~/.claude/agents/curator.md`)
2. **Slash Command Interface** (`~/.claude/commands/curate.md`)
3. **Structured Knowledge Base** (`research.md` per project)

### 1. Custom Agent Definition

Claude Code allows users to define custom agents using markdown files in `~/.claude/agents/`. Each agent definition uses YAML frontmatter:

```yaml
---
name: curator
description: Knowledge curator for conducting web research, organizing findings chronologically with tags, and maintaining research.md files. Use proactively when users ask to research topics, find information, track references, or document ideas. MUST BE USED for any research-related tasks.
tools: Read, Write, Edit, Grep, Glob, Bash, WebSearch, WebFetch
model: sonnet
---
```

**Key Components:**
- **`name`**: Identifier used when invoking the agent
- **`description`**: Injected into Claude's system prompt for automatic discovery
- **`tools`**: Grants access to specific capabilities (file operations, web search, etc.)
- **`model`**: Uses Claude Sonnet 4.5 for cost-efficiency

When Claude Code initializes, it automatically scans `~/.claude/agents/` and makes custom agents available.

The body of `curator.md` contains the agent's operational instructions, defining a 6-step workflow:

```
1. Initialize → 2. Understand Request → 3. Conduct Research →
4. Organize & Tag → 5. Update research.md → 6. Provide Summary
```

### 2. Workflow & Invocation

The curator can be triggered in two ways:

**Explicit Invocation:**
```bash
/curate find me the top 5 articles on context engineering
```

**Implicit Invocation:**
The agent description includes "MUST BE USED for any research-related tasks," which creates semantic triggers. When Claude detects research-related queries ("research X", "find information about Y", "track this reference"), it proactively invokes the curator without requiring the explicit `/curate` command.

**Request Classification:**

The agent classifies incoming requests to determine execution path:
- **Quick Note**: Recording thoughts (`"note: ..."`)
- **Deep Research**: Comprehensive investigation requiring web search
- **Reference Addition**: Saving a link (`"ref: ..."`)
- **Idea Capture**: Future research topics (`"idea: ..."`)
- **Status Update**: Modifying existing research (`"update: ..."`)

### 3. Slash Command Interface

The `/curate` command provides structured access via `~/.claude/commands/curate.md`:

```markdown
---
name: curate
argument-hint: [topic or query]
description: Curate knowledge and maintain research.md using the curator agent
---

**Topic/Query**: $ARGUMENTS

## Instructions for curator:

1. If $ARGUMENTS is empty, show current research status from research.md
2. If $ARGUMENTS is a topic/question, conduct thorough research
3. If $ARGUMENTS starts with "note:", add as quick research log entry
4. If $ARGUMENTS starts with "ref:", add as reference only
5. If $ARGUMENTS starts with "idea:", add to Ideas & Future Research
6. If $ARGUMENTS starts with "update:", update existing research entry
```

**The `$ARGUMENTS` Pattern:**

When a user types `/curate [arguments]`, Claude Code expands the command and substitutes `$ARGUMENTS` with user input. This creates a **two-phase dispatch**:
- Phase 1: Slash command expansion (substitutes variables)
- Phase 2: Agent invocation (Claude executes based on expanded prompt)

The prefix-based routing (`note:`, `ref:`, `idea:`, `update:`) allows for mode selection without complex parsing.

### 4. The research.md Schema

The knowledge base follows a strict schema with five top-level sections:

```markdown
# Research Log

> Project: [Auto-detected]
> Started: [YYYY-MM-DD]
> Last Updated: [YYYY-MM-DD]

## Active Research
### [Topic Name]
- **Status**: In Progress | Needs Validation | Blocked
- **Started**: YYYY-MM-DD
- **Tags**: #tag1 #tag2
- **Question/Objective**: ...
**Findings So Far**: ...
**Next Steps**: ...
**References**: ...

## Completed Research
[Same structure but with completion date and duration]

## Research Log
### YYYY-MM-DD HH:MM - [Title]
**Tags**: #tag1 #tag2
**Type**: Note | Research | Reference | Idea | Insight
Content...
**Sources**: [Title](URL)

## Ideas & Future Research
- **Idea**: Description [#tags]
- **Question**: What about X? [#tags]

## References Library
### By Category
#### [Category Name]
- [Source Title](URL) - Description

### By Tag
- **#tag1**: Entry 1, Entry 2, Entry 3
```

**Design Rationale:**
- **Separation of Concerns**: Active vs Completed separates current focus from historical context
- **Dual Indexing**: Chronological (Research Log) and categorical (References Library) views
- **Machine-Readable**: Structured format enables programmatic querying
- **Human-Readable**: Markdown ensures git-friendliness and editor compatibility

## Technical Invocation Flow

**Complete end-to-end execution:**

```
User: /curate find me the top 5 articles on context engineering

↓ [Claude Code expands slash command, substitutes $ARGUMENTS]

Claude receives expanded prompt with topic inserted

↓ [Claude analyzes and invokes Task tool]

Task(
  subagent_type="curator",
  description="Research context engineering articles",
  prompt="Research and find the top 5 articles..."
)

↓ [Curator agent executes 6-step workflow]

Curator:
1. WebSearch("context engineering LLMs 2025")
2. WebFetch(top_results)
3. Synthesize findings
4. Read research.md
5. Update research.md (add to Research Log, References, Active Research)
6. Return summary

↓ [Claude presents summary to user + updated research.md]
```


## Technical Innovations

### 1. Stateless Agent with Persistent Context

The curator is **stateless** (no session memory between invocations) but maintains **persistent context** via research.md. This demonstrates that stateless agents + proper context = powerful, composable primitives.

**Benefits:**
- **Composability**: Invoke from any project, any time
- **Debuggability**: All state is explicit in research.md (git-trackable)
- **Cost-Efficiency**: No session overhead; only pay for active research
- **Cacheable**: Repeated queries can leverage prompt caching on research.md content

### 2. Multi-Modal Tagging as Retrieval Index

Instead of vector embeddings, the curator uses structured tags:

```
Universal Tags + Domain Tags + Technology Tags + Status Tags
```

This creates a **symbolic index** that's human-readable, git-diffable, and queryable with simple grep/search.

### 3. Dual-Timeline Architecture

Maintains two timelines:
1. **Logical Timeline**: Active Research → Completed Research (task-oriented)
2. **Chronological Timeline**: Research Log (time-oriented)

Supports both "What am I working on now?" and "What did I learn yesterday?" without choosing one approach.

## Limitations

### 1. **No Automatic Summarization/Archiving**
- research.md grows unbounded (current: 890 lines)
- Agent suggests archiving at 1000+ lines but doesn't execute
- Requires user decision on what to archive

### 2. **Limited Cross-Project Intelligence**
- Each project has isolated research.md
- No global view across all research
- Intentional design choice (keeps context focused)

### 3. **Tag Fragmentation**
- No automated tag consolidation (#ml vs #machine-learning vs #ML)
- Current mitigation: Agent guidelines to use established tags

### 4. **Flat Structure vs Graph-Based Needs**
- Current: Markdown with tags (flat hierarchy)
- Reality: Research has complex relationships (contradicts, supports, extends, relates_to)
- **Need**: Knowledge graph backend with research.md as rendered view
  - Nodes: Concepts, Articles, Insights, Hypotheses
  - Edges: Semantic relationships
  - Benefits: Traversal queries, contradiction detection, concept evolution tracking

### 5. **Single-Threaded Research**
- Can only research one topic at a time
- "Research X, Y, and Z" becomes sequential

### 6. **No Quality Scoring**
- All sources treated equally
- Blog post has same weight as peer-reviewed paper
- Current: Manual filtering via source hierarchy

## Future Improvements

### Context Assembly Pipeline

Current: Single-phase research (WebSearch → synthesize)

Proposed:
```
1. Query Decomposition: Break into subqueries
2. Parallel Retrieval: Search multiple sources concurrently
3. Relevance Ranking: Score by credibility + recency + relevance
4. Synthesis: Merge results, identify contradictions
5. Structured Output: Generate update with confidence scores
```

### Automatic Hypothesis Testing

Current: Curator logs hypotheses but doesn't test them

Proposed:
```markdown
## Ideas & Future Research
- **Hypothesis**: Stateless agents + context = interoperability primitive
  - **Status**: Testable
  - **Test Plan**: Build workflow with stateful (OpenAI) vs stateless (Anthropic)
  - **Metrics**: Code complexity, cost, latency
  - **Trigger**: /curate test-hypothesis "stateless agents"
```

Curator could generate test plans, execute experiments, log results automatically.

### Knowledge Graph Backend

Transform flat markdown into graph structure:

```
research.md (user-facing) ← rendered from → knowledge graph (backend)

Nodes: Concepts, Articles, Insights, Hypotheses
Edges: "relates_to", "contradicts", "supports", "extends"

Benefits:
- Query: "Show all concepts related to context engineering"
- Traverse: "What led to the stateless agents hypothesis?"
- Detect: "Are there contradictions in my research?"
```

Implementation: Embed graph in research.md as YAML frontmatter, render as markdown for readability.

---

