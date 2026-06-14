from python_examples.langchain_framework.agent_with_file_system_middleware import ask_agent as ask_agent_with_fs_middleware

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def format_agent_response(agent_response) -> str:
    messages = agent_response.get("messages", []) if isinstance(agent_response, dict) else []
    if not messages:
        return str(agent_response)

    last_message = messages[-1]
    content = getattr(last_message, "content", "")
    return content if content else str(last_message)


def main():
    print("Chat started. Press Ctrl+C to exit.\n")

    try:
        while True:
            user_input = input(f"{GREEN}You{RESET}: ").strip()
            if not user_input:
                continue
            agent_response = ask_agent_with_fs_middleware(user_input)
            print(f"{RED}Agent{RESET}: {format_agent_response(agent_response)}")
            print()
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()
