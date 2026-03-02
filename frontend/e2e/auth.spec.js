import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display home page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('AI智能PPT生成平台')
  })

  test('should navigate to login page', async ({ page }) => {
    await page.click('text=登录')
    await expect(page).toHaveURL(/.*login/)
    await expect(page.locator('h1')).toContainText('登录')
  })

  test('should navigate to register page', async ({ page }) => {
    await page.click('text=注册')
    await expect(page).toHaveURL(/.*register/)
    await expect(page.locator('h1')).toContainText('注册')
  })

  test('should show validation errors on login', async ({ page }) => {
    await page.goto('/login')
    await page.click('.login-btn')
    
    await expect(page.locator('.el-form-item__error')).toBeVisible()
  })

  test('should show validation errors on register', async ({ page }) => {
    await page.goto('/register')
    await page.click('.register-btn')
    
    await expect(page.locator('.el-form-item__error')).toBeVisible()
  })
})

test.describe('Protected Routes', () => {
  test('should redirect to login when accessing protected route', async ({ page }) => {
    await page.goto('/create')
    
    await expect(page).toHaveURL(/.*login/)
  })

  test('should redirect to login when accessing projects', async ({ page }) => {
    await page.goto('/projects')
    
    await expect(page).toHaveURL(/.*login/)
  })
})

test.describe('Navigation', () => {
  test('should navigate to templates page', async ({ page }) => {
    await page.goto('/')
    await page.click('text=模板中心')
    
    await expect(page).toHaveURL(/.*templates/)
    await expect(page.locator('.page-header h1')).toContainText('模板中心')
  })

  test('should navigate to pricing page', async ({ page }) => {
    await page.goto('/')
    await page.click('text=会员订阅')
    
    await expect(page).toHaveURL(/.*pricing/)
    await expect(page.locator('.page-header h1')).toContainText('会员订阅')
  })
})
