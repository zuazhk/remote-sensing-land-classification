import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button component', () => {
  test('renders with default props', () => {
    render(<Button>Click me</Button>)
    const btn = screen.getByText('Click me')
    expect(btn).toBeInTheDocument()
    expect(btn.tagName).toBe('BUTTON')
  })

  test('renders with different variants', () => {
    render(<>
      <Button variant="default">Default</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
    </>)
    const def = screen.getByText('Default')
    const out = screen.getByText('Outline')
    const ghs = screen.getByText('Ghost')
    expect(def).toBeInTheDocument()
    expect(out).toBeInTheDocument()
    expect(ghs).toBeInTheDocument()
    
    expect(def.closest('button')?.className).toContain('bg-blue-600')
    expect(out.closest('button')?.className).toContain('border')
    expect(out.closest('button')?.className).toContain('bg-transparent')
    expect(ghs.closest('button')?.className).toContain('bg-transparent')
  })

  test('renders with different sizes', () => {
    render(<>
      <Button size="default">Default</Button>
      <Button size="sm">Small</Button>
      <Button size="lg">Large</Button>
    </>)
    expect(screen.getByText('Default').closest('button')?.className).toContain('h-10')
    expect(screen.getByText('Small').closest('button')?.className).toContain('h-8')
    expect(screen.getByText('Large').closest('button')?.className).toContain('h-12')
  })

  test('handles click events', () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Click</Button>)
    const btn = screen.getByText('Click')
    fireEvent.click(btn)
    expect(onClick).toHaveBeenCalled()
  })

  test('renders asChild when asChild is true', () => {
    render(
      <Button asChild>
        <a href="#">Link</a>
      </Button>
    )
    const link = screen.getByText('Link')
    expect(link.tagName).toBe('A')
    expect(link.closest('a')?.className).toContain('bg-blue-600')
  })

  test('disabled state', () => {
    render(<Button disabled>Can't click</Button>)
    const btn = screen.getByText("Can't click") as HTMLButtonElement
    expect(btn.disabled).toBeTruthy()
  })
})
