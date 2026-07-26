def fib(n: int) -> int:
    """Return the nth Fibonacci number (0-indexed)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python fibonacci.py <non-negative integer>")
        sys.exit(1)
    try:
        num = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid integer.")
        sys.exit(1)
    print(fib(num))
