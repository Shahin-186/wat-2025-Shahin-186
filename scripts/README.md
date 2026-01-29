Banner GIF conversion helper

Steps to capture frames and assemble an animated GIF from the animated SVG (`banner (1).svg`):

1. Install dependencies (requires Node.js >= 16):

   npm install

2. Run the capture script (adjust args as needed):

   node capture-frames.js "../portfolio/exercises/week4/banner (1).svg" ./gif-frames 8 15

   This captures ~8 seconds @15fps into `./gif-frames/`.

3. Assemble frames into GIF using ImageMagick (if installed):

   convert -delay 6 -loop 0 gif-frames/frame-*.png banner.gif

   Or with newer ImageMagick (`magick`):

   magick convert -delay 6 -loop 0 gif-frames/frame-*.png banner.gif

   Or use gifsicle for a smaller GIF:

   gifsicle --delay=6 --loopcount gif-frames/frame-*.png > banner.gif

Notes:
- The SVG uses SMIL animation and <animateMotion>, which is supported by Chromium; capturing with Puppeteer ensures those animations are rendered.
- Producing GIFs from SVG can increase file size; consider using an animated WebP or keeping the SVG if you need a smaller, scalable result.
