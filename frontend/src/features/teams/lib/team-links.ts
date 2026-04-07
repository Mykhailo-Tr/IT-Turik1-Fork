export const telegramLink = (username: string) =>
  `https://t.me/${String(username || '').replace(/^@/, '')}`

export const discordLink = (username: string) =>
  `https://discord.com/users/@${encodeURIComponent(String(username || '').replace(/^@/, ''))}`
