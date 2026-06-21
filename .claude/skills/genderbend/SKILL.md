---
name: genderbend
description: Add or edit characters in the Stardew Valley "Genderbend Info" Content Patcher pack — regender an NPC to female (dialogue, events, other NPCs' references, marriage) for English and Russian. Use when adding a new genderbent character, changing or fixing a regendered phrase, or re-checking patches after a Stardew Valley update. Covers the pack's per-character patch folders, its dialogue_diff tool, and SDV dialogue and event regendering grammar.
---

# SDV Genderbend (Content Patcher) authoring

Role: you maintain a data-only Content Patcher pack that flips chosen NPCs to female.
No textures. Each NPC is one GMCM toggle `{Char}Female`. You either (a) add a new
character, (b) change a regendered phrase, or (c) audit patches after a game update.

Work inside the pack folder (e.g. `[CP] Genderbent Dialogue/`). NEVER write into the
ModOrganizer mods folder; the user copies the pack there.

## Pack layout (output contract)
```
content.json                      Format "2.1.0" + ConfigSchema + Include actions only
patches/{Char}/gender.json        Data/Characters Gender=Female  (Fields, not Entries)
patches/{Char}/dialogue.json      the NPC's own lines + marriage (EN + RU blocks)
patches/{Char}/references.json    how OTHER NPCs talk about the NPC (EN + RU)
patches/{Char}/events.json        the NPC's lines, player choices and over-head text in events
patches/Shared/{events,dialogue}.json  combined blocks for keys two chars share, gated on
                                  BOTH toggles; Included LAST (see new-character step 6)
i18n/default.json , i18n/ru.json  GMCM labels  config.{Char}Female.name/.description
baseline/originals.json           snapshot of game originals (for update diffs)
```
Each `patches/{Char}/*.json` is `{ "Changes": [ ...EditData blocks... ] }`.
`content.json` `Changes` is ONLY `{"Action":"Include","FromFile":"patches/{Char}/{group}.json"}`.

## Content Patcher anchors (reproduce exactly)
- Gender block:
  `{"Action":"EditData","Target":"Data/Characters","Fields":{"{Npc}":{"Gender":"Female"}},"When":{"{Char}Female":true}}`
- Dialogue/event block — ONE per asset per locale:
  `{"Action":"EditData","Target":"{asset}","TargetLocale":"{loc}","When":{"{Char}Female":true},"Entries":{ "{key}":"{full regendered value}" }}`
- `TargetLocale`: `""` = English/base asset, `"ru-RU"` = Russian. MUST be the full code
  `ru-RU` (not `ru`), and `TargetLocale` REQUIRES `"Format": "2.1.0"` — with Format 2.0 CP
  silently ignores the whole pack (WARN: using TargetLocale requires Format 2.1.0).
- ConfigSchema entry: `"{Char}Female": {"AllowValues":"true, false","Default":"false"}`.
- i18n keys (both default.json and ru.json): `config.{Char}Female.name`, `config.{Char}Female.description`.
- `EditData`+`Entries` REPLACES the entire entry value, so each value MUST be the full
  original line with only the gendered fragments changed. Keep every command/token/`#$b#` intact.
- Asset names: `Characters/Dialogue/{Npc}`, `Characters/Dialogue/MarriageDialogue{Npc}`,
  `Data/Events/{Location}`, `Data/mail`, `Strings/Characters`, `Strings/StringsFromCSFiles`.
  Event keys are the FULL key incl. preconditions, e.g. `384882/f Sebastian 2500/t 2000 2400`.

## Regendering rules (the hard part)
Change ONLY words that refer to THIS character. Leave everything else.

Russian (most work — grammatical gender):
- masculine past verbs `-л` -> `-ла`: был->была, пошёл->пошла, видел->видела, думал->думала,
  собирался->собиралась, чувствовал->чувствовала, занялся->занялась.
- short adjectives: рад->рада, готов->готова, должен->должна, занят->занята, уверен->уверена,
  счастлив->счастлива, один->одна, сам->сама.
- relationship/role nouns: отец->мать, брат->сестра, сын->дочь, муж->жена, супруг->супруга,
  племянник->племянница, крёстный->крёстная, целитель->целительница; парень->девушка only
  when it denotes THIS character.
English (sparse): guy->girl, man->woman, father->mother, husband->wife, brother->sister,
  son->daughter, nephew->niece, godfather->godmother, he/him/his->she/her.

DO NOT touch (safety — silent errors if you do):
- `${male^female}$` and bare `^` splits — these depend on the PLAYER's gender, engine-handled.
- masculine words for OTHER people/animals in the same line (Sam, Demetrius, the frog
  "лягушонок", "город манил", "поезд проходил", "котёл", "стол") — only the target NPC flips.
- the NPC's name itself (keep "Себастиан"/"Sebastian"); only pronouns/agreement around it.

Pitfall: a masculine form is often NOT adjacent to "я" — "Я как раз собирался",
"Я никогда не чувствовал". Scan the whole quoted line, not just `я {verb}`.

Player choices count too: regender pronouns about the NPC inside `question`/`quickQuestion`
options and `textAboveHead {Npc} "..."` lines (e.g. fork "Он занят..."->"Она занята...",
over-head "Поймал!"->"Поймала!"). Frog/Sam refs in those choices stay male.

## Verification (never skip)
- Every replacement substring must occur EXACTLY ONCE in its entry value. If it occurs 0x,
  the original text differs (typo or a game update changed it); if more than once, add context
  to the substring. This one-match rule is also your game-update break detector.
- All JSON must parse (Windows: `py`, not `python`):
  `py -c "import json,glob; [json.load(open(f,encoding='utf-8')) for f in glob.glob('patches/**/*.json',recursive=True)+['content.json']]"`
- Residual scan: after editing, re-unpack the NPC's assets and grep their `speak`/value text
  for leftover masculine forms (был, рад, готов, должен, занят, verbs ending -лся or -ал/-ил/-ел/-ыл/-ёл/-ул),
  manually rejecting noun / other-person false positives.

## Tools (run on the machine with the game; needs Python 3)
On Windows the launcher is `py`, not `python`; prefix `PYTHONIOENCODING=utf-8` (or write to a
file) when output contains Cyrillic, or the console cp1252 codec raises UnicodeEncodeError.
- Unpack an original to read keys/text (Dictionary string,string assets):
  `py xnb_unpacker.py "{Content}/Characters/Dialogue/{Npc}.ru-RU.xnb" -o out.json`
  (omit `.ru-RU` for English base). `{Content}` = `...\Stardew Valley\Content`.
- Find every event a character speaks in: unpack `Data/Events/*.xnb` and grep `speak {Npc}`
  / `textAboveHead {Npc}`; the event ID is the key text before the first `/`.
- After a verified build, record the baseline:
  `py dialogue_diff.py --mod "[CP] Genderbent Dialogue" --content "{Content}" snapshot --version {gameVer}`
- After a Stardew Valley update, find what changed under you:
  `py dialogue_diff.py --mod "[CP] Genderbent Dialogue" --content "{Content}" check`
  -> lists CHANGED (with diff + your current patch output) and MISSING keys, exit 1 if any.
  Re-regender those entries against the new original, then snapshot again.

## Add a NEW character (procedure)
1. Unpack EN base + `.ru-RU` for `Characters/Dialogue/{Npc}`, `MarriageDialogue{Npc}`, and
   each `Data/Events/{Loc}` where they appear; also scan other NPCs' dialogue + mail + Strings
   for the name to collect references.
2. Create `patches/{Char}/gender.json`, `dialogue.json`, `references.json`, `events.json` with
   EditData blocks per the anchors above (EN `""` and RU `ru-RU` blocks), full regendered
   values, `When` = `{Char}Female`.
3. `content.json`: add the 4 `Include` actions. ConfigSchema: add `{Char}Female`.
   i18n/default.json + i18n/ru.json: add the two labels.
4. Metadata (easy to forget — the Alex commit skipped all three): bump `manifest.json`
   `Version` one minor (each char = a minor bump) and add the char to its `Description`;
   add a dated `CHANGELOG.md` entry (dialogue/marriage/mail/refs/events touched + any
   shared-key collision note).
5. Verify (JSON parses, one-match rule, residual scan). Run `snapshot` (a shared key
   already owned by another char does NOT grow the baseline — that's the collision).
6. Shared-key collisions (both-female correctness): scan every `(Target,TargetLocale,key)`
   across `patches/*/*.json` (skip `Shared`) for keys owned by >1 char. For each, add a
   COMBINED block to `patches/Shared/{events|dialogue}.json` gated on BOTH toggles
   (`"When": {"{A}Female": true, "{B}Female": true}`); build its value by a 3-way char-level
   merge (base = `baseline/originals.json` entry + each owner's flips; assert the owners'
   change-regions don't overlap). Keep the two `patches/Shared/*` Includes LAST in
   `content.json` so they win the both-on case; single toggles are unaffected. Without this,
   the later Include wins and the other character reverts to male.
7. Test in-game: enable the toggle in GMCM, then SMAPI console `debug ebi {eventID}`
   (close menus; stand on a DIFFERENT map than where the event plays).

## Change a phrase (procedure)
1. Find the entry by key in the right `patches/{Char}/*.json`. The value is the FULL line.
2. Edit only the gendered fragment; keep `${}$` / `^` tokens and all commands intact.
3. Validate JSON. The game original is unchanged, so the baseline stays valid (no re-snapshot
   needed unless you added/removed a patched key).

## Notes
- Other languages: only the `Gender` field flips for them; their text stays male (we only do EN+RU).
- The whole system is data + JSON; CP reloads on GMCM toggle, so no game restart needed for config
  changes — but a pack that was rejected (e.g. Format/TargetLocale mismatch) needs a full restart.
