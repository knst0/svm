# Changelog

All notable changes to **Genderbent Dialogue** are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/);
this pack follows [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-06-21
### Added
- Initial release. Lore-friendly, data-only NPC genderbend for **EN + RU**: sets the
  `Data/Characters` gender field to `Female` and rewrites gendered dialogue, marriage
  dialogue, events, mail, festival lines and other NPCs' references. No textures — pair
  with a portrait/sprite mod.
- Six characters, each toggled independently in Generic Mod Config Menu:
  **Sebastian** (`SebastianFemale`), **Shane** (`ShaneFemale`),
  **Harvey** (`HarveyFemale`), **Alex** (`AlexFemale`),
  **Elliott** (`ElliottFemale`) and **Sam** (`SamFemale`).
- `patches/Shared/{events,dialogue}.json` resolve keys shared by two characters, gated on
  both `*Female` toggles, so enabling two overlapping characters flips each correctly.
