"""
web_ui.py - Interactive Web Interface for Student Index Recovery System
Zero external dependencies (pure Python standard library: http.server, json, webbrowser, threading).
"""

import sys
import os
import json
import socket
import threading
import webbrowser
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from bst_core import Node, inorder_traversal, format_tree, collect_leaf_ids, is_valid_bst
from merger import parse_fragments, recover_student_index, fragment_to_node


HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Index Recovery System | BST Stitcher</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #0a0f1d;
            --bg-surface: #11182c;
            --bg-card: #17223b;
            --bg-card-hover: #1d2b4b;
            --border: #233354;
            --border-focus: #3b82f6;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            --accent-blue: #3b82f6;
            --accent-indigo: #6366f1;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-amber: #f59e0b;
            --accent-purple: #a855f7;
            --glow-green: rgba(16, 185, 129, 0.25);
            --glow-red: rgba(239, 68, 68, 0.25);
            --glow-blue: rgba(59, 130, 246, 0.25);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        header {
            background: linear-gradient(180deg, #131c33 0%, var(--bg-surface) 100%);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 50;
            backdrop-filter: blur(12px);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }

        .brand-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-indigo));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.25rem;
            color: white;
            box-shadow: 0 4px 14px var(--glow-blue);
        }

        .brand h1 {
            font-size: 1.2rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .brand span {
            font-size: 0.8rem;
            color: var(--text-muted);
            font-weight: 500;
            display: block;
        }

        .header-actions {
            display: flex;
            gap: 0.75rem;
            align-items: center;
        }

        .btn {
            padding: 0.55rem 1.1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            text-decoration: none;
            font-family: inherit;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-indigo));
            color: white;
            box-shadow: 0 4px 12px var(--glow-blue);
        }

        .btn-primary:hover {
            opacity: 0.92;
            transform: translateY(-1px);
        }

        .btn-test {
            background: var(--bg-card);
            color: var(--text-main);
            border-color: var(--border);
        }

        .btn-test:hover {
            background: var(--bg-card-hover);
            border-color: var(--text-muted);
        }

        main {
            flex: 1;
            max-width: 1560px;
            margin: 0 auto;
            width: 100%;
            padding: 1.5rem 2rem 2.5rem;
            display: grid;
            grid-template-columns: 460px 1fr;
            gap: 1.5rem;
        }

        @media (max-width: 1100px) {
            main {
                grid-template-columns: 1fr;
            }
        }

        /* Preset Toolbar */
        .preset-section {
            grid-column: 1 / -1;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem 1.25rem;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.75rem;
        }

        .preset-label {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-right: 0.25rem;
        }

        .preset-chip {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 0.45rem 0.9rem;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }

        .preset-chip:hover {
            border-color: var(--border-focus);
            background: var(--bg-card-hover);
            transform: translateY(-1px);
        }

        .preset-chip.active {
            background: rgba(59, 130, 246, 0.15);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }

        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        .dot-green { background: var(--accent-green); box-shadow: 0 0 8px var(--glow-green); }
        .dot-blue { background: var(--accent-blue); box-shadow: 0 0 8px var(--glow-blue); }
        .dot-red { background: var(--accent-red); box-shadow: 0 0 8px var(--glow-red); }
        .dot-amber { background: var(--accent-amber); }

        /* Left Column: Input Panel */
        .left-col {
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .panel {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .panel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .panel-title {
            font-size: 0.95rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .badge-count {
            background: var(--bg-card);
            color: var(--text-muted);
            font-size: 0.75rem;
            padding: 0.15rem 0.5rem;
            border-radius: 6px;
            border: 1px solid var(--border);
        }

        textarea {
            width: 100%;
            height: 140px;
            background: var(--bg-base);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.85rem;
            color: var(--text-main);
            font-family: 'Fira Code', monospace;
            font-size: 0.86rem;
            resize: vertical;
            line-height: 1.5;
            transition: border-color 0.2s ease;
        }

        textarea:focus {
            outline: none;
            border-color: var(--border-focus);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
        }

        .input-hint {
            font-size: 0.75rem;
            color: var(--text-dim);
            line-height: 1.4;
        }

        /* Fragment Visual Cards */
        .fragment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
            gap: 0.75rem;
            max-height: 280px;
            overflow-y: auto;
            padding-right: 0.25rem;
        }

        .fragment-grid::-webkit-scrollbar {
            width: 6px;
        }
        .fragment-grid::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }

        .frag-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.65rem 0.75rem;
            font-family: 'Fira Code', monospace;
            font-size: 0.8rem;
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            position: relative;
            transition: all 0.2s ease;
        }

        .frag-card:hover {
            border-color: var(--border-focus);
            transform: translateY(-1px);
        }

        .frag-card-header {
            font-size: 0.7rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
        }

        .frag-root {
            font-weight: 700;
            color: var(--accent-blue);
            font-size: 0.95rem;
        }

        .frag-children {
            display: flex;
            justify-content: space-between;
            font-size: 0.72rem;
            color: var(--text-dim);
            border-top: 1px dashed var(--border);
            padding-top: 0.35rem;
        }

        /* Right Column: Visualization & Results */
        .right-col {
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        /* Status Banner */
        .status-banner {
            padding: 1.1rem 1.4rem;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid transparent;
            transition: all 0.3s ease;
        }

        .status-banner.ok {
            background: rgba(16, 185, 129, 0.1);
            border-color: rgba(16, 185, 129, 0.35);
        }

        .status-banner.impossible {
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.35);
        }

        .status-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .status-pill {
            padding: 0.45rem 1rem;
            border-radius: 9999px;
            font-weight: 800;
            font-size: 0.9rem;
            letter-spacing: 0.05em;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }

        .status-banner.ok .status-pill {
            background: var(--accent-green);
            color: #064e3b;
        }

        .status-banner.impossible .status-pill {
            background: var(--accent-red);
            color: white;
        }

        .status-meta {
            font-size: 0.9rem;
            font-weight: 600;
        }

        .status-banner.impossible .status-meta {
            color: #fca5a5;
            font-size: 0.85rem;
            line-height: 1.4;
        }

        /* Traversal Section */
        .inorder-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: center;
            font-family: 'Fira Code', monospace;
        }

        .inorder-pill {
            background: var(--bg-base);
            border: 1px solid var(--border);
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-size: 0.85rem;
            color: var(--accent-blue);
            font-weight: 600;
        }

        .inorder-arrow {
            color: var(--text-dim);
            font-size: 0.75rem;
        }

        /* SVG BST Canvas */
        .canvas-card {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            flex: 1;
            min-height: 480px;
            position: relative;
        }

        .canvas-toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .svg-container {
            flex: 1;
            background: radial-gradient(circle at center, #131c33 0%, var(--bg-base) 100%);
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: auto;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 380px;
            position: relative;
        }

        svg {
            display: block;
            margin: auto;
        }

        .node-circle {
            fill: #1e293b;
            stroke: var(--accent-blue);
            stroke-width: 2.5;
            transition: all 0.3s ease;
        }

        .node-circle.root-node {
            stroke: var(--accent-indigo);
            fill: #1e1b4b;
            stroke-width: 3.5;
        }

        .node-circle.leaf-node {
            stroke: var(--accent-green);
        }

        .node-circle.violating-node {
            stroke: var(--accent-red);
            fill: #450a0a;
            stroke-width: 3.5;
            animation: pulse-red 1.8s infinite;
        }

        @keyframes pulse-red {
            0% { filter: drop-shadow(0 0 2px var(--accent-red)); }
            50% { filter: drop-shadow(0 0 10px var(--accent-red)); }
            100% { filter: drop-shadow(0 0 2px var(--accent-red)); }
        }

        .node-text {
            fill: #f8fafc;
            font-family: 'Fira Code', monospace;
            font-size: 13px;
            font-weight: 700;
            text-anchor: middle;
            dominant-baseline: central;
            pointer-events: none;
        }

        .edge-line {
            stroke: #334155;
            stroke-width: 2;
            stroke-linecap: round;
        }

        .edge-label {
            fill: var(--text-dim);
            font-family: 'Fira Code', monospace;
            font-size: 10px;
            font-weight: 600;
            text-anchor: middle;
        }

        .empty-state {
            color: var(--text-dim);
            font-size: 0.95rem;
            text-align: center;
            padding: 3rem 1rem;
        }

        /* ASCII Accordion */
        details {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.65rem 1rem;
        }

        summary {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            cursor: pointer;
            user-select: none;
        }

        pre.ascii-box {
            margin-top: 0.75rem;
            background: var(--bg-base);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.75rem 1rem;
            font-family: 'Fira Code', monospace;
            font-size: 0.8rem;
            color: #93c5fd;
            overflow-x: auto;
            white-space: pre-wrap;
        }

        /* Test Modal */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 100;
            backdrop-filter: blur(4px);
        }

        .modal-overlay.active {
            display: flex;
        }

        .modal-box {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            width: 90%;
            max-width: 720px;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }

        .modal-header {
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .modal-body {
            padding: 1.25rem 1.5rem;
            overflow-y: auto;
            flex: 1;
        }

        .test-output {
            background: var(--bg-base);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            font-family: 'Fira Code', monospace;
            font-size: 0.82rem;
            color: #a7f3d0;
            white-space: pre-wrap;
            line-height: 1.5;
        }
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="brand-icon">BST</div>
            <div>
                <h1>Student Index Recovery System</h1>
                <span>Binary Search Tree Fragment Reconstructor &amp; Invariant Validator</span>
            </div>
        </div>
        <div class="header-actions">
            <button class="btn btn-test" onclick="runBackendTests()">
                <span style="font-size: 1rem;">&#9654;</span> Run Test Suite
            </button>
            <a class="btn btn-primary" href="#custom" onclick="document.getElementById('frag-input').focus()">
                + New Merge
            </a>
        </div>
    </header>

    <main>
        <!-- One-Click Viva Presets -->
        <div class="preset-section">
            <span class="preset-label">Viva Presets:</span>
            <button class="preset-chip active" onclick="loadPreset(1)">
                <span class="dot dot-green"></span> 1. Illustrative Valid Merge [1..5]
            </button>
            <button class="preset-chip" onclick="loadPreset(2)">
                <span class="dot dot-blue"></span> 2. Unseen Valid (7 Nodes)
            </button>
            <button class="preset-chip" onclick="loadPreset(3)">
                <span class="dot dot-red"></span> 3. Ordering Conflict (Ancestor Bound)
            </button>
            <button class="preset-chip" onclick="loadPreset(4)">
                <span class="dot dot-amber"></span> 4. Disconnected / Unused
            </button>
        </div>

        <!-- Left Column: Input and Fragment Cards -->
        <div class="left-col">
            <div class="panel" id="custom">
                <div class="panel-header">
                    <div class="panel-title">
                        <span>Fragment Input</span>
                        <span class="badge-count" id="frag-count-badge">3 fragments</span>
                    </div>
                    <button class="btn btn-primary" style="padding: 0.4rem 0.85rem; font-size: 0.8rem;" onclick="submitRecovery()">
                        Recover Tree
                    </button>
                </div>
                <textarea id="frag-input" placeholder="Enter fragments, e.g.:&#10;[[2, 1], [3, 2, 5], [5, 4]]">[[2, 1], [3, 2, 5], [5, 4]]</textarea>
                <div class="input-hint">
                    Accepts list of lists <code>[[root, left, right], ...]</code> or line-by-line fragments. 1, 2, or 3 node mini-trees supported.
                </div>
            </div>

            <!-- Mini-tree visual cards -->
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">Input Fragment Cards</div>
                    <span style="font-size: 0.75rem; color: var(--text-dim);">Pre-stitch state</span>
                </div>
                <div class="fragment-grid" id="fragment-grid">
                    <!-- Populated by JS -->
                </div>
            </div>

            <!-- ASCII format_tree view -->
            <details>
                <summary>Terminal ASCII Representation (format_tree)</summary>
                <pre class="ascii-box" id="ascii-output">(No tree rendered yet)</pre>
            </details>
        </div>

        <!-- Right Column: Visual Diagram & Diagnostics -->
        <div class="right-col">
            <!-- Status Result Banner -->
            <div class="status-banner ok" id="status-banner">
                <div class="status-left">
                    <div class="status-pill" id="status-pill">STATUS: OK</div>
                    <div>
                        <div class="status-meta" id="status-meta">Root ID: 3 | Inorder: [1, 2, 3, 4, 5]</div>
                        <div style="font-size: 0.75rem; color: var(--text-dim);" id="status-sub">All leaf attachments valid &amp; global BST invariants strictly satisfied.</div>
                    </div>
                </div>
            </div>

            <!-- Traversal Output Section -->
            <div class="panel" style="padding: 1rem 1.25rem;">
                <div class="panel-header" style="margin-bottom: 0.5rem;">
                    <span class="panel-title" style="font-size: 0.85rem;">Inorder Student Index Traversal (Ascending Order)</span>
                    <span id="leaf-list-badge" style="font-size: 0.75rem; color: var(--text-muted);">Leaves: [1, 4]</span>
                </div>
                <div class="inorder-container" id="inorder-container">
                    <!-- Populated by JS -->
                </div>
            </div>

            <!-- SVG Binary Search Tree Canvas -->
            <div class="canvas-card">
                <div class="canvas-toolbar">
                    <div class="panel-title">
                        <span>Assembled BST Structure</span>
                    </div>
                    <div style="display: flex; gap: 1rem; font-size: 0.78rem; color: var(--text-muted); align-items: center;">
                        <span style="display: inline-flex; align-items: center; gap: 0.3rem;"><span class="dot dot-blue"></span> Root</span>
                        <span style="display: inline-flex; align-items: center; gap: 0.3rem;"><span class="dot dot-green"></span> Leaf</span>
                        <span style="display: inline-flex; align-items: center; gap: 0.3rem;"><span class="dot dot-red"></span> Violating</span>
                    </div>
                </div>

                <div class="svg-container" id="svg-wrapper">
                    <!-- SVG Tree rendered here -->
                </div>
            </div>
        </div>
    </main>

    <!-- Test Suite Modal -->
    <div class="modal-overlay" id="test-modal">
        <div class="modal-box">
            <div class="modal-header">
                <h3 style="font-size: 1.1rem; font-weight: 700;">Backend Test Suite Execution (test_suite.py)</h3>
                <button onclick="closeModal()" style="background: none; border: none; color: var(--text-muted); font-size: 1.4rem; cursor: pointer;">&times;</button>
            </div>
            <div class="modal-body">
                <div style="margin-bottom: 0.75rem; font-size: 0.85rem; color: var(--text-muted);" id="test-status-msg">
                    Running Python unittest suite...
                </div>
                <pre class="test-output" id="test-output-box">Executing tests...</pre>
            </div>
        </div>
    </div>

    <script>
        const PRESETS = {
            1: "[[2, 1], [3, 2, 5], [5, 4]]",
            2: "[\n  [50, 25, 75],\n  [25, 15, 35],\n  [75, 60, 90],\n  [15, 10, 20],\n  [35],\n  [60],\n  [90]\n]",
            3: "[[5, 2, 8], [2, 1, 6]]",
            4: "[[3, 2, 5], [10, 8, 12]]"
        };

        function loadPreset(idx) {
            document.querySelectorAll('.preset-chip').forEach((chip, i) => {
                chip.classList.toggle('active', i + 1 === idx);
            });
            document.getElementById('frag-input').value = PRESETS[idx];
            submitRecovery();
        }

        async function submitRecovery() {
            const rawText = document.getElementById('frag-input').value.trim();
            if (!rawText) return;

            try {
                const response = await fetch('/api/recover', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ fragments: rawText })
                });
                const data = await response.json();
                renderResults(data);
            } catch (err) {
                console.error("Recovery request error:", err);
            }
        }

        function renderResults(data) {
            // Update input cards
            const grid = document.getElementById('fragment-grid');
            grid.innerHTML = '';
            if (data.fragments_info && data.fragments_info.length > 0) {
                document.getElementById('frag-count-badge').textContent = `${data.fragments_info.length} fragments`;
                data.fragments_info.forEach((f, i) => {
                    const card = document.createElement('div');
                    card.className = 'frag-card';
                    card.innerHTML = `
                        <div class="frag-card-header">Frag #${i+1}</div>
                        <div class="frag-root">Root: ${f.root}</div>
                        <div class="frag-children">
                            <span>L: ${f.left !== null ? f.left : '—'}</span>
                            <span>R: ${f.right !== null ? f.right : '—'}</span>
                        </div>
                    `;
                    grid.appendChild(card);
                });
            } else {
                document.getElementById('frag-count-badge').textContent = '0 fragments';
            }

            // Update Status Banner
            const banner = document.getElementById('status-banner');
            const pill = document.getElementById('status-pill');
            const meta = document.getElementById('status-meta');
            const sub = document.getElementById('status-sub');

            if (data.status === 'OK' || data.status === 'SUCCESS') {
                banner.className = 'status-banner ok';
                pill.textContent = 'STATUS: OK';
                meta.textContent = `Unified Root ID: ${data.root_id} | Total Student Records: ${data.inorder.length}`;
                sub.textContent = 'Global BST bounds [min < id < max] verified. All fragments connected with zero cycles.';
            } else {
                banner.className = 'status-banner impossible';
                pill.textContent = 'STATUS: IMPOSSIBLE';
                meta.textContent = data.reason || 'Merge impossible due to structural or ordering violation.';
                sub.textContent = 'Invariant check failed. Inspect the violation details and fragment configuration.';
            }

            // Update Inorder pills
            const inorderContainer = document.getElementById('inorder-container');
            inorderContainer.innerHTML = '';
            if (data.inorder && data.inorder.length > 0) {
                data.inorder.forEach((id, i) => {
                    const pillEl = document.createElement('span');
                    pillEl.className = 'inorder-pill';
                    pillEl.textContent = id;
                    inorderContainer.appendChild(pillEl);

                    if (i < data.inorder.length - 1) {
                        const arrow = document.createElement('span');
                        arrow.className = 'inorder-arrow';
                        arrow.innerHTML = '&rarr;';
                        inorderContainer.appendChild(arrow);
                    }
                });
            } else {
                inorderContainer.innerHTML = '<span style="color: var(--text-dim); font-size: 0.85rem;">[None - Merge failed]</span>';
            }

            // Update Leaves Badge
            document.getElementById('leaf-list-badge').textContent = data.leaves ? `Leaves: [${data.leaves.join(', ')}]` : '';

            // Update ASCII pre
            document.getElementById('ascii-output').textContent = data.ascii_tree || '(Empty or Invalid Tree)';

            // Render SVG Diagram
            renderSvgTree(data.tree_layout, data.violating_id);
        }

        function renderSvgTree(tree, violatingId) {
            const wrapper = document.getElementById('svg-wrapper');
            wrapper.innerHTML = '';

            if (!tree) {
                wrapper.innerHTML = '<div class="empty-state">&#9888; Tree could not be assembled.<br><span style="font-size: 0.8rem;">Review diagnostic reason above.</span></div>';
                return;
            }

            // Layout Tree in 2D coordinates
            const nodeRadius = 24;
            const levelHeight = 72;
            let currentX = 50;

            // Compute positions via inorder traversal
            function computeLayout(node, depth) {
                if (!node) return;
                computeLayout(node.left, depth + 1);
                node.x = currentX;
                node.y = depth * levelHeight + 50;
                currentX += 60;
                computeLayout(node.right, depth + 1);
            }

            computeLayout(tree, 0);

            const svgWidth = Math.max(currentX + 50, 480);
            const maxDepth = getMaxDepth(tree);
            const svgHeight = Math.max((maxDepth + 1) * levelHeight + 70, 360);

            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('width', svgWidth);
            svg.setAttribute('height', svgHeight);
            svg.setAttribute('viewBox', `0 0 ${svgWidth} ${svgHeight}`);

            // Draw edges first
            function drawEdges(node) {
                if (!node) return;
                if (node.left) {
                    drawEdge(node.x, node.y, node.left.x, node.left.y, 'L');
                    drawEdges(node.left);
                }
                if (node.right) {
                    drawEdge(node.x, node.y, node.right.x, node.right.y, 'R');
                    drawEdges(node.right);
                }
            }

            function drawEdge(x1, y1, x2, y2, label) {
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', x1);
                line.setAttribute('y1', y1);
                line.setAttribute('x2', x2);
                line.setAttribute('y2', y2);
                line.setAttribute('class', 'edge-line');
                svg.appendChild(line);

                const midX = (x1 + x2) / 2;
                const midY = (y1 + y2) / 2;
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', midX + (label === 'L' ? -10 : 10));
                text.setAttribute('y', midY);
                text.setAttribute('class', 'edge-label');
                text.textContent = label;
                svg.appendChild(text);
            }

            drawEdges(tree);

            // Draw nodes
            function drawNodes(node, isRoot) {
                if (!node) return;

                const isLeaf = !node.left && !node.right;
                const isViolating = violatingId !== null && Number(node.id) === Number(violatingId);

                const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');

                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', node.x);
                circle.setAttribute('cy', node.y);
                circle.setAttribute('r', nodeRadius);

                let cls = 'node-circle';
                if (isViolating) cls += ' violating-node';
                else if (isRoot) cls += ' root-node';
                else if (isLeaf) cls += ' leaf-node';
                circle.setAttribute('class', cls);
                g.appendChild(circle);

                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', node.x);
                text.setAttribute('y', node.y);
                text.setAttribute('class', 'node-text');
                text.textContent = node.id;
                g.appendChild(text);

                if (isRoot) {
                    const tag = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    tag.setAttribute('x', node.x);
                    tag.setAttribute('y', node.y - nodeRadius - 8);
                    tag.setAttribute('class', 'edge-label');
                    tag.setAttribute('fill', '#818cf8');
                    tag.textContent = '[ROOT]';
                    g.appendChild(tag);
                }

                svg.appendChild(g);

                drawNodes(node.left, false);
                drawNodes(node.right, false);
            }

            drawNodes(tree, true);
            wrapper.appendChild(svg);
        }

        function getMaxDepth(node) {
            if (!node) return 0;
            return 1 + Math.max(getMaxDepth(node.left), getMaxDepth(node.right));
        }

        async function runBackendTests() {
            document.getElementById('test-modal').classList.add('active');
            document.getElementById('test-status-msg').textContent = 'Executing backend test suite (test_suite.py)...';
            document.getElementById('test-output-box').textContent = 'Running tests...';

            try {
                const response = await fetch('/api/run-tests', { method: 'POST' });
                const res = await response.json();
                document.getElementById('test-status-msg').innerHTML = res.success
                    ? `<span style="color: var(--accent-green); font-weight: 700;">&#10004; All ${res.total_tests || ''} Tests Passed Successfully!</span>`
                    : `<span style="color: var(--accent-red); font-weight: 700;">&#10008; Test Suite Failures Detected</span>`;
                document.getElementById('test-output-box').textContent = res.output;
            } catch (err) {
                document.getElementById('test-output-box').textContent = 'Error connecting to test runner: ' + err;
            }
        }

        function closeModal() {
            document.getElementById('test-modal').classList.remove('active');
        }

        // Initialize with default preset 1
        window.addEventListener('DOMContentLoaded', () => {
            submitRecovery();
        });
    </script>
