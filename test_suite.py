"""
test_suite.py - Verification Test Suite
Student Index Recovery System

Verifies:
1. Illustrative valid merge ([2,1], [3,2,5], [5,4]) producing root 3 and inorder [1,2,3,4,5].
2. Additional valid multi-fragment merges (1-node, 2-node, and 3-node fragments, up to moderate counts).
3. Ordering conflicts (local violations and global ancestor bound violations) returning IMPOSSIBLE with clear reasons.
4. Unused or disconnected fragments returning IMPOSSIBLE with clear reasons.
5. Consistent dictionary and attribute return shapes across recover_student_index.
"""

import unittest
from bst_core import Node, inorder_traversal, format_tree, is_valid_bst, collect_leaf_ids
from merger import parse_fragments, recover_student_index, merge_fragments, MergeResult


class TestStudentIndexRecovery(unittest.TestCase):

    # ========================================================================
    # 1. Illustrative Valid Merge
    # ========================================================================
    def test_01_illustrative_valid_merge(self):
        """
        Verify: [2,1], [3,2,5], [5,4]
        Produces merged tree with root ID 3 and inorder traversal [1, 2, 3, 4, 5].
        """
        raw_fragments = [[2, 1], [3, 2, 5], [5, 4]]
        parsed_fragments = parse_fragments(raw_fragments)
        result = recover_student_index(parsed_fragments)

        # Dictionary shape & attribute verification
        self.assertIn(result["status"], ("OK", "SUCCESS"))
        self.assertEqual(result.status, "OK")
        self.assertTrue(result.is_success)
        self.assertIsNotNone(result["root"])
        self.assertIsNone(result["reason"])

        # Root verification
        self.assertEqual(result["root"].id, 3)
        self.assertEqual(result.root.id, 3)

        # Inorder traversal verification
        self.assertEqual(result["inorder"], [1, 2, 3, 4, 5])
        self.assertEqual(result.inorder, [1, 2, 3, 4, 5])
        self.assertEqual(inorder_traversal(result.root), [1, 2, 3, 4, 5])

        # Global BST validation check
        is_valid, reason = is_valid_bst(result.root)
        self.assertTrue(is_valid)
        self.assertIsNone(reason)

        # Current leaf IDs check
        self.assertEqual(collect_leaf_ids(result.root), [1, 4])

        # Test merge_fragments alias equivalence
        alias_result = merge_fragments(raw_fragments)
        self.assertEqual(alias_result.status, "OK")
        self.assertEqual(alias_result.root.id, 3)

    # ========================================================================
    # 2. Additional Valid Multi-Fragment Merges
    # ========================================================================
    def test_02_single_node_fragment_merge(self):
        """Test merge involving 1-node fragments attaching to leaves."""
        raw = [
            [20, 10, 30],
            [10, 5],       # 2-node
            [30, 40],      # 2-node
            [5],           # 1-node
        ]
        fragments = parse_fragments(raw)
        result = recover_student_index(fragments)
        self.assertTrue(result.is_success)
        self.assertEqual(result.root.id, 20)
        self.assertEqual(result.inorder, [5, 10, 20, 30, 40])

    def test_03_moderate_count_multi_fragment_merge(self):
        r"""
        Test a 7-fragment merge representing a complete recovery of student indexes:
        Tree structure:
                    50
                 /      \
               25        75
              /  \      /  \
            15    35   65   85
           /  \
          10  18
        """
        raw = [
            [50, 25, 75],     # Root fragment
            [25, 15, 35],     # Left child of 50
            [75, 65, 85],     # Right child of 50
            [15, 10, 18],     # Left child of 25
            [35],             # 1-node leaf
            [65],             # 1-node leaf
            [85],             # 1-node leaf
        ]
        fragments = parse_fragments(raw)
        result = recover_student_index(fragments)
        self.assertTrue(result.is_success)
        self.assertEqual(result.root.id, 50)
        expected_inorder = [10, 15, 18, 25, 35, 50, 65, 75, 85]
        self.assertEqual(result.inorder, expected_inorder)

        # Unpacking syntax support verification
        root, err = result
        self.assertEqual(root.id, 50)
        self.assertIsNone(err)

    def test_04_chain_growth_merge(self):
        """Test deep linear chain growth of fragments."""
        raw = [
            [10, 8],
            [8, 6],
            [6, 4],
            [4, 2],
        ]
        fragments = parse_fragments(raw)
        result = recover_student_index(fragments)
        self.assertTrue(result.is_success)
        self.assertEqual(result.root.id, 10)
        self.assertEqual(result.inorder, [2, 4, 6, 8, 10])

    # ========================================================================
    # 3. Ordering Conflicts (Local & Global Ancestor Bounds)
    # ========================================================================
    def test_05_global_ancestor_bound_conflict(self):
        """
        Subtree [2, 1, 6] is locally valid (1 < 2 < 6),
        but attaching to leaf 2 of [5, 2, 8] violates ancestor bound (6 > 5 in left subtree).
        Must return IMPOSSIBLE with a clear reason.
        """
        raw = [
            [5, 2, 8],
            [2, 1, 6],  # Locally valid BST, but 6 violates global upper bound of 5!
        ]
        fragments = parse_fragments(raw)
        result = recover_student_index(fragments)
        self.assertEqual(result["status"], "IMPOSSIBLE")
        self.assertEqual(result.status, "IMPOSSIBLE")
        self.assertIsNone(result["root"])
        self.assertEqual(result["inorder"], [])
        self.assertFalse(result.is_success)
        self.assertIn("ordering conflict", result["reason"].lower())
        self.assertIn("6", result["reason"])

        # Verify tuple unpacking behavior on failure
        status, reason = result
        self.assertEqual(status, "IMPOSSIBLE")
        self.assertIn("6", reason)

    def test_06_local_ordering_conflict_in_fragment(self):
        """Fragment contains direct local BST inversion (left >= root or right <= root)."""
        raw = [[10, 15, 5]]  # Left child 15 >= root 10
        result = recover_student_index(raw)
        self.assertEqual(result["status"], "IMPOSSIBLE")
        self.assertIn("ordering conflict", result["reason"].lower())

    def test_07_duplicate_key_conflict_across_fragments(self):
        """Multiple fragments introduce duplicate keys, violating strict BST ordering or tree properties."""
        # Case A: Duplicate child ID claimed by two different parent fragments
        raw_multi_parent = [
            [50, 20, 80],
            [20, 10, 30],
            [80, 30, 90],  # 30 is claimed as child of both 20 and 80
        ]
        result_a = recover_student_index(raw_multi_parent)
        self.assertEqual(result_a["status"], "IMPOSSIBLE")
        self.assertIn("conflict", result_a["reason"].lower())

        # Case B: Duplicate root ID across fragments
        raw_dup_root = [
            [50, 20, 70],
            [50, 10, 60],
        ]
        result_b = recover_student_index(raw_dup_root)
        self.assertEqual(result_b["status"], "IMPOSSIBLE")
        self.assertIn("duplicate", result_b["reason"].lower())

    # ========================================================================
    # 4. Unused or Disconnected Fragments
    # ========================================================================
    def test_08_disconnected_separate_components(self):
        """Two disjoint trees that do not share any attachment points."""
        raw = [
            [3, 2, 5],
            [10, 8, 12],
        ]
        result = recover_student_index(raw)
        self.assertEqual(result["status"], "IMPOSSIBLE")
        self.assertIn("disconnected", result["reason"].lower())
        self.assertIn("multiple independent tree roots", result["reason"].lower())

    def test_09_unused_fragment_cannot_attach_to_leaf(self):
        """
        Fragment tries to attach to an ID that is NOT a leaf,
        or fragment root does not match any leaf.
        """
        raw = [
            [10, 5, 15],
            [5, 2],
            [99, 90],  # Root 99 is nowhere in the tree
        ]
        result = recover_student_index(raw)
        self.assertEqual(result["status"], "IMPOSSIBLE")
        self.assertIn("disconnected", result["reason"].lower())
        self.assertIn("99", result["reason"])

    def test_10_cyclic_fragment_dependencies(self):
        """Fragments forming a cycle where no root candidate has in-degree 0."""
        raw = [
            [5, 2],
            [2, 5],
        ]
        result = recover_student_index(raw)
        self.assertEqual(result["status"], "IMPOSSIBLE")
        self.assertIn("cycle", result["reason"].lower())

    def test_11_format_tree_visualization(self):
        """Verify format_tree produces clear ASCII hierarchy with Root ID."""
        raw = [[2, 1], [3, 2, 5], [5, 4]]
        result = recover_student_index(parse_fragments(raw))
        self.assertTrue(result.is_success)
        formatted = format_tree(result.root)
        self.assertIn("Root ID: 3", formatted)
        self.assertIn("ID: 3", formatted)
        self.assertIn("ID: 1 (leaf)", formatted)
        self.assertIn("ID: 4 (leaf)", formatted)


if __name__ == "__main__":
    unittest.main(verbosity=2)
