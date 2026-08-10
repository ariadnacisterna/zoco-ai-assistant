const ROOT_PATH = '/'

export function formatSourceLocation(sourceUrl: string): string {
  try {
    const url = new URL(sourceUrl)
    const location = decodeURIComponent(
      `${url.pathname}${url.search}${url.hash}`,
    )

    return location === ROOT_PATH ? url.hostname : `${url.hostname}${location}`
  } catch {
    return sourceUrl
  }
}
