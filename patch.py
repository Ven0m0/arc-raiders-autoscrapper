with open('src/autoscrapper/progress/update_report.py', 'r') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith('def graph_gap_report('):
        start_idx = i
    if start_idx != -1 and line.startswith('def _render_item_list('):
        end_idx = i
        break

new_code = """def graph_gap_report(quests: Sequence[object], quest_graph: Mapping[str, object]) -> dict:
    nodes = quest_graph.get("nodes")
    node_values = nodes.values() if isinstance(nodes, dict) else []

    # Cache to prevent repeated expensive normalization operations
    matched_cache = {}
    def get_normalized(name):
        if name not in matched_cache:
            matched_cache[name] = normalize_quest_name(name)
        return matched_cache[name]

    node_names_normalized = {
        name for node_name in node_values if (name := get_normalized(node_name))
    }

    quest_entries: list[dict[str, Any]] = [cast(dict[str, Any], quest) for quest in quests if isinstance(quest, dict)]
    quest_names_normalized = set()

    missing_quests: list[dict] = []
    for quest in quest_entries:
        quest_name = get_normalized(quest.get("name"))
        if quest_name:
            quest_names_normalized.add(quest_name)
            if quest_name not in node_names_normalized:
                missing_quests.append(
                    {
                        "id": quest.get("id"),
                        "name": quest.get("name"),
                        "trader": quest.get("trader"),
                        "sortOrder": quest.get("sortOrder"),
                    }
                )

    missing_quests.sort(
        key=lambda quest: (
            str(quest.get("trader") or ""),
            _safe_float(quest.get("sortOrder")),
            str(quest.get("name") or ""),
        )
    )

    orphaned_nodes = sorted(node_names_normalized - quest_names_normalized)

    return {
        "graphNodeCount": len(node_names_normalized),
        "questCount": len(quest_entries),
        "questsMissingFromGraphCount": len(missing_quests),
        "questsMissingFromGraph": missing_quests,
        "graphNodesMissingFromQuestsCount": len(orphaned_nodes),
        "graphNodesMissingFromQuests": orphaned_nodes,
    }


"""

lines[start_idx:end_idx] = [new_code]
with open('src/autoscrapper/progress/update_report.py', 'w') as f:
    f.writelines(lines)
