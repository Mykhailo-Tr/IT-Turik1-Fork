interface FormatDateOptions {
  showHours?: boolean
}
export const formatDate = (date: Date, options?: FormatDateOptions) => {
  if (options?.showHours)
    return date.toLocaleDateString('uk-UA', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
    })

  return date.toLocaleDateString('uk-UA', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export function truncateText(text: string, maxLength: number) {
  if (text.length > maxLength) return text.slice(0, maxLength) + '...'
  return text
}
