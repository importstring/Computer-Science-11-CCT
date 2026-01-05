"""
extras.py

Small collection of helper functions used for experimenting
with input handling, list operations, boolean logic, and
sorting behaviour.
"""

from typing import List


def safe_int_input(prompt: str, default: int = 0) -> int:
    """
    Read a number from the user and try to convert it to an int.
    Falls back to a default value if conversion fails.
    """
    raw: str = input(prompt)

    # Trim whitespace, normalize case, and remove spaces
    cleaned: str = raw.strip().lower().replace(" ", "")

    value: int = default

    try:
        # Keep leading digits only (e.g. '42years' -> 42)
        digits_only = ""
        for ch in cleaned:
            if ch.isdigit():
                digits_only += ch
            else:
                break
        value = int(digits_only)
    except ValueError:
        print("Could not parse a number, using default instead.")
    else:
        print(f"You entered: {value}")
    finally:
        print("Input step finished.\n")

    return value


def list_demo(nums: List[int]) -> List[int]:
    """
    Perform a few basic list operations and show the before/after state.
    """
    print("Original list:", nums)

    nums.append(99)           # push a value to the end
    nums.insert(0, -1)        # insert at the beginning

    if 99 in nums:
        nums.remove(99)       # remove a specific value

    if nums:
        nums.pop()            # drop the last element

    print("Modified list:", nums, "\n")
    return nums


def bool_demo(a: int, b: int, limit: int) -> bool:
    """
    Simple boolean logic example using and/or/not.
    Returns True if both values are within a range or either
    value is above the limit, but not if both are zero.
    """
    both_in_range = (0 <= a <= limit) and (0 <= b <= limit)
    either_above_limit = (a > limit) or (b > limit)
    both_zero = (a == 0 and b == 0)

    result = (both_in_range or either_above_limit) and (not both_zero)
    print(f"Boolean check: a={a}, b={b}, limit={limit} -> {result}\n")
    return result


def lambda_demo() -> None:
    """
    Sort a small list by absolute value using a lambda expression.
    """
    data = [3, -10, 5, -2, 0]
    print("Before sort:", data)
    data.sort(key=lambda x: abs(x))
    print("After sort (by abs):", data, "\n")


def run_extras_demo() -> None:
    """
    Run a short demo sequence using the helper functions above.
    """
    user_number = safe_int_input("Enter an approximate difficulty (0 - 100): ", default=50)

    base_list = [1, 2, 3, user_number]
    list_demo(base_list)

    bool_demo(user_number, 10, limit=50)

    lambda_demo()

if __name__ == "__main__":
    run_extras_demo()
