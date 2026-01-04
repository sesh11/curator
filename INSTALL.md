# Installation Guide

## Quick Install

### Option 1: Local Testing (Recommended for Development)

```bash
# Test the plugin without installing globally
claude --plugin-dir /path/to/curator
```

Commands will be available as `/curator:curate`.

### Option 2: Clone to Plugins Directory

```bash
# Navigate to Claude Code plugins directory
cd ~/.claude/plugins

# Clone the repository
git clone https://github.com/sesh11/curator

# That's it! Claude Code will automatically detect the plugin
```

### Option 3: Manual Installation

If you prefer manual installation or want to customize:

```bash
# 1. Copy the agent definition
cp agents/curator.md ~/.claude/agents/

# 2. Copy the command
cp commands/curate.md ~/.claude/commands/

# 3. Verify installation
ls ~/.claude/agents/curator.md
ls ~/.claude/commands/curate.md
```

## Verify Installation

Start a new Claude Code session and test:

```bash
# Check if the command is available
/curate

# You should see: "No research.md found. Would you like me to create one?"
```

## Directory Structure After Installation

```
~/.claude/
├── agents/
│   └── curator.md          # Curator agent with memory retrieval
├── commands/
│   └── curate.md           # /curate slash command
└── plugins/
    └── curator/            # Full plugin (if using Option 2)
        ├── .claude-plugin/
        ├── agents/
        ├── commands/
        └── ...
```

## First Use

### 1. Initialize Research Log

Navigate to your project directory and run:

```bash
/curate
```

This creates `research.md` in your project root with the full template structure.

### 2. Start Researching

```bash
# Research a topic
/curate context engineering for AI agents

# Add a quick note
/curate note: discovered that stateless agents simplify coordination

# Save a reference
/curate ref: https://example.com/paper - excellent overview
```

### 3. Verify Memory Retrieval

After adding a few entries, test memory retrieval:

```bash
# This should surface your past research on agents
/curate recall: what do we know about agents
```

## Hooks Installation (Optional)

The plugin includes two hooks for enhanced memory retrieval:

1. **PreCompact**: Prompts session summary before conversation compaction
2. **UserPromptSubmit**: Auto-injects relevant past research into context

### Installing Hooks

```bash
# 1. Copy hooks to your project or global directory
cp -r hooks/ ~/.claude/hooks/
# OR for project-specific: cp -r hooks/ .claude/hooks/

# 2. Make scripts executable
chmod +x ~/.claude/hooks/pre-compact.sh
chmod +x ~/.claude/hooks/memory-retrieval.py

# 3. Add hook configuration to your settings
```

### Settings Configuration

Add to `~/.claude/settings.json` (global) or `.claude/settings.json` (project):

```json
{
  "hooks": {
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/hooks/pre-compact.sh"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/hooks/memory-retrieval.py"
          }
        ]
      }
    ]
  }
}
```

### What the Hooks Do

**PreCompact Hook** (`pre-compact.sh`):
- Triggers before conversation compaction (200+ messages or manual `/compact`)
- Prompts Claude to add a session summary to research.md
- Preserves topics researched, insights, and open questions

**Memory Retrieval Hook** (`memory-retrieval.py`):
- Triggers only on prompts with **curation intent** (research, ideas, references, updates)
- Skips regular coding/debugging prompts
- Searches research.md for entries matching keywords/tags in your prompt
- Injects top 3 matches as context: `[Curator] Related past research found: ...`
- Enables automatic memory recall without explicit `/curator:curate recall:` commands

---

## Configuration (Optional)

### Custom Tags

Edit `~/.claude/agents/curator.md` to add domain-specific tags:

```markdown
**Domain Tags** (auto-detect from context):
- `#your-domain` - Your custom domain
- `#your-tech` - Your technology stack
```

### Project-Specific Research Location

By default, `research.md` is created in the project root. The curator will:
- Check for existing `research.md` in current directory
- Create one if it doesn't exist
- Auto-detect project name from git or directory name

## Updating the Plugin

```bash
cd ~/.claude/plugins/curator
git pull origin main
```

Or if manually installed:

```bash
# Re-copy updated files
cp path/to/curator/agents/curator.md ~/.claude/agents/
cp path/to/curator/commands/curate.md ~/.claude/commands/
```

## Uninstalling

```bash
# Remove agent and command
rm ~/.claude/agents/curator.md
rm ~/.claude/commands/curate.md

# Remove plugin directory (if using Option 2)
rm -rf ~/.claude/plugins/curator
```

Note: Your `research.md` files in project directories are preserved.

## Troubleshooting

### Command Not Found

If `/curate` doesn't work:

1. Check file exists: `ls ~/.claude/commands/curate.md`
2. Restart Claude Code session
3. Ensure file has correct YAML frontmatter

### Agent Not Invoked

If the curator agent isn't being used:

1. Check agent exists: `ls ~/.claude/agents/curator.md`
2. Verify YAML frontmatter is valid
3. Try explicit invocation: `/curate [topic]`

### Memory Retrieval Not Working

If past research isn't being surfaced:

1. Verify `research.md` exists in current project
2. Check entries have proper tags
3. Ensure entries follow the expected markdown structure

## Support

- Issues: [GitHub Issues](https://github.com/sesh11/curator/issues)
- Discussions: [GitHub Discussions](https://github.com/sesh11/curator/discussions)
