import { test, expect } from '@playwright/test'

test.describe('Templates Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/templates')
  })

  test('should display templates page', async ({ page }) => {
    await expect(page.locator('.page-header h1')).toContainText('模板中心')
  })

  test('should display category filters', async ({ page }) => {
    await expect(page.locator('.el-radio-button')).toBeVisible()
  })

  test('should filter templates by category', async ({ page }) => {
    await page.click('.el-radio-button:has-text("商务类")')
    
    await expect(page).toHaveURL(/category=business/)
  })
})

test.describe('Pricing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pricing')
  })

  test('should display pricing plans', async ({ page }) => {
    await expect(page.locator('.pricing-card')).toHaveCount(2)
  })

  test('should display feature comparison table', async ({ page }) => {
    await expect(page.locator('.comparison-table')).toBeVisible()
    await expect(page.locator('.el-table')).toBeVisible()
  })

  test('should display FAQ section', async ({ page }) => {
    await expect(page.locator('.faq-section')).toBeVisible()
    await expect(page.locator('.el-collapse')).toBeVisible()
  })
})

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display hero section', async ({ page }) => {
    await expect(page.locator('.hero')).toBeVisible()
    await expect(page.locator('.hero h1')).toContainText('AI智能PPT生成平台')
  })

  test('should display features section', async ({ page }) => {
    await expect(page.locator('.features')).toBeVisible()
    await expect(page.locator('.feature-card').first()).toBeVisible()
  })

  test('should display how it works section', async ({ page }) => {
    await expect(page.locator('.how-it-works')).toBeVisible()
    await expect(page.locator('.step').first()).toBeVisible()
  })

  test('should have working CTA buttons', async ({ page }) => {
    await page.click('text=立即开始')
    await expect(page).toHaveURL(/.*(register|create)/)
  })
})
