import React from 'react'
import { render, screen } from '@testing-library/react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './Card'

describe('Card components', () => {
  test('Card renders correctly', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
          <CardDescription>Description</CardDescription>
        </CardHeader>
        <CardContent>Card content goes here.</CardContent>
      </Card>
    )

    expect(screen.getByText('Card Title')).toBeInTheDocument()
    expect(screen.getByText('Description')).toBeInTheDocument()
    expect(screen.getByText('Card content goes here.')).toBeInTheDocument()
  })

  test('Card subcomponents render with proper structure', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Header Title</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Content inside</p>
        </CardContent>
      </Card>
    )

    expect(screen.getByText('Header Title')).toBeInTheDocument()
    expect(screen.getByText('Content inside')).toBeInTheDocument()
  })
})
