export const telegramLink = (username) => `https://t.me/${String(username || '').replace(/^@/, '')}`

export const discordLink = (username) =>
  `https://discord.com/users/@${encodeURIComponent(String(username || '').replace(/^@/, ''))}`

