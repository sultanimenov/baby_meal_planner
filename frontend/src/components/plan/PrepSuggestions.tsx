'use client'

interface PrepSuggestion {
  day?: string
  suggestion: string
  items?: string[]
}

interface PrepSuggestionsProps {
  suggestions: PrepSuggestion[]
}

export function PrepSuggestions({ suggestions }: PrepSuggestionsProps) {
  if (!suggestions || suggestions.length === 0) {
    return null
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-xl font-semibold">Prep Suggestions</h2>
      <div className="space-y-4">
        {suggestions.map((suggestion, idx) => (
          <div key={idx} className="rounded-lg bg-blue-50 p-4">
            {suggestion.day && (
              <p className="mb-1 text-sm font-semibold text-blue-900">
                {suggestion.day}
              </p>
            )}
            <p className="text-blue-800">{suggestion.suggestion}</p>
            {suggestion.items && suggestion.items.length > 0 && (
              <div className="mt-2">
                <p className="text-sm font-medium text-blue-900">Items:</p>
                <ul className="mt-1 list-disc pl-5 text-sm text-blue-700">
                  {suggestion.items.map((item, itemIdx) => (
                    <li key={itemIdx}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}


