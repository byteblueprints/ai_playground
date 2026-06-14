def is_palindrome(num: int) -> bool:
    """
    Checks if a given integer is a palindrome.
    Args:
        num (int): The integer to check.
    Returns:
        bool: True if num is a palindrome, False otherwise.
    """
    original = str(num)
    reversed_num = original[::-1]
    return original == reversed_num


def main():
    try:
        num = int(input("Enter an integer: "))
        if is_palindrome(num):
            print(f"{num} is a palindrome number.")
        else:
            print(f"{num} is not a palindrome number.")
    except ValueError:
        print("Invalid input. Please enter an integer.")


if __name__ == "__main__":
    main()
