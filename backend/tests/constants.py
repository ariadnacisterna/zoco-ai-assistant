from datetime import UTC, datetime
from uuid import UUID

TEST_CHUNK_SIZE = 10
TEST_CHUNK_OVERLAP = 2
TEST_OVERLAPPING_TEXT = "abcdefghijklmnopqrstuvw"
TEST_BLANK_TEXT = "   "

EXPECTED_OVERLAPPING_CHUNKS = [
    "abcdefghij",
    "ijklmnopqr",
    "qrstuvw",
]

TEST_EMBEDDING_MODEL = "gemini-embedding-2"
TEST_EMBEDDING_DIMENSION = 3

TEST_PAGE_TITLE = "Cobros con ZOCO"
TEST_PAGE_CONTENT = "Información completa de la página."
TEST_FIRST_CHUNK = "Primer contenido relevante."
TEST_SECOND_CHUNK = "Segundo contenido relevante."
TEST_ZERO_NORM_CHUNK = "Contenido con vector nulo."
TEST_MISMATCHED_DIMENSION_CHUNK = "Contenido con dimensión incorrecta."
TEST_QUERY = "¿Cómo puedo cobrar con ZOCO?"
TEST_SOURCE_URL = "https://zocopagos.com/prueba"

TEST_PRIMARY_EMBEDDING = [1.0, 0.0, 0.0]
TEST_SECONDARY_EMBEDDING = [0.8, 0.2, 0.0]
TEST_IRRELEVANT_EMBEDDING = [0.0, 1.0, 0.0]

TEST_RETRIEVAL_TOP_K = 2
EXPECTED_RETRIEVAL_RESULT_COUNT = 1
TEST_DUPLICATE_SOURCE_URL = "https://zocopagos.com/pagos"
TEST_MIN_SIMILARITY = 0.5

TEST_GENERATION_MODEL = "gemini-generation-model"
TEST_CHAT_MESSAGE = "¿Cómo puedo cobrar con ZOCO?"
TEST_CHAT_ANSWER = "Podés cobrar con las soluciones de ZOCO."
TEST_MAX_MESSAGE_LENGTH = 1000
TEST_SOURCE_SIMILARITY = 0.9

TEST_CONVERSATION_ID = UUID("12345678-1234-5678-1234-567812345678")
TEST_CONVERSATION_CONTEXT_MESSAGES = 6
TEST_PREVIOUS_USER_MESSAGE = "¿También puedo cobrar con un enlace?"
TEST_PREVIOUS_ASSISTANT_MESSAGE = "Sí, ZOCO permite generar enlaces de pago."
TEST_MESSAGE_CREATED_AT = datetime(2026, 1, 1, tzinfo=UTC)
EXPECTED_CONVERSATION_MESSAGE_COUNT = 2