</body>
</html>
"""


def extract_violating_id(reason_str: Optional[str]) -> Optional[int]:
    """Helper to detect violating node ID from diagnostic error string."""
    if not reason_str:
        return None
    import re
    # Match patterns like 'Node ID 6' or 'node 6' or 'root 6'
    match = re.search(r'(?:Node ID|node|root)\s+(\d+)', reason_str, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return None


def node_to_dict(node: Optional[Node]) -> Optional[Dict[str, Any]]:
    """Converts a Node hierarchy into a serializable layout dict for SVG rendering."""
    if node is None:
        return None
    return {
        "id": node.id,
        "left": node_to_dict(node.left),
        "right": node_to_dict(node.right),
    }


def get_fragments_info(raw_input: Any) -> List[Dict[str, Any]]:
    """Extracts summary cards for each input fragment."""
    fragments = parse_fragments(raw_input)
    cards = []
    for f in fragments:
        if f is not None:
            cards.append({
                "root": f.id,
                "left": f.left.id if f.left else None,
                "right": f.right.id if f.right else None,
            })
    return cards


class RecoveryServerHandler(BaseHTTPRequestHandler):

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress routine HTTP request logging to keep console clean
        return

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        if parsed_url.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
        else:
            self.send_error(404, "Endpoint Not Found")

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/recover":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            try:
                payload = json.loads(body)
                raw_frag = payload.get("fragments", "")

                # Parse fragments
                fragments = parse_fragments(raw_frag)
                frag_info = get_fragments_info(raw_frag)

                # Recover student index
                res = recover_student_index(fragments)

                violating_id = extract_violating_id(res.get("reason", None))
                root_node = res.get("root", None)

                response_data = {
                    "status": res.get("status", "IMPOSSIBLE"),
                    "root_id": root_node.id if root_node else None,
                    "inorder": res.get("inorder", []),
                    "reason": res.get("reason", None),
                    "leaves": collect_leaf_ids(root_node) if root_node else [],
                    "ascii_tree": format_tree(root_node) if root_node else "",
                    "tree_layout": node_to_dict(root_node),
                    "fragments_info": frag_info,
                    "violating_id": violating_id,
                }
            except Exception as e:
                response_data = {
                    "status": "IMPOSSIBLE",
                    "root_id": None,
                    "inorder": [],
                    "reason": f"Input Parsing Error: {str(e)}",
                    "leaves": [],
                    "ascii_tree": "",
                    "tree_layout": None,
                    "fragments_info": [],
                    "violating_id": None,
                }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        elif parsed_url.path == "/api/run-tests":
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "unittest", "test_suite.py"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                output = proc.stdout + "\n" + proc.stderr
                success = (proc.returncode == 0)
                data = {
                    "success": success,
                    "output": output.strip(),
                    "total_tests": output.count(" ... ok") + output.count(" ... FAIL"),
                }
            except Exception as e:
                data = {
                    "success": False,
                    "output": f"Error running tests: {str(e)}",
                }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))

        else:
            self.send_error(404, "API Endpoint Not Found")


def find_available_port(preferred_port: int = 8080) -> int:
    """Finds an open port starting from preferred_port."""
    for port in range(preferred_port, preferred_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return preferred_port


def main():
    port = find_available_port(8080)
    server = HTTPServer(("127.0.0.1", port), RecoveryServerHandler)
    url = f"http://127.0.0.1:{port}"

    print("=" * 64)
    print("   STUDENT INDEX RECOVERY SYSTEM - INTERACTIVE WEB UI   ")
    print("=" * 64)
    print(f"Server active at: {url}")
    print("Launching browser interface automatically...")
    print("Press Ctrl+C to terminate the web server.")
    print("=" * 64)

    # Open browser automatically after server boots
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down web server. Goodbye!")
        server.server_close()


if __name__ == "__main__":
    main()
