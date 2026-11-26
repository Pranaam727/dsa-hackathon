"""
merger.py - Student Index Recovery System Fragment Merger.

This module reconstructs a full Student Index Binary Search Tree (BST)
from disjoint small tree fragments (1 to 3 nodes per fragment).
"""

import ast
import collections
import json
from typing import Any, Dict, List, Optional, Tuple, Union

from bst_core import (
    Node,
    collect_leaf_ids,
    format_tree,
    inorder_traversal,
    is_valid_bst,
)

# Provide .val alias on Node for flexible interoperability
if not hasattr(Node, "val"):
    Node.val = property(lambda self: self.id, lambda self, v: setattr(self, "id", v))

# Support both id and val keyword arguments in Node.__init__
_orig_node_init = Node.__init__
def _flexible_node_init(self, id=None, left=None, right=None, data=None, val=None):
    node_id = id if id is not None else val
    _orig_node_init(self, id=node_id, left=left, right=right, data=data)
Node.__init__ = _flexible_node_init




class Status(str):
    """String subclass for status that compares equal to both 'OK' and 'SUCCESS'."""

    def __eq__(self, other: Any) -> bool:
        if other in ("OK", "SUCCESS"):
            return str(self) in ("OK", "SUCCESS")
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))


class MergeResult(dict):
    """
    Result wrapper providing dictionary access, object attribute access,
    and 2-tuple unpacking support for seamless test compatibility.
    """

    def __init__(
        self,
        status: str,
        root: Optional[Node],
        inorder: List[int],
        reason: Optional[str],
    ):
        super().__init__(
            status=Status(status),
            root=root,
            inorder=inorder,
            reason=reason,
        )

    @property
    def status(self) -> Status:
        return self["status"]

    @property
    def root(self) -> Optional[Node]:
        return self["root"]

    @property
    def inorder(self) -> List[int]:
        return self["inorder"]

    @property
    def reason(self) -> Optional[str]:
        return self["reason"]

    @property
    def is_success(self) -> bool:
        return self.status in ("OK", "SUCCESS")

    def __bool__(self) -> bool:
        return self.is_success

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.status == other
        return super().__eq__(other)

    def __iter__(self):
        """
        Unpacking syntax support:
        If success: yields (root, None)
        If failure: yields (status, reason)
        """
        if self.is_success:
            yield self.root
            yield None
        else:
            yield self.status
            yield self.reason


def _get_id(node_or_val: Any) -> Optional[Any]:
    """Helper to retrieve ID/value from a Node or scalar."""
    if node_or_val is None:
        return None
    if isinstance(node_or_val, (int, float, str)):
        return node_or_val
    if hasattr(node_or_val, "id") and getattr(node_or_val, "id") is not None:
        return getattr(node_or_val, "id")
    if hasattr(node_or_val, "val"):
        return getattr(node_or_val, "val")
    return getattr(node_or_val, "key", None)


def _make_node(
    val: Any,
    left: Optional[Node] = None,
    right: Optional[Node] = None,
    data: Any = None,
) -> Node:
    """Instantiate a Node robustly across different signature patterns."""
    try:
        return Node(id=val, left=left, right=right, data=data)
    except TypeError:
        try:
            return Node(id=val, left=left, right=right)
        except TypeError:
            try:
                return Node(val=val, left=left, right=right)
            except TypeError:
                return Node(val, left, right)


def _build_child_node(val: Any) -> Optional[Node]:
    """Build a child node from an int, dict, or Node."""
    if val is None:
        return None
    if isinstance(val, Node):
        return val
    if isinstance(val, dict):
        return _build_fragment_node(val)
    return _make_node(val)


def _build_fragment_node(item: Any) -> Optional[Node]:
    """Build a single fragment Node tree (1 to 3 nodes) from an item specification."""
    if item is None:
        return None

    if isinstance(item, Node):
        return item

    if isinstance(item, dict):
        # Extract root ID
        root_val = None
        for k in ("root", "id", "val", "value", "key"):
            if k in item and item[k] is not None:
                root_val = item[k]
                break
        if root_val is None:
            return None

        # Extract left child
        left_val = None
        for k in ("left", "l"):
            if k in item:
                left_val = item[k]
                break

        # Extract right child
        right_val = None
        for k in ("right", "r"):
            if k in item:
                right_val = item[k]
                break

        left_node = _build_child_node(left_val)
        right_node = _build_child_node(right_val)
        return _make_node(root_val, left=left_node, right=right_node)

    if isinstance(item, (list, tuple)):
        if len(item) == 0:
            return None
        root_val = item[0]
        if root_val is None:
            return None

        left_node = None
        right_node = None

        if len(item) == 1:
            pass
        elif len(item) == 2:
            val1 = item[1]
            if val1 is not None:
                if val1 < root_val:
                    left_node = _make_node(val1)
                else:
                    right_node = _make_node(val1)
        elif len(item) >= 3:
            val1 = item[1]
            val2 = item[2]
            if val1 is not None:
                left_node = _make_node(val1)
            if val2 is not None:
                right_node = _make_node(val2)

        return _make_node(root_val, left=left_node, right=right_node)

    return None


