# Student Index Recovery System (BST Reconstruction)

An algorithmic framework designed to recover corrupted student index records by merging fragmented Binary Search Tree (BST) subtrees into a single, strictly valid, unified BST.

---

## 1. System Overview & Architecture

When student index records are split into disjoint small tree fragments (1-node, 2-node, or 3-node subtrees), this system reconstructs the entire tree hierarchy or proves that recovery is `IMPOSSIBLE` due to ordering or structural violations.

```
                  Input Fragments:
     [2, 1]          [3, 2, 5]          [5, 4]
       2                 3                 5
      /                 / \               /
     1                 2   5             4
                       │   │
                       └───┴── Grafting onto Leaves
                                │
                                ▼
                       Unified BST Root: 3
                                3
                              /   \
                             2     5
                            /     /
                           1     4
             Inorder Traversal: [1, 2, 3, 4, 5]
```

### Module Structure

| File | Module Name | Responsibilities | Key Functions |
| :--- | :--- | :--- | :--- |
| `bst_core.py` | Core Data Structure | Node class, strict global BST validation, traversal, leaf helpers, and visual ASCII formatter. | `Node`, `is_valid_bst`, `inorder_traversal`, `collect_leaf_ids`, `format_tree` |
| `merger.py` | Recovery Engine | Parses fragment representations and stitches them into a unified BST. | `parse_fragments`, `recover_student_index`, `merge_fragments` |
| `app.py` | CLI & UI Runner | Interactive menu and preset demos (illustrative, unseen, ordering conflicts, disconnected fragments). | `main`, `display_result`, `run_demo_*` |
| `test_suite.py` | Verification Suite | Unit tests verifying all valid merges, edge cases, and failure modes. | `TestStudentIndexRecovery` |

### Recovery Result Contract

`recover_student_index(fragments)` returns a `MergeResult` dictionary object adhering to:

- **On Success**:
  ```python
  {
      "status": "OK",
      "root": <Node object>,
      "inorder": [1, 2, 3, 4, 5],
      "reason": None
  }
  ```
- **On Failure / Conflict**:
  ```python
  {
      "status": "IMPOSSIBLE",
      "root": None,
      "inorder": [],
      "reason": "<Detailed diagnostic message>"
  }
  ```

---

## 2. Setup & Requirements

- **Python Version**: Python 3.8+
- **External Dependencies**: None (Standard Library only: `typing`, `unittest`, `ast`, `json`, `collections`).

```bash
python --version
```

---

## 3. How to Run

### Running the Test Suite
Execute the full test suite verifying illustrative merges, ancestor bound conflicts, and disconnected components:
```bash
python -m unittest test_suite.py -v
```

### Running the Application (`app.py`)
Launch the interactive terminal interface:
```bash
python app.py
```

Or run dedicated CLI presets:
```bash
# 1. Preset 1: Illustrative valid merge ([2,1], [3,2,5], [5,4])
python app.py --demo

# 2. Preset 2: Unseen valid multi-fragment merge
python app.py --unseen

# 3. Preset 3: BST ordering conflict (ancestor bound violation)
python app.py --conflict

# 4. Preset 4: Disconnected / unused fragments demo
python app.py --disconnected

# 5. Evaluate custom fragment string directly
python app.py "[[2, 1], [3, 2, 5], [5, 4]]"
```

---

## 4. Team Member Module Ownership

| Member | Module | Files | Deliverables & Responsibilities |
| :--- | :--- | :--- | :--- |
| **Member 1** | **Core Tree Structures & Invariants** | `bst_core.py` | Scratch-built `Node` class, leaf & ID collectors (`collect_leaf_nodes`), global BST bounds validation (`is_valid_bst`), tree traversal (`inorder_traversal`), and ASCII visualizer (`format_tree`). |
| **Member 2** | **Merge Engine & Algorithm** | `merger.py` | Robust fragment parsing (`parse_fragments`), candidate root identification, leaf-to-root grafting, cycle detection, component connectivity, and result encapsulation (`recover_student_index`). |
| **Member 3** | **Integration, CLI & Test Suite** | `app.py`, `test_suite.py`, `README.md` | Interactive CLI application with presets and custom input, end-to-end unit test suite covering valid and invalid bounds, documentation, and evaluation guides. |

---

## 5. Evaluation Guide & Talking Points

Use these explanations during project defense, lab exams, or code walkthroughs:

### Member 1: Core Tree Structures & Validation (`bst_core.py`)
- **"Why is a local check (`left < root < right`) insufficient for BST validation?"**
  - *Answer*: "Local checks only inspect immediate parent-child relationships and fail to detect ancestor bound violations. A node in a left subtree must be less than *all* of its ancestors. In `is_valid_bst(root, min_val, max_val)`, we pass down strict bounds $(-\infty, +\infty)$ and narrow them recursively: the left subtree must fall strictly within `(min_val, root.id)` and the right subtree within `(root.id, max_val)`. This guarantees strict global ordering in $O(N)$ time."
- **"How does `format_tree` render branch directions clearly?"**
  - *Answer*: "It inspects each node's children and labels them with `[L]` and `[R]` directional tags along with `(leaf)` markers, eliminating ambiguity when a node has only a single child."

### Member 2: Fragment Merging Algorithm (`merger.py`)
- **"How is the overall root identified among multiple fragments?"**
  - *Answer*: "We construct a parent-child dependency graph. Fragments attached to leaves have in-degree 1 (their root ID matches an existing leaf). The overall tree root is the unique fragment whose root ID has in-degree 0 (never appears as a child in any other fragment). If 0 candidates exist, there is a cycle; if $>1$ candidates exist, the fragments are disconnected."
- **"Why can a fragment root only attach to a leaf node?"**
  - *Answer*: "If a fragment root $X$ were attached to an internal node $X$ that already possessed children, node $X$ would exceed the binary tree limit or overwrite existing branches, corrupting the index."

### Member 3: System Integration & Verification (`app.py`, `test_suite.py`)
- **"What edge cases does `test_suite.py` verify?"**
  - *Answer*:
    1. **Illustrative Valid Merge**: Merges `[2,1], [3,2,5], [5,4]` into root 3 with inorder `[1,2,3,4,5]`.
    2. **Multi-Fragment Trees**: Merges chains and balanced trees with 1-node, 2-node, and 3-node fragments.
    3. **Ancestor Inversions**: Where a subtree like `[2, 1, 6]` is locally valid, but its right child 6 violates the ancestor bound $< 5$ when merged under root 5.
    4. **Structural Conflicts**: Disconnected fragments, unattachable fragments, duplicate roots, and cyclic loops returning `IMPOSSIBLE` with exact diagnostic error reasons.
- **"How does `app.py` ensure robust user interactions?"**
  - *Answer*: "It provides a menu with presets for all key scenarios, parses user inputs safely via `ast.literal_eval` and `parse_fragments`, and outputs detailed trees via `format_tree`."
