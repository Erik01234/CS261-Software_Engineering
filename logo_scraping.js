const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
    const browser = await puppeteer.launch({
        headless: false // so we can see what the script is doing
    });
    const page = await browser.newPage();
    const dataFolderPath = path.resolve(__dirname, 'data');
    if (!fs.existsSync(dataFolderPath)) {
        fs.mkdirSync(dataFolderPath);
    }
    const filePath = path.resolve(dataFolderPath, 'company_logos_remaining.csv');
    fs.writeFileSync(filePath, `Ticker,LogoURL\n`); // Write the header first

    // Go to the Wikipedia page that lists the S&P 500 companies
    await page.goto('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', { waitUntil: 'domcontentloaded' });

    // Retrieve all the tickers and URLs for the company pages
    const companies = await page.evaluate(() =>
        Array.from(document.querySelectorAll('table.wikitable tbody tr')).map(row => {
            const tickerElement = row.querySelector('td:first-child a');
            const linkElement = row.querySelector('td:nth-child(2) a');
            return {
                ticker: tickerElement ? tickerElement.textContent.trim() : null,
                url: linkElement ? linkElement.href : null
            };
        }).filter(company => company.ticker && company.url) // Filter out any null entries
    );

    const targetCompanies = companies.slice(464, 503);

    for (const { ticker, url } of targetCompanies) {
        try {
            await page.goto(url, { waitUntil: 'domcontentloaded' });
            const logoUrl = await page.evaluate(() => {
                const imageElement = document.querySelector('img.mw-file-element');
                return imageElement ? imageElement.src : null;
            });

            if (logoUrl) {
                const absoluteLogoUrl = logoUrl.startsWith('//') ? `https:${logoUrl}` : logoUrl;
                fs.appendFileSync(filePath, `"${ticker}","${absoluteLogoUrl}"\n`);
            } else {
                fs.appendFileSync(filePath, `"${ticker}",""\n`); // Write empty logo URL if not found
            }
        } catch (error) {
            console.error(`Error processing ${ticker}: ${error}`);
            fs.appendFileSync(filePath, `"${ticker}","ERROR"\n`); // Write ERROR in the logo URL column
        }
    }

    console.log('CSV file has been written.');

    await browser.close();
})();
