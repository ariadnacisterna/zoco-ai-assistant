const CHAT_API_PATH = '/api/chat'
const MAX_MESSAGE_LENGTH = 1000
const MESSAGE_INPUT_ROWS = 1

const ENVIRONMENT_VARIABLE = {
  API_BASE_URL: 'VITE_API_BASE_URL',
  HUMAN_SUPPORT_URL: 'VITE_HUMAN_SUPPORT_URL',
} as const

function getRequiredEnvironmentValue(
  value: string | undefined,
  variableName: string,
): string {
  const normalizedValue = value?.trim()

  if (!normalizedValue) {
    throw new Error(`Falta configurar la variable ${variableName}.`)
  }

  return normalizedValue
}

export const CHAT_CONFIG = {
  API_BASE_URL: getRequiredEnvironmentValue(
    import.meta.env.VITE_API_BASE_URL,
    ENVIRONMENT_VARIABLE.API_BASE_URL,
  ),
  API_PATH: CHAT_API_PATH,
  MAX_MESSAGE_LENGTH,
  HUMAN_SUPPORT_URL: getRequiredEnvironmentValue(
    import.meta.env.VITE_HUMAN_SUPPORT_URL,
    ENVIRONMENT_VARIABLE.HUMAN_SUPPORT_URL,
  ),
  MESSAGE_INPUT_ROWS,
} as const

export const HTTP_CONFIG = {
  METHOD_POST: 'POST',
  CONTENT_TYPE_HEADER: 'Content-Type',
  JSON_CONTENT_TYPE: 'application/json',
} as const
