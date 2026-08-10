import { CHAT_CONFIG } from '../config/chat'

export const CHAT_COPY = {
  WELCOME_HEADER_LABEL: 'Asistente virtual',
  WELCOME_TITLE: 'Todas tus consultas en un solo lugar',
  WELCOME_DESCRIPTION: 'Preciso. Sencillo. Seguro.',
  START_CONVERSATION: 'Iniciar nueva conversación',
  VERIFIED_INFORMATION:
    'Respuestas basadas en la información de la página oficial de ZOCO.',
  CHAT_TITLE: 'Asistente ZOCO',
  CHAT_STATUS: 'En línea para ayudarte',
  RETURN_TO_WELCOME: 'Volver a la pantalla de bienvenida',
  NEW_CONVERSATION: 'Nueva conversación',
  INITIAL_MESSAGE:
    '¡Hola! Soy el asistente virtual de ZOCO. ¿Qué te gustaría consultar?',
  MESSAGE_PLACEHOLDER: 'Escribí tu consulta...',
  MESSAGE_INPUT_LABEL: 'Mensaje para el asistente',
  SEND_MESSAGE: 'Enviar mensaje',
  WRITING_RESPONSE: 'ZOCO está preparando una respuesta...',
  USER_MESSAGE_LABEL: 'Tu mensaje',
  ASSISTANT_MESSAGE_LABEL: 'Respuesta del asistente',
  ASSISTANT_AVATAR_LABEL: 'Z',
  SOURCES_TITLE: 'Fuentes utilizadas',
  OPEN_SOURCE_LABEL: 'Abrir fuente',
  HUMAN_SUPPORT_TITLE: '¿Necesitás más ayuda?',
  HUMAN_SUPPORT_DESCRIPTION:
    'Podés continuar la consulta con una persona del equipo de ZOCO.',
  HUMAN_SUPPORT_ACTION: 'Hablar con una persona',
  ERROR_TITLE: 'No pudimos completar la consulta',
  ERROR_DEFAULT:
    'Ocurrió un problema al comunicarnos con el servicio. Intentá nuevamente.',
  ERROR_INVALID_RESPONSE: 'El servidor devolvió una respuesta inválida.',
  ERROR_MESSAGE_TOO_LONG: `El mensaje no puede superar los ${CHAT_CONFIG.MAX_MESSAGE_LENGTH} caracteres.`,
  ERROR_CLOSE: 'Cerrar aviso',
  CHARACTER_LIMIT_LABEL: 'caracteres disponibles',
} as const

export const KEYBOARD_KEY = {
  ENTER: 'Enter',
  TAB: 'Tab',
} as const

export const SCROLL_BEHAVIOR = {
  NEW_MESSAGE: 'smooth',
} as const
