# Changelog

All notable changes to `Genderbent Dialogue` are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/);
this pack follows [Semantic Versioning](https://semver.org/).

## [1.2.0] - 2026-06-27

### Fixed

- Display name now set via `Data/Characters` `DisplayName` field (the SDV 1.6 mechanism); the previous `Strings/NPCNames` approach did not apply, so custom names never showed.
- Vincent now calls a female Sam "big sister" / "старшая сестрёнка" (`Mon` line was unpatched in both locales).
- Sebastian: partial-flip residuals corrected (`сказал`→`сказала`, `упоминал`→`упоминала`, `поменял`→`поменяла`, `какой … стал бледный`→`какая … стала бледная`); restored dropped word `таких` in `dating_Sebastian`.
- Shane: EN cliff/hospital event "brought him in"→"brought her in"; Saloon event 97 (`спросил`→`спросила`).
- Harvey: Hospital event 7 residual `он`→`она`.

### Added

- Festival coverage for Alex and Sam (`patches/{Alex,Sam}/festivals.json`) — previously only Shane had festival patches, leaving female Alex/Sam with masculine festival self-references.
- Generic spouse asset `Characters/Dialogue/MarriageDialogue` now patched for Sebastian, Shane and Sam (`{key}_{Npc}` lines were unpatched).
- Missing reference/event/mail lines: Robin `divorced_Sebastian`/`Fri_inlaw_Sebastian`; Harvey `Data/Events/Farm`+`Forest`, pass-out mail; Alex grandparents (Evelyn/George), Pam, Haley references, `joshMessage` mail; Sam Kent/Jodi references.
- New both-female Shared blocks for `Data/Events/Farm` and `Data/Events/Forest` (Shane + Harvey) so each flips correctly when both toggles are on.

## [1.1.0] - 2026-06-23

### Added

- Custom name fields per character (English + Russian by grammatical case) via Generic Mod Config Menu.
- Display name override so the renamed NPC appears with their custom name in the social tab and dialogue UI (see 1.2.0 — corrected to use `Data/Characters` `DisplayName`).
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
