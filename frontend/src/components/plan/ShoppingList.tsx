'use client'

import { useState } from 'react'
import { ShoppingListItem } from './ShoppingListItem'

interface ShoppingListProps {
  shoppingList: Record<string, Array<{ name: string; quantity?: number; unit?: string }>>
}

const CATEGORY_LABELS: Record<string, string> = {
  produce: 'Produce',
  protein: 'Protein',
  grain: 'Grains',
  dairy: 'Dairy',
  other: 'Other',
}

const CATEGORY_ORDER = ['produce', 'protein', 'grain', 'dairy', 'other']

export function ShoppingList({ shoppingList }: ShoppingListProps) {
  const [shareSupported] = useState(() => {
    if (typeof navigator !== 'undefined' && 'share' in navigator) {
      return true
    }
    return false
  })

  const handleShare = async () => {
    if (!shareSupported) {
      // Fallback: copy to clipboard
      const text = formatShoppingListText(shoppingList)
      await navigator.clipboard.writeText(text)
      alert('Shopping list copied to clipboard!')
      return
    }

    const text = formatShoppingListText(shoppingList)
    try {
      await navigator.share({
        title: 'Meal Plan Shopping List',
        text: text,
      })
    } catch (err) {
      // User cancelled or error
      console.error('Error sharing:', err)
    }
  }

  const formatShoppingListText = (
    list: Record<string, Array<{ name: string; quantity?: number; unit?: string }>>
  ): string => {
    let text = 'Shopping List\n\n'
    for (const category of CATEGORY_ORDER) {
      const items = list[category]
      if (items && items.length > 0) {
        text += `${CATEGORY_LABELS[category] || category}:\n`
        for (const item of items) {
          if (item.quantity) {
            text += `  - ${item.name}: ${item.quantity} ${item.unit || ''}\n`
          } else {
            text += `  - ${item.name}\n`
          }
        }
        text += '\n'
      }
    }
    return text.trim()
  }

  const handleCopyToClipboard = async () => {
    const text = formatShoppingListText(shoppingList)
    await navigator.clipboard.writeText(text)
    alert('Shopping list copied to clipboard!')
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-semibold">Shopping List</h2>
        <div className="flex space-x-2">
          {shareSupported ? (
            <button
              onClick={handleShare}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Share
            </button>
          ) : (
            <button
              onClick={handleCopyToClipboard}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Copy
            </button>
          )}
        </div>
      </div>

      <div className="space-y-6">
        {CATEGORY_ORDER.map((category) => {
          const items = shoppingList[category]
          if (!items || items.length === 0) {
            return null
          }

          return (
            <div key={category}>
              <h3 className="mb-3 text-lg font-medium text-gray-900">
                {CATEGORY_LABELS[category] || category}
              </h3>
              <div className="space-y-2">
                {items.map((item, idx) => (
                  <ShoppingListItem
                    key={`${category}-${idx}`}
                    name={item.name}
                    quantity={item.quantity}
                    unit={item.unit}
                    category={category}
                  />
                ))}
              </div>
            </div>
          )
        })}

        {Object.keys(shoppingList).length === 0 && (
          <p className="text-center text-gray-500">No items in shopping list</p>
        )}
      </div>
    </div>
  )
}

