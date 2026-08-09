TEST_CHUNK_SIZE = 10
TEST_CHUNK_OVERLAP = 2
TEST_OVERLAPPING_TEXT = "abcdefghijklmnopqrstuvw"
TEST_BLANK_TEXT = "   "

EXPECTED_OVERLAPPING_CHUNKS = [
    "abcdefghij",
    "ijklmnopqr",
    "qrstuvw",
]
