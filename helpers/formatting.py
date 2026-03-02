from html import escape


def build_message(title="", description="", fields=None, footer=""):
    """Build an HTML-formatted message string that mirrors a Discord embed layout.

    Args:
        title: Bold header line.
        description: Main body text.
        fields: List of (name, value) tuples rendered as labeled sections.
        footer: Italic footer line.
    """
    parts = []

    if title:
        parts.append(f"<b>{escape(title)}</b>")
    if description:
        parts.append(escape(description))
    if fields:
        for name, value in fields:
            parts.append(f"<b>{escape(name)}</b>\n{escape(value)}")
    if footer:
        parts.append(f"<i>{escape(footer)}</i>")

    return "\n\n".join(parts)


def build_message_raw(title="", description="", fields=None, footer=""):
    """Build an HTML-formatted message where field values already contain HTML.

    Use this when field values include pre-formatted HTML (bold, links, etc.).
    Title, description, and footer are still escaped.
    """
    parts = []

    if title:
        parts.append(f"<b>{escape(title)}</b>")
    if description:
        parts.append(description)
    if fields:
        for name, value in fields:
            parts.append(f"<b>{escape(name)}</b>\n{value}")
    if footer:
        parts.append(f"<i>{escape(footer)}</i>")

    return "\n\n".join(parts)
