import logging


log = logging.getLogger("revoltbot.utils.chat_formatting")


def box(text: str, formatting_language: str = ""):
    """Return a string of text in a codeblock."""
    boxed_string = f"```{formatting_language}\n{text}\n```"
    if len(boxed_string) > 2000:
        log.info("box() returned a string with over 2000 characters.")
    return boxed_string


def pagify(text: str, delim="\n", *, shorten_by=0, page_length=2000):
    """
    Chunk text into manageable chunks.

    This does not respect code blocks or special formatting.
    """
    list_of_chunks = []
    chunk_length = page_length - shorten_by

    deliminator_test = text.rfind(delim)
    if deliminator_test < 0:
        # delim isn't in the text as rfind returns -1
        delim = ""

    while len(text) > chunk_length:
        line_length = text[:chunk_length].rfind(delim)
        list_of_chunks.append(text[:line_length])
        text = text[line_length:].lstrip(delim)
    list_of_chunks.append(text)

    return list_of_chunks
