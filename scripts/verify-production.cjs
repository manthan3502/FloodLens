// Verify the live deployment in a fresh browser; never mock production responses.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const appUrl = process.env.APP_URL, apiUrl = process.env.API_BASE_URL;
if (!appUrl?.startsWith('https://') || !apiUrl?.startsWith('https://')) throw new Error('Set actual HTTPS APP_URL and API_BASE_URL');
(async () => {
 const browser = await chromium.launch({channel:'msedge',headless:true});
 try {
  const context = await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:'.cache/production-video',size:{width:1440,height:1000}}});
  const page = await context.newPage(); page.setDefaultTimeout(90000);
  const errors=[],apiFailures=[],origins=new Set();
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.url().startsWith(apiUrl)){if(r.status()>=400)apiFailures.push({url:r.url(),status:r.status()});origins.add(r.headers()['access-control-allow-origin']);}});
  const started=Date.now();
  const nextScenario = scenario => page.waitForResponse(r=>r.url()===apiUrl+'/scenarios/evaluate' && r.request().postDataJSON().scenario_id===scenario);
  const initial=nextScenario('normal');
  await page.goto(appUrl); const normal=await(await initial).json();
  await page.locator('.map-state').waitFor({state:'hidden'});
  const polygons=page.locator('.leaflet-overlay-pane path[fill-opacity="0.65"]');
  assert.equal(await polygons.count(),380);
  const firstLoadMs=Date.now()-started,scenarios={normal},legends={normal:await page.locator('.legend').innerText()};
  await page.waitForFunction(()=>[...document.querySelectorAll('.leaflet-tile')].some(t=>t.complete&&t.naturalWidth>0));
  await page.waitForTimeout(1500); // Let initial Leaflet zoom and tile fades finish for the asset.
  await page.screenshot({path:'docs/evidence/production-normal.png',fullPage:true});
  for(const scenario of ['heavy','extreme']){
   const pending=nextScenario(scenario); await page.getByLabel('Rainfall scenario').selectOption(scenario);
   scenarios[scenario]=await(await pending).json(); await page.locator('.map-state').waitFor({state:'hidden'});
   legends[scenario]=await page.locator('.legend').innerText(); assert.equal(await polygons.count(),380);
  }
  const scores=data=>new Map(data.features.map(f=>[f.properties.id,f.properties.risk_score]));
  const n=scores(normal),h=scores(scenarios.heavy),e=scores(scenarios.extreme);
  for(const [id,score] of n){assert(h.get(id)>score);assert(e.get(id)>h.get(id));}
  assert.notEqual(legends.normal,legends.extreme);
  for(const count of [5,3]){
   await page.getByLabel('Available response teams').fill(String(count));
   await page.waitForFunction(n=>document.querySelectorAll('.priorities li').length===n,count);
   assert.equal(await page.locator('.leaflet-overlay-pane path[stroke="#245ec1"]').count(),count);
  }
  const request={data:{scenario_id:'extreme',available_teams:3}};
  const response=await page.request.post(apiUrl+'/priorities/calculate',request); assert.equal(response.status(),200);
  const expected=await response.json();
  assert.deepEqual(await page.locator('.priorities button').evaluateAll(nodes=>nodes.map(n=>n.dataset.villageId)),expected.map(v=>v.id));
  assert.deepEqual(await(await page.request.post(apiUrl+'/priorities/calculate',request)).json(),expected);
  await page.locator('.priorities button').first().click(); await page.getByLabel('Village detail',{exact:true}).waitFor();
  assert.equal(await page.locator('.detail h2').innerText(),expected[0].name);
  assert((await page.locator('.detail .risk-line').innerText()).includes(expected[0].risk_score.toFixed(3)));
  assert((await page.locator('.detail .facts').innerText()).includes(Math.round(expected[0].population_estimate).toLocaleString('en-IN')));
  assert.equal(await page.locator('.detail .factor').count(),5);
  await page.getByLabel('Highlight SAR change zones').check();
  assert((await page.locator('.map-note').first().innerText()).includes('not flood-extent boundaries'));
  await page.screenshot({path:'docs/evidence/production-dashboard.png',fullPage:true});
  await page.getByRole('button',{name:/Understand the methodology/}).click();
  await page.getByRole('dialog',{name:'Methodology'}).waitFor();
  await page.screenshot({path:'docs/evidence/production-methodology.png',fullPage:true});
  await page.getByRole('dialog').getByRole('button',{name:'Close ×',exact:true}).click();
  const origin=new URL(appUrl).origin;
  for(const path of ['/scenarios/evaluate','/priorities/calculate']){
   const preflight=await page.request.fetch(apiUrl+path,{method:'OPTIONS',headers:{Origin:origin,'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'}});
   assert.equal(preflight.status(),200);assert.equal(preflight.headers()['access-control-allow-origin'],origin);
  }
  const rejected=await page.request.fetch(apiUrl+'/scenarios/evaluate',{method:'OPTIONS',headers:{Origin:'https://untrusted.example','Access-Control-Request-Method':'POST'}});
  assert.equal(rejected.status(),400);assert(!rejected.headers()['access-control-allow-origin']);
  assert.deepEqual([...origins],[origin]);assert.deepEqual(errors,[]);assert.deepEqual(apiFailures,[]);
  const video=page.video();await context.close();fs.copyFileSync(await video.path(),'docs/evidence/floodlens-production-demo.webm');
  const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  const mp=await mobile.newPage();mp.setDefaultTimeout(90000);await mp.goto(appUrl);await mp.locator('.map-state').waitFor({state:'hidden'});
  assert.equal(await mp.locator('.leaflet-overlay-pane path[fill-opacity="0.65"]').count(),380);
  assert(await mp.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
  await mp.waitForFunction(()=>[...document.querySelectorAll('.leaflet-tile')].some(t=>t.complete&&t.naturalWidth>0));
  await mp.waitForTimeout(1500);
  await mp.screenshot({path:'docs/evidence/production-mobile.png',fullPage:true});await mobile.close();
  const result={checked_at:new Date().toISOString(),appUrl,apiUrl,cold_browser:true,first_load_ms:firstLoadMs,elapsed_ms:Date.now()-started,villages:380,scenarios:['normal','heavy','extreme'],all_village_scores_increase:true,legends,latest_priority_ids:expected.map(v=>v.id),priority_determinism:true,map_ranking_detail_agree:true,population_and_factors_verified:true,cors:{allowed_origin:origin,untrusted_origin_rejected:true},mobile_no_horizontal_overflow:true,errors,apiFailures};
  fs.writeFileSync('docs/evidence/production-smoke.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
