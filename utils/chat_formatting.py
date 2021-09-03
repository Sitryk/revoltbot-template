import logging


log = logging.getLogger("revoltbot.utils.chat_formatting")


def box(text: str, formatting_language: str = ""):
    """Return a string of text in a codeblock."""
    boxed_string = f"```{formatting_language}\n{text}\n```"
    if len(boxed_string) > 2000:
        log.info("box() returned a string with over 2000 characters.")
    return boxed_string


def humanize_seconds(seconds: int):
    """Convert seconds to readable format."""
    seconds = int(seconds)
    days = seconds // 86400
    hours = (seconds - days * 86400) // 3600
    minutes = (seconds - days * 86400 - hours * 3600) // 60
    seconds = seconds - days * 86400 - hours * 3600 - minutes * 60
    result = (
        ("{0} day{1}, ".format(days, "s" if days != 1 else "") if days else "")
        + ("{0} hour{1}, ".format(hours, "s" if hours != 1 else "") if hours else "")
        + ("{0} minute{1}, ".format(minutes, "s" if minutes != 1 else "") if minutes else "")
        + ("{0} second{1} ".format(seconds, "s" if seconds != 1 else "") if seconds else "")
    )
    return result


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
