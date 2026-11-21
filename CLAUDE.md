# Sum Shredders (beta repo)

Kids' 3D maths bike-park game, one self-contained `index.html` (Three.js r128 from cdnjs).
This repo deploys to **beta.sumshredders.com** (Vercel). Production lives in `joel-blackburn/math-bike-game`
and is only ever updated by the **Promote beta to production** GitHub Action. Never push to production directly.

## Rules
- Keep the line `const CHANNEL='beta';` exactly as is. The promote workflow flips it to `'prod'`.
- Save data: beta key `sumShredders_beta_v2`, prod key `sumShredders_v2` (migrates from `sumShredders_v1`).
- Test changes in a headless browser before pushing. Commit with clear messages.

## Dad's voice
- `studio.html` is a hidden recording page (beta.sumshredders.com/studio.html). Joel records clips and exports a zip.
- Process a zip with `python3 tools/process_voice.py <zip>`. This writes `voice/<id>.mp3` and `voice/index.json`, then commit.
- The game loads `voice/index.json`. With narrator "Dad", it stitches clips (numbers, maths words, phrases) and falls
  back to the computer voice for any line with a missing clip. Clip IDs are defined in `studio.html`.
- The promote workflow copies `voice/` to production along with `index.html` (not studio.html or tools/).

## Brand
- Studio brand: **Captain Dad** (Captain Dad Games). Its design system artifact is https://claude.ai/artifact/S5LNCW8krvLEGFgpvRU4aW (logos, icon, colours: navy #071b37, cream #fff3d7, gold #ffc928, red #e92f36).
- Web-optimised copies live in `brand/` (favicon, apple-touch icon, manifest icons, title-screen logo, wide lockups). The promote workflow copies `brand/` to production.
