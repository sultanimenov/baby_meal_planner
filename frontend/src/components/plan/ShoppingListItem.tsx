'use client'

import { useState } from 'react'

interface ShoppingListItemProps {
  name: string
  quantity?: number
  unit?: string
  category: string
  onToggle?: (checked: boolean) => void
  onQuantityChange?: (quantity: number) => void
}

export function ShoppingListItem({
  name,
  quantity,
  unit,
  category,
  onToggle,
  onQuantityChange,
}: ShoppingListItemProps) {
  const [checked, setChecked] = useState(false)
  const [editQuantity, setEditQuantity] = useState(quantity || 1)

  const handleToggle = () => {
    const newChecked = !checked
    setChecked(newChecked)
    onToggle?.(newChecked)
  }

  const handleQuantityChange = (newQuantity: number) => {
    if (newQuantity > 0) {
      setEditQuantity(newQuantity)
      onQuantityChange?.(newQuantity)
    }
  }

  return (
    <div
      className={`flex items-center justify-between rounded-lg border p-3 ${
        checked ? 'bg-gray-50 opacity-60' : 'bg-white'
      }`}
    >
      <div className="flex items-center space-x-3">
        <input
          type="checkbox"
          checked={checked}
          onChange={handleToggle}
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <div>
          <p className={`font-medium ${checked ? 'line-through text-gray-500' : 'text-gray-900'}`}>
            {name}
          </p>
          {quantity !== undefined && (
            <div className="mt-1 flex items-center space-x-2">
              <input
                type="number"
                min="0.1"
                step="0.1"
                value={editQuantity}
                onChange={(e) => handleQuantityChange(parseFloat(e.target.value))}
                className="w-20 rounded border border-gray-300 px-2 py-1 text-sm"
                disabled={checked}
              />
              {unit && <span className="text-sm text-gray-600">{unit}</span>}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}


