        #!/usr/bin/env node
        /*
         * Browser bridge — uses playwright-core with the Chromium already installed
         * by Termux (pkg install chromium). Set CHROME_EXECUTABLE_PATH to the
         * chromium binary (e.g. /data/data/com.termux/files/usr/bin/chromium).
         *
         * Usage: node browser_bridge.js <url>
         */
        const { chromium } = require('playwright-core');

        async function main() {
          const url = process.argv[2];
          if (!url) {
            console.error('usage: node browser_bridge.js <url>');
            process.exit(2);
          }
          const executablePath = process.env.CHROME_EXECUTABLE_PATH;
          if (!executablePath) {
            console.error('CHROME_EXECUTABLE_PATH is required');
            process.exit(2);
          }
          const browser = await chromium.launch({ executablePath, headless: true });
          try {
            const ctx = await browser.newContext();
            const page = await ctx.newPage();
            await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30_000 });
            const title = await page.title();
            const text = await page.evaluate(() => document.body.innerText.slice(0, 4000));
            process.stdout.write(JSON.stringify({ url, title, text }) + '
');
          } finally {
            await browser.close();
          }
        }

        main().catch((err) => {
          console.error(err.message);
          process.exit(1);
        });
