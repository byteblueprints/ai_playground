def format_agent_response(agent_response: dict) -> str:
    messages = agent_response.get("messages", []) if isinstance(agent_response, dict) else []
    if not messages:
        return str(agent_response)

    last_message = messages[-1]
    content = getattr(last_message, "content", "")
    if isinstance(content, str):
        return content if content else str(last_message)

    if isinstance(content, list):
        text_chunks: list[str] = []
        for block in content:
            if isinstance(block, str):
                text_chunks.append(block)
                continue

            if isinstance(block, dict):
                if block.get("type") == "text" and isinstance(block.get("text"), str):
                    text_chunks.append(block["text"])
                continue

            block_type = getattr(block, "type", None)
            block_text = getattr(block, "text", None)
            if block_type == "text" and isinstance(block_text, str):
                text_chunks.append(block_text)

        formatted_text = "\n".join(chunk.strip() for chunk in text_chunks if chunk and chunk.strip())
        if formatted_text:
            return formatted_text

    return str(content) if content else str(last_message)
