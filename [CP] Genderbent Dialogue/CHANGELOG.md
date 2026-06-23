# Changelog

All notable changes to `Genderbent Dialogue` are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/);
this pack follows [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-06-23

### Added

- Custom name fields per character (English + Russian by grammatical case) via Generic Mod Config Menu.
- Display name via `Strings/NPCNames` so the renamed NPC appears with their custom name in the social tab and dialogue UI.
- English dialogue tokens woven into `dialogue/`, `Events/`, `mail/`, `references/` and Shared patches. Russian per-case substitution (Nominative, Genitive, Accusative, Dative, Instrumental as needed per character) applied throughout.
- Known limitations: diminutives (`Сэмми` / `Sammy`) are not renamed; prepositional sandhi (о/об, с/со before the name) is not auto-adjusted — if a future line needs it, the preposition must be folded into the case-field value.

## [1.0.0] - 2026-06-21

### Added

- Initial release. Lore-friendly, data-only NPC genderbend for EN + RU: sets the `Data/Characters` gender field to `Female` and rewrites gendered dialogue, marriage dialogue, events, mail, festival lines and other NPCs' references. No textures — pair with a portrait/sprite mod.
- Six characters, each toggled independently in Generic Mod Config Menu:
  - Sebastian (`SebastianFemale`)
  - Shane (`ShaneFemale`)
  - Harvey (`HarveyFemale`)
  - Alex (`AlexFemale`)
  - Elliott (`ElliottFemale`)
  - Sam (`SamFemale`)
- `patches/Shared/{events,dialogue}.json` resolve keys shared by two characters, gated on both `*Female` toggles, so enabling two overlapping characters flips each correctly.
