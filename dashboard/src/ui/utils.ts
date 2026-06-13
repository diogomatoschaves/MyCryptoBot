export const hexToRgba = (hex: string, alpha: number): string => {
  const match = hex.replace('#', '')
  const full = match.length === 3
    ? match.split('').map(c => c + c).join('')
    : match
  const num = parseInt(full, 16)
  const r = (num >> 16) & 255
  const g = (num >> 8) & 255
  const b = num & 255
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}
