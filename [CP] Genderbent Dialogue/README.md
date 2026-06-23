# Genderbent Dialogue

Lore-friendly NPC genderbend for English and Russian. No textures.

Turns selected NPCs into women at the game-data level: it flips the gender field in `Data/Characters` and rewrites gendered text — dialogue, marriage dialogue, events, festivals, mail and other NPCs' references — to feminine. It changes words, not art, so pair it with a portrait/sprite mod.

## Requirements

- [Content Patcher](https://github.com/Pathoschild/StardewMods/tree/develop/ContentPatcher) 2.1.0 or newer (required)
- [Generic Mod Config Menu](https://github.com/spacechase0/StardewValleyMods/tree/develop/framework/GenericModConfigMenu) (optional, for the toggles)

## Custom names

Each character has an optional custom name field in Generic Mod Config Menu. When set, the displayed name changes in dialogue, events, mail, and other NPCs' references.

- **English**: one field per character. Fill it with the desired name.
- **Russian**: one field per grammatical case (Nominative, Genitive, Accusative, Dative, Instrumental — which cases appear depends on the character). Fill the cases you need; any case left blank or at its default keeps the original name for that grammatical role.
- Leave all fields blank or at default to keep the character's original name everywhere.

### Limitations

- Diminutives (`Сэмми` / `Sammy`) are not renamed.
- Prepositions before the name (о/об, с/со) are not automatically adjusted for the custom name. If a future dialogue line needs sandhi correction, fold the preposition into the case-field value (e.g. enter `об Алексе` instead of relying on `о {{AlexNamePrep}}`).

## Development tools

Kept in the mod folder, not shipped in releases.

- `dialogue_diff.py` — shows which patched lines changed after a game update.
- `xnb_unpacker.py` — unpacks the game's `.xnb` assets to JSON.

```shell
python dialogue_diff.py check
python dialogue_diff.py snapshot --version 1.6.15
python xnb_unpacker.py "<...>/Characters/Dialogue/Sebastian.ru-RU.xnb" -o out.json
```