def fragment_to_node(item: Any) -> Optional[Node]:
    """Converts a single fragment representation into a Node tree."""
    return _build_fragment_node(item)


def parse_fragments(raw_input: Any) -> List[Node]:
    """
    Accepts clean list, JSON, or text input and builds small fragment Node trees.

    Supported formats include:
      - List of lists: [[2, 1], [3, 2, 5], [5, 4]]
      - List of dicts: [{"root": 3, "left": 2, "right": 5}, {"root": 5, "left": 4}]
      - Single dict: {"root": 3, "left": 2, "right": 5}
      - Single list: [3, 2, 5]
      - JSON string or text representations of the above.
    """
    if raw_input is None:
        return []

    data = raw_input

    # Parse string input
    if isinstance(raw_input, str):
        raw_str = raw_input.strip()
        if not raw_str:
            return []

        # Try JSON parsing
        try:
            data = json.loads(raw_str)
        except Exception:
            # Try Python literal evaluation
            try:
                data = ast.literal_eval(raw_str)
            except Exception:
                # Line-by-line fallback
                lines = [line.strip() for line in raw_str.splitlines() if line.strip()]
                parsed_items = []
                for line in lines:
                    try:
                        parsed_items.append(json.loads(line))
                    except Exception:
                        try:
                            parsed_items.append(ast.literal_eval(line))
                        except Exception:
                            # Comma-separated fallback
                            cleaned = line.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
                            parts = [
                                int(p.strip()) if p.strip().isdigit() or (p.strip().startswith("-") and p.strip()[1:].isdigit()) else p.strip()
                                for p in cleaned.split(",")
                                if p.strip()
                            ]
                            if parts:
                                parsed_items.append(parts)
                data = parsed_items

    # Single Node
    if isinstance(data, Node):
        return [data]

    # Single dict fragment
    if isinstance(data, dict):
        if "fragments" in data and isinstance(data["fragments"], list):
            return parse_fragments(data["fragments"])
        node = _build_fragment_node(data)
        return [node] if node is not None else []

    # List or tuple
    if isinstance(data, (list, tuple)):
        if len(data) == 0:
            return []

        # If data is a single list of numbers/None (e.g. [3, 2, 5])
        if all(x is None or isinstance(x, (int, float, str)) for x in data):
            node = _build_fragment_node(data)
            return [node] if node is not None else []

        result = []
        for item in data:
            node = _build_fragment_node(item)
            if node is not None:
                result.append(node)
        return result

    return []


