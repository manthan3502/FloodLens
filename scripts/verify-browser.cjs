// Uses the bundled browser runtime, or a normal local Playwright installation.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle' });
  await page.locator('.leaflet-container').waitFor();
  await page.getByRole('heading', { name: 'FloodLens' }).waitFor();
  const loadedTiles = await page.locator('.leaflet-tile-loaded').count();
  fs.mkdirSync('docs/evidence', { recursive: true });
  await page.screenshot({ path: 'docs/evidence/m0-map.png', fullPage: true });
  const report = { heading: await page.title(), loadedTiles, errors };
  fs.writeFileSync('docs/evidence/browser-m0.json', JSON.stringify(report, null, 2));
  console.log(report);
  await browser.close();
  if (errors.length || !loadedTiles) process.exitCode = 1;
})().catch(error => { console.error(error); process.exitCode = 1; });
