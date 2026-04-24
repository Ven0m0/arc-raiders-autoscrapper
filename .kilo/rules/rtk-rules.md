# RTK - Rust Token Killer (Kilo Code)

**Usage**: Token-optimized CLI proxy for shell commands.

## Rule

Always prefix shell commands with `rtk` to minimize token consumption.

Examples:

```bash
rtk git status
rtk cargo test
rtk ls src/
rtk grep "pattern" src/
rtk find "*.rs" .
rtk docker ps
rtk gh pr list
```

## Meta Commands

rtk gain # Show token savings
rtk gain --history # Command history with savings
rtk discover # Find missed RTK opportunities
rtk proxy COMMAND # Run raw (no filtering, for debugging)

## Why

RTK filters and compresses command output before it reaches the LLM context, saving 60-90% tokens on common operations. Always use `rtk COMMAND` instead of raw commands.
