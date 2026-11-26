"""
app.py - Student Index Recovery System (Interactive CLI & Runner)
"""

import sys
import ast
from bst_core import format_tree, collect_leaf_ids, Node
from merger import parse_fragments, recover_student_index, merge_fragments


def parse_raw_fragments_string(text: str):
    """
    Parses a string representation of fragments into a structured list.
    Supports:
        - "[[2,1], [3,2,5], [5,4]]"
        - "[2,1], [3,2,5], [5,4]"
    """
    text = text.strip()
    if not text.startswith("["):
        text = f"[{text}]"
    if not text.endswith("]"):
        text = f"{text}]"
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], (int, type(None))):
            return [parsed]
        return parsed
    except Exception as e:
        raise ValueError(f"Could not parse fragments: {e}")


def display_result(result, fragments_input):
    """Displays formatted recovery results or diagnostic error messages."""
    print("=" * 64)
    print("INPUT FRAGMENTS:")
    if isinstance(fragments_input, list):
        for i, f in enumerate(fragments_input, 1):
            if isinstance(f, Node):
                left_id = f.left.id if f.left else None
                right_id = f.right.id if f.right else None
                print(f"  Fragment #{i}: Node(id={f.id}, left={left_id}, right={right_id})")
            else:
                print(f"  Fragment #{i}: {f}")
    else:
        print(f"  {fragments_input}")
    print("-" * 64)

    status = result.get("status", result.status) if hasattr(result, "get") else result.status
    reason = result.get("reason", result.reason) if hasattr(result, "get") else result.reason
    root = result.get("root", result.root) if hasattr(result, "get") else result.root
    inorder = result.get("inorder", result.inorder) if hasattr(result, "get") else result.inorder

    if status in ("OK", "SUCCESS") and root is not None:
        print(f"STATUS            : OK")
        print(f"Recovered Root ID : {root.id}")
        print(f"Inorder Traversal : {inorder}")
        print(f"Current Leaf IDs  : {collect_leaf_ids(root)}")
        print("\nRecovered BST Structure:")
        print(format_tree(root))
    else:
        print("STATUS            : IMPOSSIBLE")
        print(f"Reason            : {reason}")
    print("=" * 64)


def run_demo_illustrative():
    """Preset 1: Illustrative Valid Merge [2,1], [3,2,5], [5,4] -> inorder [1,2,3,4,5]."""
    print("\n>>> Preset 1: Illustrative Valid Merge")
    raw = [[2, 1], [3, 2, 5], [5, 4]]
    fragments = parse_fragments(raw)
    result = recover_student_index(fragments)
    display_result(result, raw)


def run_demo_unseen_valid():
    """Preset 2: Unseen Valid Merge (Multi-level balanced student index hierarchy)."""
    print("\n>>> Preset 2: Unseen Valid Multi-Fragment Merge")
    raw = [
        [50, 25, 75],
        [25, 15, 35],
        [75, 60, 90],
        [15, 10, 20],
        [35],
        [60],
        [90],
    ]
    fragments = parse_fragments(raw)
    result = recover_student_index(fragments)
    display_result(result, raw)


def run_demo_conflict():
    """Preset 3: BST Ordering Conflict (Global ancestor bound violation)."""
    print("\n>>> Preset 3: BST Ordering Conflict (Ancestor Bound Violation)")
    # [2, 1, 6] is locally valid (1 < 2 < 6), but 6 violates global upper bound of root 5
    raw = [[5, 2, 8], [2, 1, 6]]
    fragments = parse_fragments(raw)
    result = recover_student_index(fragments)
    display_result(result, raw)


def run_demo_disconnected():
    """Preset 4: Unused / Disconnected Fragments."""
    print("\n>>> Preset 4: Disconnected / Unused Fragments")
    # Multiple independent disjoint components that cannot attach
    raw = [[3, 2, 5], [10, 8, 12]]
    fragments = parse_fragments(raw)
    result = recover_student_index(fragments)
    display_result(result, raw)


def handle_custom_input():
    """Accepts and processes user-defined fragment inputs."""
    user_input = input("\nEnter fragments (e.g., [[2,1], [3,2,5], [5,4]]): ").strip()
    if not user_input:
        print("Input cannot be empty.")
        return
    try:
        parsed = parse_raw_fragments_string(user_input)
        fragments = parse_fragments(parsed)
        result = recover_student_index(fragments)
        display_result(result, parsed)
    except Exception as e:
        print(f"Error parsing or merging input: {e}")


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg in ("--demo", "-d"):
            run_demo_illustrative()
            return
        elif arg in ("--unseen", "-u"):
            run_demo_unseen_valid()
            return
        elif arg in ("--conflict", "-c"):
            run_demo_conflict()
            return
        elif arg in ("--disconnected", "-x"):
            run_demo_disconnected()
            return
        elif arg in ("--help", "-h"):
            print("Usage:")
            print("  python app.py                # Launch interactive menu")
            print("  python app.py --demo         # Run illustrative merge demo")
            print("  python app.py --unseen       # Run unseen valid merge demo")
            print("  python app.py --conflict     # Run ordering conflict demo")
            print("  python app.py --disconnected # Run disconnected fragments demo")
            print("  python app.py \"<fragments>\"  # Directly evaluate fragment string")
            return
        else:
            try:
                parsed = parse_raw_fragments_string(arg)
                fragments = parse_fragments(parsed)
                result = recover_student_index(fragments)
                display_result(result, parsed)
                return
            except Exception as e:
                print(f"Error parsing argument: {e}")
                return

    # Interactive menu loop
    while True:
        print("\n==============================================")
        print("   STUDENT INDEX RECOVERY SYSTEM (BST CLI)    ")
        print("==============================================")
        print("1. Illustrative Valid Merge ([2,1], [3,2,5], [5,4])")
        print("2. Unseen Valid Multi-Fragment Merge")
        print("3. BST Ordering Conflict Demo ([5,2,8], [2,1,6])")
        print("4. Disconnected / Unused Fragments Demo")
        print("5. Enter Custom Tree Fragments")
        print("6. Run Verification Test Suite")
        print("7. Exit")
        print("----------------------------------------------")
        choice = input("Enter choice (1-7): ").strip()

        if choice == "1":
            run_demo_illustrative()
        elif choice == "2":
            run_demo_unseen_valid()
        elif choice == "3":
            run_demo_conflict()
        elif choice == "4":
            run_demo_disconnected()
        elif choice == "5":
            handle_custom_input()
        elif choice == "6":
            import unittest
            import test_suite
            suite = unittest.TestLoader().loadTestsFromModule(test_suite)
            unittest.TextTestRunner(verbosity=2).run(suite)
        elif choice == "7":
            print("\nExiting Student Index Recovery System. Goodbye!")
            break
        else:
            print("Invalid selection. Please choose an option from 1 to 7.")


if __name__ == "__main__":
    main()
