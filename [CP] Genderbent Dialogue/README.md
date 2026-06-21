# Genderbent Dialogue

*Lore-friendly NPC genderbend — dialogue, events and pronouns, no textures.*

Source: https://github.com/knst0/svm

Turns selected NPCs into women at the **game-data** level (no textures): flips the gender
field in `Data/Characters` and rewrites gendered text to feminine for **EN + RU**. Pair it
with a portrait/sprite mod.

Currently in the pack: **Sebastian**, **Shane**, **Harvey**, **Alex**, **Elliott**, **Sam**.
Each is a separate toggle in **Generic Mod Config Menu** (`SebastianFemale`, `ShaneFemale`,
`HarveyFemale`, `AlexFemale`, `ElliottFemale`, `SamFemale`).

## Requirements
SMAPI, Content Patcher (required), Generic Mod Config Menu (optional).

## Install
Copy the folder into `Stardew Valley/Mods`, launch through SMAPI, and enable the characters
you want in GMCM. Applies immediately.

## Development tools (inside the mod folder, not shipped in releases)
- `dialogue_diff.py` — shows which patched lines changed after a game update.
- `xnb_unpacker.py` — unpacks the game's `.xnb` assets to JSON.

```
python dialogue_diff.py check
python dialogue_diff.py snapshot --version 1.6.15
python xnb_unpacker.py "<...>/Characters/Dialogue/Sebastian.ru-RU.xnb" -o out.json
```
