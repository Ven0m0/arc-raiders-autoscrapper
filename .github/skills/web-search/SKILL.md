---
name: web-search
description: Search web content using Exa advanced search across categories - personal sites/blogs, research papers, and tweets/X. Use when searching for web content, academic papers, blog posts, or social media discussions.
context: fork
agent: general-purpose
---

# Web Search (Exa Advanced)

## Tool Restriction

ONLY use `web_search_advanced_exa`. Select the `category` parameter based on
search type: `"personal site"`, `"research paper"`, or `"tweet"`.

## Token Isolation

Never run Exa searches in main context. Always spawn Task agents:

- Agent calls `web_search_advanced_exa` with the appropriate category
- Agent merges and deduplicates results before presenting
- Agent returns distilled output (brief markdown or compact JSON)
- Main context stays clean regardless of search volume

## Personal Sites & Blogs

Category: `"personal site"`. Full filter support.

Use when you need:

- Individual expert opinions and experiences
- Personal blog posts on technical topics
- Portfolio websites
- Independent analysis (not corporate content)
- Deep dives and tutorials from practitioners

Example - technical blog posts:

```
web_search_advanced_exa {
  "query": "building production LLM applications lessons learned",
  "category": "personal site",
  "numResults": 15,
  "type": "deep",
  "enableSummary": true
}
```

Example - exclude aggregators:

```
web_search_advanced_exa {
  "query": "startup founder lessons",
  "category": "personal site",
  "excludeDomains": ["medium.com", "substack.com"],
  "numResults": 15,
  "type": "auto"
}
```

## Research Papers

Category: `"research paper"`. Full filter support.

Use when you need:

- Academic papers from arXiv, OpenReview, PubMed, and similar sources
- Scientific research on specific topics
- Literature reviews with date filtering
- Papers containing specific methodologies or terms

Example - recent papers:

```
web_search_advanced_exa {
  "query": "transformer attention mechanisms efficiency",
  "category": "research paper",
  "startPublishedDate": "2024-01-01",
  "numResults": 15,
  "type": "auto"
}
```

Example - specific venues:

```
web_search_advanced_exa {
  "query": "large language model agents",
  "category": "research paper",
  "includeDomains": ["arxiv.org", "openreview.net"],
  "includeText": ["LLM"],
  "numResults": 20,
  "type": "deep"
}
```

## Tweets & X Content

Category: `"tweet"`. LIMITED filter support.

**Critical:** The following parameters are NOT supported for tweets and will
cause errors (400 or 500):

- `includeText` - NOT SUPPORTED
- `excludeText` - NOT SUPPORTED
- `includeDomains` - NOT SUPPORTED
- `excludeDomains` - NOT SUPPORTED
- `moderation` - NOT SUPPORTED (causes 500 server error)

Put keyword constraints in the `query` string instead of text/domain filters.
Use date filters to narrow results.

Use when you need:

- Social discussions on a topic
- Product announcements from company accounts
- Developer opinions and experiences
- Trending topics and community sentiment
- Expert takes and threads

Example - recent tweets:

```
web_search_advanced_exa {
  "query": "Claude Code MCP experience",
  "category": "tweet",
  "startPublishedDate": "2025-01-01",
  "numResults": 20,
  "type": "auto",
  "livecrawl": "preferred"
}
```

Example - keywords in query (not includeText):

```
web_search_advanced_exa {
  "query": "launching announcing new open source release",
  "category": "tweet",
  "startPublishedDate": "2025-12-01",
  "numResults": 15,
  "type": "auto"
}
```

## Common Parameters

Parameters shared across all categories:

### Core

- `query` (required)
- `numResults`
- `type` - `"auto"`, `"fast"`, `"deep"`, `"neural"`

### Date filtering (ISO 8601)

- `startPublishedDate` / `endPublishedDate`
- `startCrawlDate` / `endCrawlDate`

### Content extraction

- `textMaxCharacters` / `contextMaxCharacters`
- `enableSummary` / `summaryQuery`
- `enableHighlights` / `highlightsNumSentences` / `highlightsPerUrl` /
  `highlightsQuery`

### Additional (personal site and research paper only)

- `includeDomains` / `excludeDomains`
- `includeText` / `excludeText` - single-item arrays only; multi-item arrays
  (2+ items) cause 400 errors; use `query` for multiple terms
- `additionalQueries`
- `livecrawl` / `livecrawlTimeout`
- `subpages` / `subpageTarget`

## Output Format

For all categories, return:

1. Results - title, author/source, date, key insights or summary
2. Sources - URLs with context (venue for papers, handle for tweets)
3. Notes - relevant observations (author expertise, methodology, sentiment)

## Related

- `skills/code-search/` — Use for code snippets, API examples, and SDK usage via `get_code_context_exa`
