const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs=require('node:fs');const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:5173/');await page.locator('.map-state').waitFor({state:'hidden'});
 await page.route('**/scenarios/evaluate',async route=>{if(route.request().postDataJSON().scenario_id==='heavy') await new Promise(r=>setTimeout(r,1200));await route.continue().catch(()=>{});});
 await page.route('**/priorities/calculate',async route=>{if(route.request().postDataJSON().scenario_id==='heavy') await new Promise(r=>setTimeout(r,1200));await route.continue().catch(()=>{});});
 await page.getByLabel('Available response teams').fill('5');await page.waitForFunction(()=>document.querySelectorAll('.priorities li').length===5);
 await page.getByLabel('Rainfall scenario').selectOption('heavy');await page.getByLabel('Available response teams').fill('2');await page.waitForTimeout(250);
 await page.getByLabel('Rainfall scenario').selectOption('extreme');await page.getByLabel('Available response teams').fill('3');
 await page.locator('.map-state').waitFor({state:'hidden'});await page.waitForFunction(()=>document.querySelectorAll('.priorities li').length===3);await page.waitForTimeout(1600);
 const expected=await(await page.request.post('http://localhost:8000/priorities/calculate',{data:{scenario_id:'extreme',available_teams:3}})).json();
 assert.deepEqual(await page.locator('.priorities button').evaluateAll(elements=>elements.map(e=>e.dataset.villageId)),expected.map(v=>v.id));
 assert.equal(await page.locator('.leaflet-overlay-pane path[stroke="#245ec1"]').count(),3);
 await page.locator('.priorities button').first().click();await page.getByLabel('Village detail',{exact:true}).waitFor();assert((await page.locator('.detail .risk-line').innerText()).includes(expected[0].risk_score.toFixed(3)));
 assert.deepEqual(errors,[]);const result={rapid_scenario_and_team_changes:'passed',final_scenario:'extreme',final_teams:3,map_and_priority_and_detail_agree:true,errors};fs.writeFileSync('docs/evidence/m6-integration.json',JSON.stringify(result,null,2));console.log(result);await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