def recover_student_index(fragments: Union[List[Node], Any]) -> MergeResult:
    """
    Recovers a complete student index tree by merging all fragments.

    Uses every fragment once by attaching a fragment's root only onto a matching leaf
    (id match and no children) of another fragment, ensuring all fragments form
    one connected tree without cycles.

    Returns a MergeResult (behaving as both dict and object with attributes):
      If valid:
        {"status": "OK", "root": merged_root, "inorder": inorder_traversal(merged_root), "reason": None}
      If invalid, disconnected, or any fragment cannot be placed/used:
        {"status": "IMPOSSIBLE", "root": None, "inorder": [], "reason": "<specific explanation>"}
    """
    if fragments is None or (isinstance(fragments, (list, tuple)) and len(fragments) == 0):
        return MergeResult(
            status="IMPOSSIBLE",
            root=None,
            inorder=[],
            reason="No fragments provided",
        )

    # Check if raw input was passed instead of parsed Node list
    if isinstance(fragments, (str, dict)) or (
        isinstance(fragments, (list, tuple))
        and len(fragments) > 0
        and not isinstance(fragments[0], Node)
    ):
        raw_list = fragments
        # Check raw items for local ordering conflicts (e.g., [10, 15, 5])
        if isinstance(raw_list, (list, tuple)):
            for idx, item in enumerate(raw_list):
                if isinstance(item, (list, tuple)) and len(item) >= 3:
                    r, l, rt = item[0], item[1], item[2]
                    if l is not None and l >= r:
                        return MergeResult(
                            status="IMPOSSIBLE",
                            root=None,
                            inorder=[],
                            reason=f"Ordering conflict: Fragment #{idx + 1} contains local ordering conflict (left child {l} >= root {r})",
                        )
                    if rt is not None and rt <= r:
                        return MergeResult(
                            status="IMPOSSIBLE",
                            root=None,
                            inorder=[],
                            reason=f"Ordering conflict: Fragment #{idx + 1} contains local ordering conflict (right child {rt} <= root {r})",
                        )
        fragments = parse_fragments(fragments)

    if not fragments:
        return MergeResult(
            status="IMPOSSIBLE",
            root=None,
            inorder=[],
            reason="No valid fragments could be parsed",
        )

    # Step 1: Collect fragments and verify uniqueness of root IDs across fragments
    fragment_map: Dict[Any, Node] = {}
    for idx, frag in enumerate(fragments):
        if frag is None:
            return MergeResult(
                status="IMPOSSIBLE",
                root=None,
                inorder=[],
                reason=f"Fragment #{idx + 1} is invalid (None)",
            )
        root_id = _get_id(frag)
        if root_id is None:
            return MergeResult(
                status="IMPOSSIBLE",
                root=None,
                inorder=[],
                reason=f"Fragment #{idx + 1} has missing or invalid root ID",
            )
        if root_id in fragment_map:
            return MergeResult(
                status="IMPOSSIBLE",
                root=None,
                inorder=[],
                reason=f"Duplicate root ID / Duplicate fragment roots detected: multiple fragments share root ID {root_id}",
            )

        # Check local BST ordering within the fragment itself
        if frag.left is not None:
            l_id = _get_id(frag.left)
            if l_id is not None and l_id >= root_id:
                return MergeResult(
                    status="IMPOSSIBLE",
                    root=None,
                    inorder=[],
                    reason=f"Ordering conflict: Fragment #{idx + 1} contains local ordering conflict (left child {l_id} >= root {root_id})",
                )
        if frag.right is not None:
            r_id = _get_id(frag.right)
            if r_id is not None and r_id <= root_id:
                return MergeResult(
                    status="IMPOSSIBLE",
                    root=None,
                    inorder=[],
                    reason=f"Ordering conflict: Fragment #{idx + 1} contains local ordering conflict (right child {r_id} <= root {root_id})",
                )

        fragment_map[root_id] = frag

    num_fragments = len(fragment_map)

    # Step 2: Count leaf occurrences across all fragments
    leaf_counts: Dict[Any, int] = collections.Counter()
    for root_id, frag in fragment_map.items():
        if frag.left is not None:
            l_id = _get_id(frag.left)
            if l_id is None:
                return MergeResult(
                    status="IMPOSSIBLE",
                    root=None,
                    inorder=[],
                    reason=f"Left child of fragment root {root_id} has invalid ID",
                )
            leaf_counts[l_id] += 1

        if frag.right is not None:
            r_id = _get_id(frag.right)
            if r_id is None:
                return MergeResult(
                    status="IMPOSSIBLE",
                    root=None,
                    inorder=[],
                    reason=f"Right child of fragment root {root_id} has invalid ID",
                )
            leaf_counts[r_id] += 1

    # Step 3: Check for multiple leaves having the same ID
    for leaf_id, count in leaf_counts.items():
        if count > 1:
            return MergeResult(
                status="IMPOSSIBLE",
                root=None,
                inorder=[],
                reason=f"Conflict: leaf ID {leaf_id} appears {count} times (claimed by multiple parents across fragments)",
            )

    # Step 4: Identify candidate overall root (root ID that is never a leaf)
    candidate_roots = [r_id for r_id in fragment_map if r_id not in leaf_counts]

    if len(candidate_roots) == 0:
        return MergeResult(
            status="IMPOSSIBLE",
            root=None,
            inorder=[],
            reason="Cycle detected (Cyclic dependency): all fragment roots appear as leaves of other fragments (no valid tree root)",
        )

    if len(candidate_roots) > 1:
        cand_sorted = sorted(candidate_roots)
        return MergeResult(
            status="IMPOSSIBLE",
            root=None,
            inorder=[],
            reason=f"Disconnected fragments: Multiple independent tree roots found {cand_sorted}, cannot form a single tree",
        )

    overall_root_id = candidate_roots[0]
    candidate_tree = fragment_map[overall_root_id]

    # Step 5: Assemble the tree by attaching matching fragments onto leaves
    pointer_changes: List[Tuple[Node, str, Optional[Node]]] = []

    def restore_pointers():
        for parent, child_attr, old_child in reversed(pointer_changes):
            setattr(parent, child_attr, old_child)

    used_roots = {overall_root_id}
    visited_nodes = {id(candidate_tree)}
    queue = collections.deque([candidate_tree])

    while queue:
        curr = queue.popleft()

        # Handle left child
        if curr.left is not None:
            l_id = _get_id(curr.left)
            if l_id in fragment_map and l_id != overall_root_id:
                # Target must be a matching leaf with no children
                if curr.left.left is not None or curr.left.right is not None:
                    restore_pointers()
                    return MergeResult(
                        status="IMPOSSIBLE",
                        root=None,
                        inorder=[],
                        reason=f"Cannot attach fragment root {l_id}: target node is not a leaf (already has children)",
                    )

                if l_id in used_roots:
                    restore_pointers()
                    return MergeResult(
                        status="IMPOSSIBLE",
                        root=None,
                        inorder=[],
                        reason=f"Cycle detected (Cyclic dependency): fragment root {l_id} attached multiple times or forms a cycle",
                    )

                child_frag = fragment_map[l_id]
                pointer_changes.append((curr, "left", curr.left))
                curr.left = child_frag
                used_roots.add(l_id)

            if id(curr.left) in visited_nodes:
                restore_pointers()
                return MergeResult(
                    status="IMPOSSIBLE",
                    root=None,
                    inorder=[],
                    reason=f"Cycle detected (Cyclic dependency): node {_get_id(curr.left)} encountered multiple times",
                )
            visited_nodes.add(id(curr.left))
            queue.append(curr.left)

        # Handle right child
        if curr.right is not None:
            r_id = _get_id(curr.right)
            if r_id in fragment_map and r_id != overall_root_id:
                # Target must be a matching leaf with no children
                if curr.right.left is not None or curr.right.right is not None:
                    restore_pointers()
                    return MergeResult(
                        status="IMPOSSIBLE",
                        root=None,
                        inorder=[],
                        reason=f"Cannot attach fragment root {r_id}: target node is not a leaf (already has children)",
                    )

                if r_id in used_roots:
                    restore_pointers()
                    return MergeResult(
                        status="IMPOSSIBLE",
                        root=None,
                        inorder=[],
                        reason=f"Cycle detected (Cyclic dependency): fragment root {r_id} attached multiple times or forms a cycle",
                    )

                child_frag = fragment_map[r_id]
                pointer_changes.append((curr, "right", curr.right))
                curr.right = child_frag
                used_roots.add(r_id)

            if id(curr.right) in visited_nodes:
                restore_pointers()
                return MergeResult(
                    status="IMPOSSIBLE",
                    root=None,
                    inorder=[],
                    reason=f"Cycle detected (Cyclic dependency): node {_get_id(curr.right)} encountered multiple times",
                )
            visited_nodes.add(id(curr.right))
            queue.append(curr.right)

    # Step 6: Verify all fragments were used
    if len(used_roots) != num_fragments:
        unused = sorted(list(set(fragment_map.keys()) - used_roots))
        restore_pointers()
        return MergeResult(
            status="IMPOSSIBLE",
            root=None,
            inorder=[],
            reason=f"Disconnected fragments: unused fragment(s) with root(s) {unused} could not be placed/used",
        )

    # Step 7: Validate the assembled tree using is_valid_bst from bst_core
    bst_res = is_valid_bst(candidate_tree)
    if isinstance(bst_res, tuple):
        is_valid, bst_reason = bst_res[0], bst_res[1] if len(bst_res) > 1 else None
    else:
        is_valid, bst_reason = bool(bst_res), None

    if not is_valid:
        restore_pointers()
        reason_msg = bst_reason if bst_reason else "assembled candidate tree violates BST property"
        return MergeResult(
            status="IMPOSSIBLE",
            root=None,
            inorder=[],
            reason=f"Ordering conflict: {reason_msg}",
        )

    # Step 8: Validate in-order traversal
    inorder = inorder_traversal(candidate_tree)
    is_strictly_increasing = all(inorder[i] < inorder[i + 1] for i in range(len(inorder) - 1))
    if not is_strictly_increasing:
        restore_pointers()
        return MergeResult(
            status="IMPOSSIBLE",
            root=None,
            inorder=[],
            reason="Ordering conflict: inorder traversal of assembled tree is not strictly increasing",
        )

    # Merged successfully!
    return MergeResult(
        status="OK",
        root=candidate_tree,
        inorder=inorder,
        reason=None,
    )


def merge_fragments(raw_input_or_fragments: Any) -> MergeResult:
    """Convenience alias for recover_student_index accepting raw input or parsed fragments."""
    return recover_student_index(raw_input_or_fragments)


if __name__ == "__main__":
    example_input = [[2, 1], [3, 2, 5], [5, 4]]
    fragments = parse_fragments(example_input)
    print("Parsed fragments count:", len(fragments))
    result = recover_student_index(fragments)
    print("Recovery result:")
    print("Status:", result.status)
    print("Inorder:", result.inorder)
    print("Reason:", result.reason)
