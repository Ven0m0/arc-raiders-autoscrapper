import time
import random
import string
from src.autoscrapper.utils.normalization import normalize_quest_name

def generate_random_quest_name():
    return "".join(random.choices(string.ascii_letters + " '", k=15))

def benchmark_current(node_values, quests):
    start = time.perf_counter()

    # 1. node_names_normalized
    node_names_normalized = {
        normalize_quest_name(node_name) for node_name in node_values if normalize_quest_name(node_name)
    }

    # 2. quest_names_normalized
    quest_entries = [quest for quest in quests if isinstance(quest, dict)]
    quest_names_normalized = {
        normalize_quest_name(quest.get("name")) for quest in quest_entries if normalize_quest_name(quest.get("name"))
    }

    # 3. missing_quests
    missing_quests = []
    for quest in quest_entries:
        quest_name = normalize_quest_name(quest.get("name"))
        if not quest_name or quest_name in node_names_normalized:
            continue
        missing_quests.append(quest)

    return time.perf_counter() - start

def benchmark_optimized(node_values, quests):
    start = time.perf_counter()

    # Let's write the optimized version here
    # Local cache for normalization to avoid repeated regex ops
    norm_cache = {}
    def get_normalized(name):
        if name not in norm_cache:
            norm_cache[name] = normalize_quest_name(name)
        return norm_cache[name]

    node_names_normalized = {
        name for node_name in node_values if (name := get_normalized(node_name))
    }

    quest_entries = [quest for quest in quests if isinstance(quest, dict)]
    quest_names_normalized = set()

    missing_quests = []
    for quest in quest_entries:
        quest_name = get_normalized(quest.get("name"))
        if quest_name:
            quest_names_normalized.add(quest_name)
            if quest_name not in node_names_normalized:
                missing_quests.append(quest)

    return time.perf_counter() - start

node_values = [generate_random_quest_name() for _ in range(5000)]
quests = [{"name": generate_random_quest_name(), "id": i} for i in range(5000)]

# Introduce duplicates to mimic reality
node_values += node_values[:1000]
for q in quests[:1000]:
    quests.append(q.copy())

# Warmup
benchmark_current(node_values, quests)
benchmark_optimized(node_values, quests)

n_runs = 10
current_times = [benchmark_current(node_values, quests) for _ in range(n_runs)]
optimized_times = [benchmark_optimized(node_values, quests) for _ in range(n_runs)]

print(f"Current Avg: {sum(current_times)/n_runs:.4f}s")
print(f"Optimized Avg: {sum(optimized_times)/n_runs:.4f}s")
print(f"Speedup: {sum(current_times)/sum(optimized_times):.2f}x")
