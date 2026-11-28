# Sum Shredders (beta repo)

Kids' 3D maths bike-park game, one `index.html` with Three.js r128 bundled in `lib/`, self-hosted fonts in `fonts/` and offline support via `sw.js`.
This repo deploys to **beta.sumshredders.com** (Vercel). Production lives in `joel-blackburn/math-bike-game`
and is only ever updated by the **Promote beta to production** GitHub Action. Never push to production directly.

## Rules
- Keep the line `const CHANNEL='beta';` exactly as is. The promote workflow flips it to `'prod'`.
- Save data: beta key `sumShredders_beta_v2`, prod key `sumShredders_v2` (migrates from `sumShredders_v1`).
- Test changes in a headless browser before pushing. Commit with clear messages.

## Secrets
- Chicken: type `sum` on the rider setup screen (or tap S-U-M in the "Suit up, max out!" heading).
- North Pole (Christmas park, `PARKS[XMAS]`, `xmas:true`): type `xmas` (or tap X-M-A-S in the heading). Saved per profile as `xmas`. It is not part of the park unlock chain and never counts as the "last" park.
- In the North Pole you always ride as Santa (`SANTA`) in a reindeer sleigh (`BUILD.sleigh`); the music switches to Jingle Bells (traditional, public domain) via `mus.xmas`.
- Don't add copyrighted characters (e.g. the Grinch, Max, Rudolph); keep characters original or public domain.

## Park order, racing, timer, daily challenge
- Unlock order is `CHAIN` (all parks except the North Pole): the original ten, then Dino Jungle, Food Land, Spooky Land (bonus parks, unlocked one by one on each maths level). `LASTP` (Spooky Land) is the Champion park; `nextPark(i)` drives the Next button.
- Racing Dash is a per-player option on the setup screen (step 7, `sel.race`, default on). When on, Dash races in every park except the North Pole. Dash (`RIVAL`, `spawnRival`/`updateRival`) rides at x=-1.25 on a timer per jump ({rookie:12.5,pro:10.5,legend:9}s x park `rt`, default 1) with rubber-banding. Beating him: +500 and `prog[level].race[park]=1` (🏁 on the map card).
- Spooky Land jump scare is always on: one cartoon monster (`jumpScare`, camera child) after a random jump 3-5. Keep it silly, not gory.
- Park timer: runs from GO to the finish (paused while paused), shown in the HUD; best time per park per level in `prog[level].time` (seconds), shown on map cards and the finish screen (NEW RECORD!).
- Daily challenge: seeded by date, picked from parks this player has unlocked on their level; goals: beat Dash (only if racing is on) / no mistakes / 5 in a row. Saved per profile in `daily` {last, streak, best, total}; streak rewards are items with `d:3` and `d:7`.
- `ANIM` holds per-frame scenery animations; it is reset in `buildWorld`.

## Dad's voice
- `studio.html` is a hidden recording page (beta.sumshredders.com/studio.html). Joel records clips and exports a zip.
- Process a zip with `python3 tools/process_voice.py <zip>`. This writes `voice/<id>.mp3` and `voice/index.json`, then commit.
- The game loads `voice/index.json`. With narrator "Dad", it stitches clips (numbers, maths words, phrases) and falls
  back to the computer voice for any line with a missing clip. Clip IDs are defined in `studio.html`.
- The promote workflow copies `voice/` to production along with `index.html` (not studio.html or tools/).

## Bundled files and offline
- `lib/three.min.js` (Three.js r128) and `fonts/` (Bungee, Nunito; OFL) are served from our own domain. Do not go back to CDNs or Google Fonts.
- `sw.js` caches the game for offline play: the page and `voice/index.json` are network-first, everything else stale-while-revalidate. Voice clips listed in `voice/index.json` are pre-cached. Bump `VERSION` in sw.js only when the caching rules change.
- The promote workflow copies `lib/`, `fonts/` and `sw.js` to production.

## Brand
- Studio brand: **Captain Dad** (Captain Dad Games). Its design system artifact is https://claude.ai/artifact/S5LNCW8krvLEGFgpvRU4aW (logos, icon, palette: navy #0b2a5b, sky #33c3ff, gold #ffc90a, red #ff4d4d, cream #fff3e0; type: Baloo 2 ExtraBold for headings, Nunito for body, both Google Fonts). Use these for Captain Dad branding text; the game keeps Bungee for its own UI.
- Web-optimised copies live in `brand/` (favicon, apple-touch icon, manifest icons, title-screen logo, wide lockups). The promote workflow copies `brand/` to production.
