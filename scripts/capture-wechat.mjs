import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const skillDir = path.resolve(__dirname, '..')

const args = new Map()
for (let i = 2; i < process.argv.length; i += 2) {
  args.set(process.argv[i], process.argv[i + 1])
}

const csvPath = path.resolve(args.get('--csv') || path.join(skillDir, 'references', '2050-articles-2026.csv'))
const outDir = path.resolve(args.get('--out') || path.join(skillDir, 'assets', 'wechat-screenshots'))
const limit = Number(args.get('--limit') || '0')

function parseCsvLine(line) {
  const cells = []
  let current = ''
  let quoted = false
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i]
    const next = line[i + 1]
    if (ch === '"' && quoted && next === '"') {
      current += '"'
      i += 1
    } else if (ch === '"') {
      quoted = !quoted
    } else if (ch === ',' && !quoted) {
      cells.push(current)
      current = ''
    } else {
      current += ch
    }
  }
  cells.push(current)
  return cells
}

function slugTitle(title, index) {
  const compact = title
    .replace(/[\\/:*?"<>|]/g, '')
    .replace(/\s+/g, '-')
    .slice(0, 42)
  return `${String(index + 1).padStart(3, '0')}-${compact || 'article'}.png`
}

function getTitle(article) {
  return article['标题'] || article.title || `article-${article.source_order || ''}`
}

function getUrl(article) {
  return article['链接'] || article.url || ''
}

function readArticles(filePath) {
  const text = fs.readFileSync(filePath, 'utf8').replace(/^\uFEFF/, '')
  const lines = text.split(/\r?\n/).filter(Boolean)
  const headers = parseCsvLine(lines[0])
  return lines.slice(1).map((line) => {
    const cells = parseCsvLine(line)
    return Object.fromEntries(headers.map((header, idx) => [header, cells[idx] || '']))
  })
}

async function loadAllImages(page) {
  await page.evaluate(async () => {
    const imgs = Array.from(document.querySelectorAll('img'))
    for (const img of imgs) {
      if (img.dataset.src) {
        img.src = img.dataset.src
        img.removeAttribute('data-src')
      }
      if (img.dataset.srcset) {
        img.srcset = img.dataset.srcset
        img.removeAttribute('data-srcset')
      }
    }
    await Promise.all(imgs.map((img) => {
      if (img.complete && img.naturalWidth > 0) return Promise.resolve()
      return new Promise((resolve) => {
        img.onload = resolve
        img.onerror = resolve
        setTimeout(resolve, 8000)
      })
    }))
  })
}

async function scrollThroughPage(page) {
  let lastHeight = 0
  let stable = 0
  while (stable < 3) {
    const height = await page.evaluate(() => document.documentElement.scrollHeight)
    if (height === lastHeight) stable += 1
    else stable = 0
    lastHeight = height

    const done = await page.evaluate(() => window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 60)
    if (done && stable >= 1) break
    await page.mouse.wheel(0, 900)
    await page.waitForTimeout(350)
    await loadAllImages(page)
  }
}

async function captureArticle(page, article, index) {
  const url = getUrl(article)
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(8000)
  await scrollThroughPage(page)
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(2000)
  await loadAllImages(page)
  await page.waitForTimeout(6000)
  const output = path.join(outDir, slugTitle(getTitle(article), index))
  await page.screenshot({ path: output, fullPage: true, timeout: 120000 })
  return output
}

async function main() {
  fs.mkdirSync(outDir, { recursive: true })
  const allArticles = readArticles(csvPath).filter((row) => getUrl(row).startsWith('http'))
  const articles = limit > 0 ? allArticles.slice(0, limit) : allArticles
  console.log(`Found ${articles.length} article links from ${csvPath}`)

  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-font-subpixel-positioning', '--disable-skia-runtime'],
  })
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 2,
  })
  const page = await context.newPage()

  for (let i = 0; i < articles.length; i += 1) {
    const article = articles[i]
    try {
      console.log(`[${i + 1}/${articles.length}] ${getTitle(article)}`)
      const output = await captureArticle(page, article, i)
      console.log(`  saved ${output}`)
    } catch (error) {
      console.error(`  failed ${getUrl(article)}: ${error.message}`)
    }
  }

  await browser.close()
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
