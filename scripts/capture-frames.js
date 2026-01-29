#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

async function main(){
  const svgRelative = process.argv[2] || '../portfolio/exercises/week4/banner (1).svg';
  const outDir = process.argv[3] || path.resolve(process.cwd(),'gif-frames');
  const duration = parseFloat(process.argv[4]) || 8; // seconds
  const fps = parseFloat(process.argv[5]) || 15;

  if(!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  const wrapperPath = path.resolve(__dirname, 'wrapper-banner.html');
  const wrapperUrl = 'file://' + wrapperPath;

  console.log(`Capturing frames from: ${svgRelative}`);
  console.log(`Output frames directory: ${outDir}`);
  console.log(`Duration: ${duration}s @ ${fps}fps => ${Math.ceil(duration*fps)} frames`);

  const browser = await puppeteer.launch({args:['--disable-features=VizDisplayCompositor']});
  const page = await browser.newPage();

  // set viewport to match the SVG viewBox size (or scale down)
  const width = 1600, height = 400;
  await page.setViewport({width, height});

  // make the SVG path available to the wrapper by writing the path into the wrapper query
  await page.goto(wrapperUrl + `?src=${encodeURIComponent(svgRelative)}`);
  await page.waitForTimeout(300); // small delay for initial render

  const totalFrames = Math.ceil(duration * fps);
  const delayMs = Math.round(1000 / fps);

  for(let i=0;i<totalFrames;i++){
    const filename = path.join(outDir, `frame-${String(i).padStart(4,'0')}.png`);
    await page.screenshot({path: filename});
    process.stdout.write(`\rSaved ${i+1}/${totalFrames} frames`);
    await page.waitForTimeout(delayMs);
  }

  console.log('\nDone capturing frames.');
  await browser.close();
  console.log('\nNext step: assemble frames into an animated GIF. See scripts/README.md for commands.');
}

main().catch(err=>{console.error(err);process.exit(1)});
