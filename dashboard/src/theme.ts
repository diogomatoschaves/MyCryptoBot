// Central design tokens, mirrored from the CSS variables in index.css so that
// JS consumers (charts, inline styles) share the exact same palette.

export const theme = {
  bg: '#0a0e15',
  bgRaised: '#0f141e',
  bgElevated: '#141b28',
  bgInput: '#0c111a',
  border: '#1c2433',
  borderStrong: '#283142',
  text: '#e8edf4',
  textDim: '#8c97aa',
  textFaint: '#5e6878',
  accent: '#c6f432',
  green: '#2ee6a8',
  red: '#ff5470',
  yellow: '#ffc24b',
  blue: '#4f9dff',
  fontUi: "'Archivo', 'Helvetica Neue', Arial, sans-serif",
  fontMono: "'JetBrains Mono', 'SF Mono', Menlo, monospace",
}

export type BotColorName =
  | 'purple'
  | 'violet'
  | 'pink'
  | 'blue'
  | 'teal'
  | 'green'
  | 'red'
  | 'yellow'

// Per-bot identity colors, tuned to read well on the dark surfaces.
export const BOT_COLORS: Record<BotColorName, string> = {
  purple: '#c084fc',
  violet: '#8b8bf4',
  pink: '#f472b6',
  blue: '#5fa8ff',
  teal: '#2dd4bf',
  green: '#4ade80',
  red: '#fb7185',
  yellow: '#facc15',
}

export const getBotColor = (name?: string): string => {
  if (!name) return theme.textDim
  return BOT_COLORS[name.toLowerCase() as BotColorName] || theme.textDim
}
