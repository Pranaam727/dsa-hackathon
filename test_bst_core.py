"""
Unit tests for bst_core.py
"""

import unittest
from bst_core import (
    Node,
    collect_leaf_nodes,
    get_leaf_nodes,
    collect_leaf_ids,
    get_leaf_ids,
    collect_all_node_ids,
    get_all_node_ids,
    is_valid_bst,
    inorder_traversal,
    format_tree,
    insert_node,
    build_balanced_bst_from_sorted,
)


class TestBSTCore(unittest.TestCase):

    def setUp(self):
        # Create a sample valid BST:
        #        50
        #       /  \
        #      30   70
        #     /  \    \
        #    20  40    80
        self.n20 = Node(20)
        self.n40 = Node(40)
        self.n30 = Node(30, left=self.n20, right=self.n40)
        self.n80 = Node(80)
        self.n70 = Node(70, right=self.n80)
        self.root = Node(50, left=self.n30, right=self.n70)

    def test_node_creation_and_leaf_check(self):
        leaf = Node(101)
        self.assertEqual(leaf.id, 101)
        self.assertIsNone(leaf.left)
        self.assertIsNone(leaf.right)
        self.assertTrue(leaf.is_leaf())

        parent = Node(102, left=leaf)
        self.assertFalse(parent.is_leaf())

    def test_collect_leaves(self):
        leaves = collect_leaf_nodes(self.root)
        leaf_ids = [n.id for n in leaves]
        self.assertEqual(leaf_ids, [20, 40, 80])
        self.assertEqual(get_leaf_ids(self.root), [20, 40, 80])

        # Test empty tree
        self.assertEqual(collect_leaf_nodes(None), [])
        self.assertEqual(get_leaf_ids(None), [])

        # Single node tree
        single = Node(10)
        self.assertEqual(get_leaf_ids(single), [10])

    def test_inorder_and_collect_all_ids(self):
        expected_ids = [20, 30, 40, 50, 70, 80]
        self.assertEqual(inorder_traversal(self.root), expected_ids)
        self.assertEqual(collect_all_node_ids(self.root), expected_ids)
        self.assertEqual(get_all_node_ids(self.root), expected_ids)
        self.assertEqual(inorder_traversal(None), [])

    def test_is_valid_bst_success(self):
        valid, reason = is_valid_bst(self.root)
        self.assertTrue(valid)
        self.assertIsNone(reason)

        # Empty tree is valid
        valid_empty, reason_empty = is_valid_bst(None)
        self.assertTrue(valid_empty)
        self.assertIsNone(reason_empty)

    def test_is_valid_bst_local_violation(self):
        # Left child larger than parent
        invalid_tree = Node(50, left=Node(60))
        valid, reason = is_valid_bst(invalid_tree)
        self.assertFalse(valid)
        self.assertIsNotNone(reason)
        self.assertIn("60", reason)

    def test_is_valid_bst_global_violation(self):
        # Local property holds (25 < 60), but global property violated (60 > 50 in left subtree):
        #        50
        #       /
        #      25
        #        \
        #         60
        invalid_tree = Node(50, left=Node(25, right=Node(60)))
        valid, reason = is_valid_bst(invalid_tree)
        self.assertFalse(valid)
        self.assertIsNotNone(reason)
        self.assertIn("60", reason)

    def test_is_valid_bst_duplicate_violation(self):
        # BST requires strict inequality (min_val < node.id < max_val)
        duplicate_tree = Node(50, left=Node(50))
        valid, reason = is_valid_bst(duplicate_tree)
        self.assertFalse(valid)
        self.assertIsNotNone(reason)
        self.assertIn("50", reason)

    def test_format_tree(self):
        output = format_tree(self.root)
        self.assertIn("Root ID: 50", output)
        self.assertIn("ID: 20", output)
        self.assertIn("ID: 70", output)
        self.assertIn("(leaf)", output)

        empty_output = format_tree(None)
        self.assertIn("Root ID: None", empty_output)
        self.assertIn("Empty Tree", empty_output)

    def test_balanced_builder_and_insert(self):
        ids = [10, 20, 30, 40, 50, 60, 70]
        balanced = build_balanced_bst_from_sorted(ids)
        self.assertEqual(inorder_traversal(balanced), ids)
        valid, _ = is_valid_bst(balanced)
        self.assertTrue(valid)

        # Insert new ID
        inserted = insert_node(balanced, 25)
        self.assertEqual(inorder_traversal(inserted), [10, 20, 25, 30, 40, 50, 60, 70])
        valid, _ = is_valid_bst(inserted)
        self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()
