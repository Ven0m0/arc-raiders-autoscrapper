# MetaForge Arc Raiders API — Field Schemas

## Item

Returned by `GET /items`.

| Field | Type | Notes |
|---|---|---|
| `id` | string | Slug, e.g. `acoustic-guitar` |
| `name` | string | Display name |
| `description` | string | |
| `item_type` | string | `Weapon`, `Quick Use`, `Topside Material`, `Basic Material`, `Armor`, etc. |
| `rarity` | string | `Common`, `Uncommon`, `Rare`, `Epic`, `Legendary` |
| `value` | int | Base loot value in credits |
| `workbench` | string\|null | Crafting bench name, e.g. `Weapon Bench 2` |
| `loadout_slots` | string[] | e.g. `["weapon"]`, `["armor"]`, `[]` for non-equippable |
| `icon` | string | CDN URL to `.webp` icon |
| `flavor_text` | string | |
| `subcategory` | string | |
| `shield_type` | string | |
| `loot_area` | string | |
| `ammo_type` | string | e.g. `heavy`, `light`, `shotgun` |
| `sources` | null\|any | Loot sources (sparse) |
| `locations` | array | Map locations |
| `guide_links` | `{url, label}[]` | Links to MetaForge guides |
| `game_asset_id` | int | Internal ID; `-9999` = no asset ID |
| `created_at` | ISO8601 | |
| `updated_at` | ISO8601 | |
| `stat_block` | object | See below |

### stat_block fields

All numeric; `0` means not applicable for this item type.

**Universal:** `value`, `weight`, `stackSize`

**Combat:** `damage`, `health`, `radius`, `shield`, `arcStun`, `raiderStun`, `damageMult`, `damagePerSecond`, `damageMitigation`

**Weapon-specific:** `range`, `fireRate`, `stability`, `magazineSize`, `firingMode` (string), `reducedReloadTime`, `reducedVerticalRecoil`, `increasedVerticalRecoil`, `increasedBulletVelocity`, `reducedMaxShotDispersion`, `reducedPerShotDispersion`, `reducedDispersionRecoveryTime`, `reducedRecoilRecoveryTime`, `increasedRecoilRecoveryTime`, `reducedDurabilityBurnRate`, `reducedNoise`, `ammo` (string, weapon only), `increasedFireRate`, `increasedADSSpeed`

**Mobility/equip:** `agility`, `movementPenalty`, `reducedEquipTime`, `increasedEquipTime`, `reducedUnequipTime`, `increasedUnequipTime`

**Survival:** `healing`, `healingPerSecond`, `healingSlots`, `stamina`, `staminaPerSecond`, `stealth`, `useTime`, `duration`

**Loadout/storage:** `augmentSlots`, `backpackSlots`, `quickUseSlots`, `safePocketSlots`, `weightLimit`, `shieldCharge`, `shieldCompatibility` (string), `illuminationRadius`

---

## Arc

Returned by `GET /arcs`.

| Field | Type | Notes |
|---|---|---|
| `id` | string | Slug, e.g. `bastion` |
| `name` | string | |
| `description` | string | |
| `icon` | string | CDN URL |
| `image` | string | CDN URL (larger image) |
| `created_at` | ISO8601 | |
| `updated_at` | ISO8601 | |
| `loot` | array | Only present when `includeLoot=true`; may be empty `[]` |

---

## Quest

Returned by `GET /quests`.

| Field | Type | Notes |
|---|---|---|
| `id` | string | Slug, e.g. `a-bad-feeling` |
| `name` | string | |
| `objectives` | string[] | Step-by-step objective text |
| `xp` | int | XP reward (0 if none) |
| `granted_items` | array | Items granted on unlock |
| `trader_name` | string | Quest giver, e.g. `Celeste`, `Apollo` |
| `sort_order` | int | Quest chain order within trader |
| `position` | `{x, y}` | Map quest board position |
| `marker_category` | string\|null | |
| `image` | string | CDN URL |
| `locations` | array | |
| `guide_links` | `{url, label}[]` | |
| `required_items` | RequiredItem[] | Items to turn in (see below) |
| `rewards` | Reward[] | Items awarded on completion (see below) |
| `created_at` | ISO8601 | |
| `updated_at` | ISO8601 | |

### RequiredItem

```json
{
  "item": { "id": "...", "icon": "...", "name": "...", "rarity": "...", "item_type": "..." },
  "item_id": "string",
  "quantity": "string"
}
```

### Reward

```json
{
  "id": "uuid",
  "item": { "id": "...", "icon": "...", "name": "...", "rarity": "...", "item_type": "..." },
  "item_id": "string",
  "quantity": "string"
}
```

---

## Trader Item

Returned by `GET /traders` — each trader key maps to an array of these.

| Field | Type | Notes |
|---|---|---|
| `id` | string | Item slug |
| `name` | string | |
| `icon` | string | CDN URL |
| `rarity` | string | |
| `item_type` | string | |
| `description` | string | |
| `value` | int | Base loot value |
| `trader_price` | int | Buy price from trader (typically 3× `value`) |

**Known traders:** `Apollo`, `Celeste` (others may exist — iterate `data` keys at runtime).

---

## Event

Returned by `GET /events-schedule`.

| Field | Type | Notes |
|---|---|---|
| `name` | string | Event name, e.g. `Matriarch`, `Night Raid`, `Bird City` |
| `map` | string | Map name, e.g. `Spaceport`, `Dam`, `Buried City`, `Blue Gate`, `Stella Montis` |
| `icon` | string | CDN URL |
| `startTime` | int | Unix timestamp **milliseconds** |
| `endTime` | int | Unix timestamp **milliseconds** |

Convert to JS Date: `new Date(startTime)`. Convert to Python: `datetime.fromtimestamp(startTime / 1000)`.
