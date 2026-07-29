#!/usr/bin/env node
// verify-pager.js — PPT 式横向翻页单文件 HTML 的无头验收探针
// 用法: npm i playwright-core && node verify-pager.js <file:// 或 http(s) URL>
// 覆盖: 页数一致 / 键盘导航 / 目录跳页 / 拖拽翻页 / reduced-motion 瞬时到位 / 移动端 resize / 控制台零报错
// DOM 约定: section.page 列表、#track 容器、#cur/#total 页码、#catbtn+#catlist .catit[data-go] 目录
const { chromium } = require('playwright-core');

(async () => {
  const url = process.argv[2];
  if (!url) { console.error('usage: node verify-pager.js <url>'); process.exit(2); }
  const errors = [];
  let browser;
  try { browser = await chromium.launch({ headless: true, channel: 'chrome' }); }
  catch (e) { browser = await chromium.launch({ headless: true }); }
  const b = await browser;
  const page = await b.newPage({ viewport: { width: 1440, height: 900 } });
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
  await page.goto(url);
  await page.waitForTimeout(600);

  const r = {};
  r.pageCount = await page.locator('section.page').count();
  r.totalShown = await page.locator('#total').textContent().catch(() => 'n/a');

  await page.keyboard.press('ArrowRight'); await page.waitForTimeout(700);
  r.afterArrow = await page.locator('#cur').textContent();
  await page.keyboard.press('End'); await page.waitForTimeout(700);
  r.afterEnd = await page.locator('#cur').textContent();
  await page.keyboard.press('Home'); await page.waitForTimeout(700);
  r.afterHome = await page.locator('#cur').textContent();

  await page.click('#catbtn'); await page.waitForTimeout(400);
  r.catItems = await page.locator('#catlist .catit').count();
  const go3 = page.locator('#catlist .catit[data-go="2"]');
  if (await go3.count()) { await go3.click(); await page.waitForTimeout(800); }
  r.afterCatJump = await page.locator('#cur').textContent();

  await page.keyboard.press('Home'); await page.waitForTimeout(600);
  await page.mouse.move(1000, 450); await page.mouse.down();
  for (let i = 1; i <= 10; i++) { await page.mouse.move(1000 - i * 55, 450); await page.waitForTimeout(12); }
  await page.mouse.up(); await page.waitForTimeout(800);
  r.afterDrag = await page.locator('#cur').textContent();

  // reduced motion: 必须瞬时到位（transform 精确等于 -W*idx，无弹簧行程）
  const page2 = await b.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  page2.on('pageerror', e => errors.push('PAGEERROR(rm): ' + e.message));
  await page2.goto(url); await page2.waitForTimeout(400);
  await page2.keyboard.press('ArrowRight'); await page2.waitForTimeout(200);
  r.reducedTransform = await page2.locator('#track').evaluate(el => el.style.transform);
  r.reducedRvOpacity = await page2.evaluate(() => getComputedStyle(document.querySelector('section.page.active .rv')).opacity);

  // mobile resize: transform 必须按新宽度重新吸附
  await page.setViewportSize({ width: 390, height: 844 }); await page.waitForTimeout(400);
  r.mobileTransform = await page.locator('#track').evaluate(el => el.style.transform);

  r.consoleErrors = errors;
  const pass = errors.length === 0 && String(r.pageCount) === String(r.totalShown)
    && r.afterArrow === '2' && r.afterHome === '1' && r.afterDrag === '2';
  console.log(JSON.stringify(r, null, 2));
  console.log(pass ? 'VERIFY PASS' : 'VERIFY FAIL');
  await b.close();
  process.exit(pass ? 0 : 1);
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
