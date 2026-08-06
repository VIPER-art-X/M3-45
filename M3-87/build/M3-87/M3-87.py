#!/usr/bin/env python3
# M3-86.py
r"""
MindMap -> .xmind GUI Exporter (M3-78)
========================================
Paste hierarchy text. The first entry MUST be lvl1[1] -- it becomes the root node.

New in M3-86 (layout fix):
  - The lvl-count labels now genuinely start at bf_container's top-left
    corner. The frame holding them was only anchor="w" with its width
    force-set separately (read from bf, applied after the fact) -- close
    enough most of the time but able to lag or mismatch bf_container's
    real cavity width and show up misaligned. Switched the frame to
    fill=tk.X so it always spans bf_container's exact width, and the
    reflow now measures the frame's own width instead of bf's, so x=0
    inside it is unambiguously bf_container's true left edge -- same
    column as the Copy button underneath it.
  - Fixed the Export box (ef) visibly stretching taller the more lvl
    rows there were. Cause: ef was packed with fill=tk.Y, i.e. "stretch
    to match this row's height" -- and the row's height is set by its
    tallest child, which became bf_container once the lvl-label reflow
    (M3-88) started wrapping onto multiple rows for maps with many
    levels. So more levels -> taller bf_container -> taller bottom_bar
    row -> ef stretched to match, even though ef's own content never
    changed. bf was never *supposed* to influence ef; fill=Y just made
    ef mirror whatever height its tallest sibling happened to have.
    Fixed by dropping fill=Y and anchoring ef to the bottom of the row
    instead (anchor="s"), matching bf_container's own anchor="s" -- ef
    now keeps its natural size and stays bottom-flush with bf_container
    regardless of how many lvl rows there are.

New in M3-88 (layout fix):
  - The lvl-count labels (lvl1=N, lvl2=N, ...) moved from their own
    full-width row above bottom_bar into bf_container, stacked directly
    above the Copy/Paste/Clear/... button row -- filling the empty gap
    that appeared there once that button row got bottom-anchored (M3-87),
    instead of leaving it blank. They wrap/reflow against bf's own
    measured width specifically (not the full panel width), so this
    whole column -- lvl labels, buttons, and the Total Nodes label --
    stays confined to its own side=LEFT container next to ef and can
    never extend under or behind the Export box.

New in M3-87 (layout fix corrections):
  - The Export box (ef) is now packed side=RIGHT instead of being
    stretched with fill=BOTH/expand=True -- the stretching approach in
    M3-86 inflated ef's own internal padding rather than actually moving
    the box, which read as "added padding" rather than "moved right".
    side=RIGHT places it flush against the right edge of its row (which
    already spans the full panel width) without changing its own size at
    all -- closing the gap to the right panel by repositioning, not
    resizing.
  - Fixed bf_container's anchor="s" (bottom) having no visible effect: it
    was also packed with fill=Y, which stretches the container itself to
    fill the whole row's height -- leaving no leftover space within it
    for the anchor to position against, so its content (the button row +
    Total Nodes label) stayed pinned to the top regardless of the anchor
    setting. Removed fill=Y so the container keeps its natural (short)
    height and anchor="s" actually pins that whole group to the bottom
    of the row, level with the bottom of the taller Export box beside it.

New in M3-86 (layout fixes):
  - The Export box (ef) now stretches to fill the remaining horizontal
    space in its row instead of stopping at its own natural width, which
    used to leave a visible gap between its right edge and the right
    panel. (It was packed with fill=Y only, no fill=X/expand.)
  - The Copy/Paste/Clear/... button row (bf) and the Total Nodes label
    beneath it are now anchored to the bottom of their shared container
    (bf_container) instead of the top, so that pairing sits flush with
    the bottom of the taller Export box beside it rather than floating
    near the top with empty space below.
  - The Total Nodes label is now centered under the button row (bf)
    instead of left-anchored.

New in M3-84 (equation-rendering bug-fix pass #2, plus UI requests):
  - Found and fixed a foundational bug that was quietly corrupting most
    equations authored with the JSON-style double-backslash escaping these
    hierarchy text files consistently use (every "\\begin{...}" meaning a
    literal "\begin{...}"): normalize() only ever collapsed an *exact*
    2-backslash run down to one, so a matrix row separator arriving
    double-escaped (4 backslash characters, representing the intended
    2-character "\\") fell through to the generic cleanup pass and got
    wrongly reduced to a single backslash -- silently breaking multi-row
    matrices -- and a command like \tag/\label arriving the same way had
    its command-specific pattern match starting from the *second*
    backslash, stripping the command but leaving the first backslash
    behind as orphaned stray text. Fixed with an early, universal
    "collapse a doubled command backslash" pass plus a corrected
    row-separator regex that handles any even-length run, not just
    exactly 2.
  - Fixed \text{...} content being visible to the NEEDS_BACKSLASH pass,
    which had no idea it might be inside a text argument -- e.g. plain
    "sum" inside \overbrace{...}^{\text{sum}} was being mistaken for the
    command \sum and rewritten into "\mathrm{\sum}". \text{} content is
    now protected as fully literal from the very start of normalize().
  - Added \overbrace/\underbrace (with optional ^{}/_{} labels), \boxed,
    \underline, \cancel, \bcancel, and \cancelto -- mathtext has zero
    support for any of these (confirmed directly), so each gets a
    dedicated hand-drawn renderer (brace/box/strikethrough over the
    rendered expression) instead of leaking the literal command as text.
  - Added \choose (-> \binom), \multirow (-> just its content, dropping
    the row-span behavior), \sideset (-> its base operator, dropping the
    corner annotations), \genfrac (-> \frac, optionally wrapped in
    \left\right if delimiters were given), and \DeclareMathOperator
    (parsed and substituted throughout the rest of the same equation) --
    none of these are mathtext commands, and each needed real structural
    rewriting rather than a simple whitelist/alias entry.
  - Fixed \operatorname{...} being silently downgraded to plain \mathrm
    (losing its correct operator-spacing behavior) by a stale mapping
    that pre-dated confirming mathtext actually renders \operatorname
    natively; also used to fix \arccot/\arcsec/\arccsc (mathtext knows
    \arcsin/\arccos/\arctan as built-ins but not their siblings) by
    aliasing them to \operatorname{arccot} etc.
  - Fixed \mathring, \qquad, and \middle all being missing from the
    known-command whitelist despite mathtext rendering every one of them
    natively (confirmed directly) -- same class of bug as \overrightarrow
    in M3-83.
  - Fixed \surd (the bare radical sign) raising a hard parse error;
    swapped for the actual unicode radical glyph.
  - Added \vphantom/\hphantom/\phantom -- mathtext has no support for
    these at all; since they're meant to be invisible spacers anyway,
    dropping them entirely (command + argument) is correct, not just a
    fallback.
  - Equation Settings: the Color, BG, and Format override checkboxes now
    default to checked, per request (Width/Height/Font remain unchecked).
  - Normal-mode text area: each hierarchy line's structure is now
    highlighted live -- the leading address ("lvl1[1]lvl2[3]...") gets a
    black background, the node name light sapphire, and the note/
    equation/label field values light green/light purple/light yellow
    respectively. Runs on every edit (typing, pasting, or Manual mode
    syncing back), not just on load.

New in M3-83 (equation-rendering bug-fix pass):
  - Fixed \overrightarrow{} losing its backslash and rendering as plain text
    ("overrightarrow{AB}") -- an asymmetry where mathtext's own symbol table
    recognizes \overleftarrow but not \overrightarrow, which the normalizer's
    known-command whitelist didn't account for.
  - Fixed \overset{...}{...} and \underset{...}{...} silently discarding
    their first argument (e.g. \overset{\rightarrow}{x} used to collapse to
    plain "x", losing the arrow) -- mathtext actually renders both natively,
    unlike \stackrel, which is the only one of the three that still needs
    the lossy "keep the base, drop the annotation" fallback.
  - Added a dedicated hand-drawn renderer for \xrightarrow{...} /
    \xleftarrow{...} (with an optional [...] label underneath), since
    mathtext has no support for amsmath's extensible arrows at all.
  - Fixed Vmatrix (double vertical bars) and smallmatrix being missing from
    the matrix-grid environment list, which meant their entire contents got
    thrown away and replaced with a literal "\mathrm{Vmatrix}" /
    "\mathrm{smallmatrix}" placeholder instead of being drawn. Both are now
    drawn like every other matrix type, with a real double-bar delimiter for
    Vmatrix and compact \scriptstyle-like sizing for smallmatrix.
  - Fixed hand-drawn parentheses/braces becoming visually invisible on tall
    matrices (e.g. a matrix whose own cells are matrices) -- they used to be
    a single fixed-angle arc across the whole height, which flattens out to
    a near-straight line at extreme aspect ratios even though something was
    technically being drawn. Now driven by a curve parameterized by
    normalized height, so the curvature stays visible at any size.
  - Added real \hline / \cline{a-b} support in array environments -- these
    aren't mathtext commands, so they used to fall through to the generic
    cell renderer and show up as literal text ("hline", "cline12"). Now
    extracted before row-splitting and drawn as actual horizontal rules
    (full-width for \hline, column-range-limited for \cline).
  - Added \multicolumn{n}{align}{content} support -- likewise used to leak
    through as literal defanged text ("multicolumn2cHeader"); now unwrapped
    into a real spanning cell centered across the columns it covers.
  - Fixed leftover preview .xmind temp files accumulating in the temp
    folder: the existing _register_temp/_cleanup_all_temps atexit safety
    net was never actually wired up to the preview file it was meant to
    protect, so a preview created and then the app closed before its
    30-second delayed-delete timer fired was never cleaned up. Previews are
    now registered with that safety net, the delayed delete retries a few
    times (in case an external viewer still has the file open when the
    timer first fires), and a startup sweep clears out any stale preview
    files left behind by earlier runs.

New in M3-82:
  - Fixed: main search bar (Find All / Enter) actually searches now -- it was
    clearing the entry box before reading it, so it always searched for "".
  - Main search bar is only shown in Normal mode; it is hidden while the Eq
    Adjuster panel is open (same as it already was for Manual mode).
  - Eq Adjuster panel reworked: Focus mode removed (no longer needed). It now
    shows a collapsible, searchable list of every node that has an equation.
    Click any node in the list to instantly show its equation image.
    Type in the list's search box to filter the list live (substring match);
    the top match's equation is shown immediately as you type.

Previously in M3-81:
  - Search: Enter triggers search, Clear clears the search box.
  - Eq size adjuster: integrated panel showing ONE equation at a time (fast, no lag).
    Use Left/Right arrows to navigate, scroll to adjust.
"""

import random
import json
import uuid
import zipfile
import re
import os
import io
import tempfile
import sys
import threading
import webbrowser
import time
import subprocess
import atexit
import shutil
import weakref
import copy
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, colorchooser
from tkinter import ttk
from typing import List, Dict, Optional, Any
import tkinter.font as tkFont

# -- Image & Equation support --------------------------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import urllib.request
import urllib.error
from PIL import Image, ImageTk, ImageDraw, ImageColor, ImageFont   # for EqAdjuster + matrix-grid rendering

# -- defaults ------------------------------------------------

# Reseed explicitly on every launch (M3-82) so anything randomized -- most
# visibly the Eq Adjuster's per-node list border colors -- gets a fresh
# palette each time this file is run, rather than reusing the same sequence.
random.seed(time.time_ns() ^ os.getpid())

def _random_color():
    return f"#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}"

def _random_border_color():
    # Kept away from the extremes (pure black/white) so every border stays
    # visible against the dark Eq Adjuster list background.
    return f"#{random.randint(70,230):02x}{random.randint(70,230):02x}{random.randint(70,230):02x}"

def _auto_text(fill_hex: str) -> str:
    brightness = (int(fill_hex[1:3], 16) * 299 + int(fill_hex[3:5], 16) * 587 + int(fill_hex[5:7], 16) * 114) / 1000
    return "#FFFFFF" if brightness < 128 else "#000000"

def _make_level_palette():
    palettes = []
    for _ in range(6):
        fill = _random_color()
        text = _auto_text(fill)
        line = _random_color()
        border = _random_color()
        palettes.append({
            "fill": fill,
            "fill_opacity": 100,
            "text": text,
            "line": line,
            "line_opacity": 100,
            "border": border,
            "border_opacity": 100,
            "font_size": 14,
            "line_width": 2,
            "border_width": 3,
            "branch_shape": "Rounded",
            "node_shape": "Rounded Rect",
        })
    palettes[0]["font_size"] = 18
    return palettes

DEFAULT_LEVEL_PALETTE = _make_level_palette()
DEFAULT_MAP_BG = "#264653"

WIDTH_TO_PT = {0: "0pt", 1: "1pt", 2: "2pt", 3: "3pt", 4: "4pt", 5: "5pt"}

# Image format options
IMAGE_FORMATS = ["jpg", "png", "gif", "webp"]
DEFAULT_IMAGE_FMT = "png"

DEFAULT_EQ_W = 200
DEFAULT_EQ_H = 100
DEFAULT_EQ_FONT = 50

# Safety caps
MAX_EQ_FONT = 150
MAX_EQ_WIDTH = 2000
MAX_EQ_HEIGHT = 500

# ============================================================
# Equation Normalizer (with new typo fixes)
# ============================================================
class EquationNormalizer:
    """
    v3 — merged best-of from the M3-81/claude/patched/deepseek comparison,
    with the following bugs fixed and gaps closed on top of the `claude`
    baseline (see analysis notes):

      * \\tag{...} / \\label{...} now removed WITH their argument via real
        balanced-brace parsing, instead of leaving a dangling "1}" behind
        (bug present in ALL four original variants).
      * \\stackrel{}{}, \\overset{}{}, \\underset{}{}, \\color{}{},
        \\textcolor{}{}, \\colorbox{}{} are now extracted with a real
        balanced-brace parser (keeping the semantically-important 2nd
        argument), so nested content like \\stackrel{\\Delta}{=} or
        \\color{red}{\\frac{a}{b}} no longer breaks. The naive
        string/regex replacements every prior variant used could not
        handle nested braces (this is what caused the "patched" variant's
        \\{...\\}-doubling bug and the "deepseek" variant's mangled
        \\overset output).
      * Empty \\frac{}{} / \\sqrt{} now default to a safe 0 instead of
        crashing the mathtext parser (adopted from the deepseek variant).
      * Stray inline-math '$' delimiters and trailing sentence punctuation
        are stripped (adopted from the deepseek variant).
      * \\color{...}{...} is now handled at all (previously only
        \\textcolor was, and even that discarded the color and misplaced
        the content outside the group).
    """
    NEEDS_BACKSLASH = [
        'frac', 'sqrt', 'sum', 'prod', 'int', 'lim', 'det',
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta',
        'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi',
        'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
        'Delta', 'Gamma', 'Lambda', 'Omega', 'Pi', 'Psi', 'Sigma', 'Theta', 'Xi',
        'cdot', 'times', 'pm', 'mp', 'leq', 'geq', 'neq', 'approx', 'propto',
        'partial', 'nabla', 'hbar', 'vec', 'mathbf', 'left', 'right',
        'bigl', 'bigr', 'quad',
        'oint', 'bar', 'dot', 'ddot', 'hat', 'tilde',
        # -- trig / log / named function operators (matplotlib mathtext operator names) --
        'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
        'sinh', 'cosh', 'tanh', 'coth',
        'arcsin', 'arccos', 'arctan',
        'log', 'ln', 'exp', 'lg',
        'min', 'max', 'sup', 'inf', 'gcd', 'deg', 'arg', 'ker', 'dim', 'hom',
        'liminf', 'limsup', 'Pr',
        # -- big operators / dots / infinity --
        'to', 'infty', 'cdots', 'ldots', 'dots', 'vdots', 'ddots',
        'iint', 'iiint', 'bigcup', 'bigcap', 'bigoplus', 'bigotimes',
        'bigwedge', 'bigvee', 'coprod',
        # -- set / logic symbols --
        'forall', 'exists', 'in', 'notin', 'ni',
        'subset', 'subseteq', 'supset', 'supseteq', 'subsetneq', 'supsetneq',
        'cup', 'cap', 'setminus', 'emptyset', 'varnothing',
        'wedge', 'vee', 'neg', 'oplus', 'otimes', 'ominus', 'oslash',
        # -- relations / geometry --
        'perp', 'parallel', 'angle', 'circ', 'sim', 'simeq', 'cong', 'equiv',
        'therefore', 'because', 'triangle', 'square',
        # -- misc symbols --
        'ell', 'prime', 'langle', 'rangle', 'mapsto', 'Re', 'Im', 'wp',
        'top', 'bot', 'aleph', 'star', 'ast', 'surd', 'flat', 'sharp', 'natural',
        'overline', 'underline', 'widehat', 'widetilde',
    ]
    # Simple 1:1 token replacements -- no brace-awareness needed.
    UNSUPPORTED = {
        # Matplotlib mathtext supports: matrix, pmatrix, bmatrix, vmatrix, array, cases
        # It does NOT support: aligned, align (amsmath environments)
        r'\begin{aligned}': r'\begin{array}{rcl}',
        r'\end{aligned}': r'\end{array}',
        r'\begin{align}': r'\begin{array}{rcl}',
        r'\end{align}': r'\end{array}',
        r'\text{': r'\mathrm{',
        r'\mathcal{': r'\mathrm{',
        r'\mathbb{': r'\mathrm{',
        r'\mathfrak{': r'\mathrm{',
        r'\omicron': 'o',
        r'\longrightarrow': r'\rightarrow',
        r'\leftrightarrow': r'\leftarrow',
        # -- additional graceful degradations for common LaTeX not in mathtext --
        r'\dfrac{': r'\frac{', r'\tfrac{': r'\frac{', r'\cfrac{': r'\frac{',
        r'\textbf{': r'\mathbf{', r'\bm{': r'\mathbf{', r'\boldsymbol{': r'\mathbf{',
        r'\textit{': r'\mathrm{', r'\emph{': r'\mathrm{',
        r'\textrm{': r'\mathrm{',
        r'\big': '', r'\Big': '', r'\bigg': '', r'\Bigg': '',
        # -- style/size-switch and limit-placement commands. Real LaTeX
        # supports these, but matplotlib's mathtext engine does not: it has
        # no \displaystyle/\textstyle/\scriptstyle/\scriptscriptstyle size
        # switches, and \sum/\int always place limits automatically with no
        # \limits/\nolimits toggle. These four used to be listed as "known"
        # commands (see _known_commands()) purely to stop the catch-all
        # backslash-stripper from touching them -- but "known" only meant
        # "don't mangle it", not "mathtext can actually render it". Left
        # in place with their backslash, mathtext's parser rejected them
        # outright at render time (see _safe_mathtext_line's "is invalid"
        # log line). Dropping them here entirely is safe: removing
        # \displaystyle/\textstyle changes nothing visually (mathtext has
        # only one size), and removing \limits/\nolimits changes nothing
        # either since mathtext's automatic placement is what you get
        # either way.
        r'\displaystyle': '', r'\textstyle': '',
        r'\scriptstyle': '', r'\scriptscriptstyle': '',
        r'\limits': '', r'\nolimits': '',
        # -- symbols matplotlib mathtext does NOT recognize as \commands,
        #    but that DO render fine as the raw unicode glyph. Without this,
        #    equations using these (e.g. the d'Alembertian \Box in wave
        #    equations) silently fail render_equation()'s primary render,
        #    fall through both fallback stages, and end up as a plain
        #    "[EQ ERROR]" placeholder image -- which is why it can look like
        #    "nothing happened" even though the terminal *does* print
        #    [Equation Render Error] / [Equation Render Fallback Error] for it.
        r'\Box': '\u25a1',        # d'Alembertian / white square
        r'\square': '\u25a1',     # NEEDS_BACKSLASH auto-prefixes bare "square" to this, but mathtext doesn't support \square itself
        r'\blacksquare': '\u25a0',
        r'\Diamond': '\u25c7',
        r'\lozenge': '\u25ca',
        r'\bigstar': '\u2605',
        r'\checkmark': '\u2713',
    }
    ALIAS_MAP = {
        r'\ge': r'\geq', r'\le': r'\leq', r'\ne': r'\neq',
        r'\to': r'\rightarrow', r'\gets': r'\leftarrow',
        r'\land': r'\wedge', r'\lor': r'\vee', r'\lnot': r'\neg',
        r'\iff': r'\Leftrightarrow', r'\implies': r'\Rightarrow',
        r'\varnothing': r'\emptyset',
        # mathtext knows \arcsin/\arccos/\arctan as built-in operators (with
        # correct spacing before their argument) but not their less-common
        # siblings -- \operatorname{} gives the same properly-spaced
        # upright-word rendering for these instead of a hard parse error.
        r'\arccot': r'\operatorname{arccot}',
        r'\arcsec': r'\operatorname{arcsec}',
        r'\arccsc': r'\operatorname{arccsc}',
        # \surd (the bare radical sign, as opposed to \sqrt which also
        # draws the vinculum bar over its argument) isn't a mathtext
        # command at all; swapped for the actual unicode glyph, which the
        # unicode-text rendering path (_find_unicode_text_blocks /
        # _render_unicode_text_image) already knows how to draw.
        r'\surd': '\u221A',
    }
    TYPO_MAP = {
        r'\leqqft': r'\left', r'\leqqqft': r'\left',
        r'\leftt': r'\left', r'\lefttt': r'\left',
        r'\righttt': r'\right', r'\rightt': r'\right',
        r'\leqftt': r'\left', r'\rigt': r'\right',
        r'\righ': r'\right', r'\lef': r'\left',
        r'\lft': r'\left', r'\rgt': r'\right',
        r'\th': r'\theta', r'\Th': r'\Theta',
        r'\h': r'\hbar',
        r'\c\dot': r'\cdot', r'\c': r'\cdot',
        r'\cdotdot': r'\cdot',
        r'\bar\bar': r'\bar',
        r'\cdotos': r'\cos',          # typo: \cdotos -> \cos
        r'\d\dot': r'\ddot',          # typo: \d\dot -> \ddot
        r'\d\ddot': r'\ddot',         # extra d
        r'\geqqq': r'\geq',            # typo: \geqqq -> \geq
        r'\leqqq': r'\leq',            # typo: \leqqq -> \leq
        r'\geqq': r'\geq',             # typo: \geqq -> \geq
        r'\leqq': r'\leq',             # typo: \leqq -> \leq
    }

    # Two-arg commands \cmd{arg1}{arg2} where the SECOND argument is the
    # semantically meaningful part actually being displayed. Handled with
    # real balanced-brace parsing so nested content (e.g. \frac{a}{b}
    # inside an argument) doesn't corrupt the match.
    # NOTE: \overset and \underset used to be listed here too, which threw
    # away their first argument (the annotation) and kept only the base --
    # e.g. \overset{\rightarrow}{x} (an arrow drawn above x, the standard
    # way to write a vector name with a single-letter base) collapsed down
    # to plain "x", silently losing the arrow. Matplotlib mathtext actually
    # renders \overset{...}{...} and \underset{...}{...} natively (unlike
    # \stackrel, which mathtext has no support for at all), so they've been
    # removed from this list and now pass through normalize() untouched.
    TWO_ARG_KEEP_SECOND = [
        r'\stackrel',
        r'\color', r'\textcolor', r'\colorbox', r'\fcolorbox',
    ]
    # Commands stripped ENTIRELY, including their argument (not rendered).
    STRIP_WITH_ARG = [r'\tag', r'\label', r'\vphantom', r'\hphantom', r'\phantom']

    # A handful of bare (non-letter) characters that ARE legitimate when
    # preceded by a backslash in mathtext (spacing commands \, \; \: \! \ ,
    # and the double-bar \|). Anything else of the form "\<symbol>" -- most
    # commonly a stray/mistyped escape like '\=' picked up from copy/paste,
    # or a text-mode accent command that has no meaning in math mode -- gets
    # its backslash stripped by the catch-all sanitizer in normalize().
    _KEEP_BARE_SYMBOLS = set(" ,;:!|_^%#")

    _KNOWN_COMMAND_NAMES = None  # lazily built + cached by _known_commands()

    @classmethod
    def _known_commands(cls):
        """Build (once) the set of bare command names (no leading
        backslash) that this normalizer recognizes as real, renderable
        LaTeX/mathtext commands. Anything with a backslash NOT in this set
        by the time the catch-all sanitizer runs is treated as an
        unrecognized macro (e.g. a user's own custom \\X / \\Y shorthand, or
        a typo) and has its backslash stripped so it degrades to plain,
        readable text instead of crashing the mathtext parser outright."""
        if cls._KNOWN_COMMAND_NAMES is not None:
            return cls._KNOWN_COMMAND_NAMES
        names = set(cls.NEEDS_BACKSLASH)
        for mapping in (cls.ALIAS_MAP, cls.TYPO_MAP):
            for k, v in mapping.items():
                for token in (k, v):
                    token = token.lstrip('\\')
                    token = re.split(r'[{}\\]', token)[0]
                    if token:
                        names.add(token)
        for k, v in cls.UNSUPPORTED.items():
            for token in (k, v):
                token = token.lstrip('\\')
                token = re.split(r'[{}\\]', token)[0]
                if token:
                    names.add(token)
        for cmd in list(cls.TWO_ARG_KEEP_SECOND) + list(cls.STRIP_WITH_ARG):
            names.add(cmd.lstrip('\\'))
        # Structural / mathtext-native commands not otherwise represented
        # above (font switches, environment keywords, common arrows/relations
        # that mathtext supports natively even though no map entry produces
        # them from a typo or alias).
        names |= {
            'begin', 'end', 'mathrm', 'mathbf', 'mathit', 'mathtt', 'mathsf',
            'rm', 'bf', 'it', 'cal', 'frak', 'bb', 'binom', 'substack', 'not',
            'displaystyle', 'textstyle', 'scriptstyle', 'scriptscriptstyle',
            'nolimits', 'limits', 'above', 'genfrac',
            'rightarrow', 'leftarrow', 'Rightarrow', 'Leftarrow',
            'leftrightarrow', 'Leftrightarrow', 'longrightarrow', 'longleftarrow',
            'Longrightarrow', 'Longleftarrow', 'hookrightarrow', 'hookleftarrow',
            'rightleftharpoons', 'uparrow', 'downarrow', 'updownarrow',
            'Uparrow', 'Downarrow', 'Updownarrow', 'nearrow', 'searrow',
            'swarrow', 'nwarrow',
            # mathtext's own symbol table recognizes \overleftarrow and
            # \overleftrightarrow (picked up by the backstop below), but --
            # oddly -- not \overrightarrow, even though mathtext renders it
            # fine once it isn't defanged first. Added explicitly here so
            # that asymmetry doesn't strip its backslash.
            'overrightarrow',
            # \xrightarrow{...} / \xleftarrow{...} (extensible arrows with
            # a label above, optionally another below in [...]) have no
            # mathtext support at all -- they're drawn by a dedicated
            # hand-built renderer instead (see _find_xarrow_blocks /
            # _render_xarrow_image). Kept out of NEEDS_BACKSLASH/UNSUPPORTED
            # and listed here purely so the catch-all sanitizer doesn't
            # strip their backslash before that renderer ever sees them.
            'xrightarrow', 'xleftarrow',
            # \overset/\underset used to be registered as "known" only as
            # a side effect of sitting in TWO_ARG_KEEP_SECOND; now that
            # they're handled natively (see the comment on that list),
            # they need to be listed here explicitly instead.
            'overset', 'underset',
            # \hline / \cline{a-b} (array row rules) aren't mathtext
            # commands either -- they're hand-drawn by the matrix grid
            # renderer (see _extract_line_commands / _render_matrix_image)
            # rather than ever reaching mathtext, so their backslash must
            # survive normalization the same way the matrix environments'
            # \\ row separators do.
            'hline', 'cline',
            # \multicolumn{n}{align}{content} -- likewise not a mathtext
            # command; unwrapped into a real spanning cell by the grid
            # renderer (see _parse_multicolumn) rather than reaching
            # mathtext, where it used to get defanged into literal text
            # like "multicolumn2cHeader".
            'multicolumn',
            # \mathring and \qquad are both rendered natively by mathtext
            # (confirmed directly against mathtext.MathTextParser) but were
            # simply missing from this whitelist -- \quad was listed but
            # its double-width sibling \qquad wasn't, and \mathring had no
            # entry at all, so both lost their backslash the same way
            # \overrightarrow used to.
            'mathring', 'qquad',
            # \middle -- mathtext renders \left ... \middle ... \right
            # natively (confirmed directly); it was just never added here.
            'middle',
            # \overbrace{expr}^{label} / \underbrace{expr}_{label} have no
            # mathtext support at all (confirmed: hard "Unknown symbol"
            # even for the bare, label-less form) -- drawn by a dedicated
            # renderer instead (see _find_brace_deco_blocks /
            # _render_brace_deco_image).
            'overbrace', 'underbrace',
            # \boxed{expr} -- no mathtext support; hand-drawn as a
            # rectangle around the rendered expression instead (see
            # _find_boxed_blocks / _render_boxed_image).
            'boxed',
            # \cancel{expr} / \bcancel{expr} / \cancelto{value}{expr} -- no
            # mathtext support; hand-drawn as a strike-through line over
            # the rendered expression instead (see _find_cancel_blocks /
            # _render_cancel_image).
            'cancel', 'bcancel', 'cancelto', 'underline',
            # \multirow{n}{width}{content}, \sideset{L}{R}, \genfrac{...},
            # and \DeclareMathOperator{...}{...} are all rewritten into
            # plain mathtext-renderable forms earlier in normalize() (see
            # _strip_multirow / _strip_sideset / _convert_genfrac /
            # _apply_declare_math_operator) -- listed here only as a
            # defensive backstop in case any residual, malformed instance
            # slips through those transforms unconverted; better to show
            # its bare content/backslash than crash the renderer.
            'multirow', 'sideset', 'genfrac', 'DeclareMathOperator',
        }
        # Authoritative backstop: matplotlib's own symbol table (delimiters
        # like \lfloor/\rfloor/\lceil/\rceil, extended Greek/relation/arrow
        # variants, etc.) covers hundreds of names our manual list above
        # can't be expected to fully replicate by hand. Anything matplotlib
        # itself recognizes as a real command must never be treated as an
        # unknown custom macro and stripped -- missing even one, as
        # \lfloor/\rfloor were initially, corrupts adjacent commands (e.g.
        # "\left\lfloor" collapsing into the single invalid token
        # "\leftlfloor" once \lfloor's backslash was wrongly removed).
        try:
            import matplotlib._mathtext_data as _mtd
            names |= set(_mtd.tex2uni.keys())
        except Exception:
            pass
        cls._KNOWN_COMMAND_NAMES = names
        return names

    @staticmethod
    def _find_matching_brace(s: str, open_idx: int) -> int:
        """s[open_idx] must be '{'. Returns index of the matching '}' or -1."""
        depth = 0
        i = open_idx
        while i < len(s):
            if s[i] == '{':
                depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        return -1

    @classmethod
    def _consume_braced_args(cls, s: str, start: int, n: int):
        """From index `start` (just after a command name), consume up to
        `n` consecutive {..} groups (skipping whitespace between them).
        Returns (list_of_arg_contents, index_after_last_consumed_char)."""
        args = []
        i = start
        for _ in range(n):
            j = i
            while j < len(s) and s[j] in ' \t':
                j += 1
            if j >= len(s) or s[j] != '{':
                break
            close = cls._find_matching_brace(s, j)
            if close == -1:
                break
            args.append(s[j + 1:close])
            i = close + 1
        return args, i

    @classmethod
    def _replace_two_arg_keep_second(cls, eq: str, cmd: str) -> str:
        out = []
        i = 0
        while True:
            idx = eq.find(cmd, i)
            if idx == -1:
                out.append(eq[i:])
                break
            after = idx + len(cmd)
            # avoid matching a longer command name that starts the same way
            # (e.g. \color must not swallow \colorbox)
            if after < len(eq) and eq[after].isalpha():
                out.append(eq[i:after])
                i = after
                continue
            args, end = cls._consume_braced_args(eq, after, 2)
            out.append(eq[i:idx])
            if len(args) == 2:
                out.append(args[1])
            elif len(args) == 1:
                out.append(args[0])
            i = end
        return ''.join(out)

    @classmethod
    def _strip_command_with_arg(cls, eq: str, cmd: str) -> str:
        out = []
        i = 0
        while True:
            idx = eq.find(cmd, i)
            if idx == -1:
                out.append(eq[i:])
                break
            after = idx + len(cmd)
            if after < len(eq) and eq[after].isalpha():
                out.append(eq[i:after])
                i = after
                continue
            args, end = cls._consume_braced_args(eq, after, 1)
            out.append(eq[i:idx])
            i = end  # drop the command AND its argument entirely
        return ''.join(out)

    @classmethod
    def _protect_text_args(cls, eq: str):
        """Swap every \\text{...} span for a placeholder containing no
        letters or backslashes, so nothing later in normalize() -- in
        particular the NEEDS_BACKSLASH pass, which has no idea it might
        be sitting inside a \\text argument -- can mistake a plain word
        inside it (e.g. "sum" in \\overbrace{...}^{\\text{sum}}) for a
        LaTeX command name and rewrite it into something else entirely
        (that exact case used to turn into "\\mathrm{\\sum}"). \\text{} is
        LaTeX's escape to plain text mode, so its contents should never
        be treated as math commands to begin with. Returns
        (protected_eq, list_of_original_contents); restore with
        _restore_text_args once the rest of normalize() has run."""
        contents: List[str] = []
        out = []
        i, n = 0, len(eq)
        cmd = r'\text'
        while i < n:
            idx = eq.find(cmd, i)
            if idx == -1:
                out.append(eq[i:])
                break
            after = idx + len(cmd)
            if after < n and eq[after].isalpha():
                out.append(eq[i:after])
                i = after
                continue
            j = after
            while j < n and eq[j] in ' \t':
                j += 1
            if j >= n or eq[j] != '{':
                out.append(eq[i:after])
                i = after
                continue
            close = cls._find_matching_brace(eq, j)
            if close == -1:
                out.append(eq[i:after])
                i = after
                continue
            out.append(eq[i:idx])
            token_idx = len(contents)
            contents.append(eq[j + 1:close])
            out.append(f'\uE001TXT{token_idx}\uE001')
            i = close + 1
        return ''.join(out), contents

    @staticmethod
    def _restore_text_args(eq: str, contents: List[str]) -> str:
        for idx, content in enumerate(contents):
            eq = eq.replace(f'\uE001TXT{idx}\uE001', r'\mathrm{' + content + '}')
        return eq

    @classmethod
    def _convert_choose(cls, eq: str) -> str:
        """TeX's infix `{A \\choose B}` -> `\\binom{A}{B}` (which mathtext
        already renders natively). \\choose has no mathtext support of its
        own at all, and -- being an infix operator rather than a prefix
        command with its own braced arguments -- can't be handled by the
        ordinary "\\cmd{arg}" machinery above; it always sits inside its
        own enclosing {...} group in real LaTeX, so find that group and
        split its content at \\choose instead."""
        while True:
            idx = eq.find(r'\choose')
            if idx == -1:
                return eq
            depth, open_idx, i = 0, -1, idx - 1
            while i >= 0:
                if eq[i] == '}':
                    depth += 1
                elif eq[i] == '{':
                    if depth == 0:
                        open_idx = i
                        break
                    depth -= 1
                i -= 1
            if open_idx == -1:
                # No enclosing brace found (malformed input) -- just drop
                # \choose itself rather than loop forever on it.
                eq = eq[:idx] + eq[idx + len(r'\choose'):]
                continue
            close_idx = cls._find_matching_brace(eq, open_idx)
            if close_idx == -1:
                eq = eq[:idx] + eq[idx + len(r'\choose'):]
                continue
            inner = eq[open_idx + 1:close_idx]
            c_idx = inner.find(r'\choose')
            num = inner[:c_idx].strip()
            den = inner[c_idx + len(r'\choose'):].strip()
            eq = eq[:open_idx] + r'\binom{' + num + '}{' + den + '}' + eq[close_idx + 1:]

    @classmethod
    def _strip_multirow(cls, eq: str) -> str:
        """\\multirow{n}{width}{content} -> content. Vertically merging
        cells across rows would need real cross-row layout support in the
        grid renderer; dropping just the row-span behavior and keeping
        the actual content visible is a reasonable simplification (and
        far better than leaking the literal command as text)."""
        cmd = r'\multirow'
        out, i = [], 0
        while True:
            idx = eq.find(cmd, i)
            if idx == -1:
                out.append(eq[i:])
                break
            after = idx + len(cmd)
            if after < len(eq) and eq[after].isalpha():
                out.append(eq[i:after])
                i = after
                continue
            args, end = cls._consume_braced_args(eq, after, 3)
            out.append(eq[i:idx])
            if len(args) == 3:
                out.append(args[2])
            i = end
        return ''.join(out)

    @classmethod
    def _strip_sideset(cls, eq: str) -> str:
        """\\sideset{L}{R}\\sum... -> \\sum... . mathtext has no support
        for \\sideset's corner-symbol placement at all; dropping the {L}{R}
        wrapper and keeping whatever base operator follows untouched is a
        reasonable simplification for this fairly obscure command."""
        cmd = r'\sideset'
        out, i = [], 0
        while True:
            idx = eq.find(cmd, i)
            if idx == -1:
                out.append(eq[i:])
                break
            after = idx + len(cmd)
            if after < len(eq) and eq[after].isalpha():
                out.append(eq[i:after])
                i = after
                continue
            args, end = cls._consume_braced_args(eq, after, 2)
            out.append(eq[i:idx])
            i = end  # drop \sideset{L}{R} entirely; base operator follows untouched
        return ''.join(out)

    @classmethod
    def _convert_genfrac(cls, eq: str) -> str:
        """\\genfrac{L}{R}{thickness}{style}{num}{den} -> \\frac{num}{den},
        wrapped in \\left L ... \\right R if delimiters were given.
        matplotlib mathtext does have its own \\genfrac, but with an
        incompatible argument convention (a bare numeric rule-width and a
        0-3 style digit, vs. amsmath's "0pt"/empty-style convention) --
        converting to the equivalent \\frac (+ \\left\\right) sidesteps
        that mismatch entirely instead of it raising a hard parse error."""
        cmd = r'\genfrac'
        out, i = [], 0
        while True:
            idx = eq.find(cmd, i)
            if idx == -1:
                out.append(eq[i:])
                break
            after = idx + len(cmd)
            if after < len(eq) and eq[after].isalpha():
                out.append(eq[i:after])
                i = after
                continue
            args, end = cls._consume_braced_args(eq, after, 6)
            out.append(eq[i:idx])
            if len(args) == 6:
                left, right, _thickness, _style, num, den = args
                left, right = left.strip(), right.strip()
                frac = r'\frac{' + num + '}{' + den + '}'
                if left or right:
                    frac = r'\left' + (left or '.') + ' ' + frac + r' \right' + (right or '.')
                out.append(frac)
            i = end
        return ''.join(out)

    @classmethod
    def _apply_declare_math_operator(cls, eq: str) -> str:
        """\\DeclareMathOperator{\\Name}{Text} (or the starred
        \\DeclareMathOperator*) defines \\Name as shorthand for
        \\operatorname{Text} for the rest of the document -- it produces
        no visible output of its own. Since this tool renders one
        equation snippet at a time rather than a full document with a
        preamble, mimic that effect directly within the snippet: strip
        each declaration out, then replace every later use of \\Name in
        the same equation with \\operatorname{Text}."""
        cmd = r'\DeclareMathOperator'
        out, i = [], 0
        substitutions: Dict[str, str] = {}
        while True:
            idx = eq.find(cmd, i)
            if idx == -1:
                out.append(eq[i:])
                break
            after = idx + len(cmd)
            if after < len(eq) and eq[after] == '*':
                after += 1
            elif after < len(eq) and eq[after].isalpha():
                out.append(eq[i:after])
                i = after
                continue
            args, end = cls._consume_braced_args(eq, after, 2)
            out.append(eq[i:idx])
            if len(args) == 2:
                name = args[0].strip().lstrip('\\').strip()
                if name:
                    substitutions[name] = args[1].strip()
            i = end
        eq = ''.join(out)
        for name, text in sorted(substitutions.items(), key=lambda kv: -len(kv[0])):
            eq = re.sub(r'\\' + re.escape(name) + r'(?![a-zA-Z])',
                         lambda m, t=text: r'\operatorname{' + t + '}', eq)
        return eq

    @classmethod
    def normalize(cls, raw: str) -> str:
        if not raw:
            return raw
        eq = raw.strip()

        # Strip stray inline-math '$'/'$$' delimiters some users paste in,
        # and trailing sentence punctuation that isn't part of the math.
        eq = eq.replace('$', '')
        # Also strip LaTeX's own \( \) and \[ \] math-mode delimiters -- a
        # very common artifact when equations are copied straight out of a
        # LaTeX document or an equation editor. Matplotlib mathtext doesn't
        # understand \( \[ as commands at all (it wraps content in $ $
        # itself), so left in place these crashed the parser immediately
        # instead of just being redundant, harmless delimiters.
        eq = re.sub(r'\\[()\[\]]', '', eq)
        eq = re.sub(r'[.;:!?"\']+$', '', eq).strip()

        # Collapse a doubled command backslash (e.g. "\\tag{1}" meaning a
        # literal "\tag{1}") down to one backslash, as early as possible --
        # this is extremely common in hierarchy text authored with
        # JSON-style escaping, where every real backslash in the source
        # LaTeX is written twice. Every command-specific pattern below
        # (STRIP_WITH_ARG, TWO_ARG_KEEP_SECOND, UNSUPPORTED, ALIAS_MAP,
        # TYPO_MAP, the known-command whitelist...) assumes a single
        # leading backslash, so doing this collapse only at the very end
        # (as before) was too late: a regex like STRIP_WITH_ARG's \tag
        # matcher would still find "\tag{1}" starting from the *second*
        # backslash of "\\tag{1}", correctly strip that, but leave the
        # first backslash behind as orphaned stray text (which is exactly
        # what caused \tag/\label content to come out as mangled leftover
        # backslashes instead of being cleanly dropped). Only backslash
        # runs immediately followed by a letter are touched here -- a run
        # followed by anything else (space, &, another backslash) is left
        # alone for the row-separator protection below, since that's
        # never a command name.
        eq = re.sub(r'\\{2,}(?=[a-zA-Z])', r'\\', eq)

        eq, _text_contents = cls._protect_text_args(eq)

        for cmd in cls.NEEDS_BACKSLASH:
            pat = r'(?<![a-zA-Z\\])' + re.escape(cmd) + r'(?![a-zA-Z])'
            eq = re.sub(pat, r'\\' + cmd, eq)

        # --- balanced-brace-aware handling (must run before naive string
        # replacements below, since those assume no nested braces) ---
        for cmd in cls.STRIP_WITH_ARG:
            eq = cls._strip_command_with_arg(eq, cmd)
        for cmd in cls.TWO_ARG_KEEP_SECOND:
            eq = cls._replace_two_arg_keep_second(eq, cmd)

        # Structural rewrites for commands mathtext can't render in their
        # original form at all, converted here (before matrix-environment
        # processing, since e.g. \multirow shows up as array-cell content)
        # into an equivalent form it can.
        eq = cls._convert_choose(eq)
        eq = cls._strip_multirow(eq)
        eq = cls._strip_sideset(eq)
        eq = cls._convert_genfrac(eq)
        eq = cls._apply_declare_math_operator(eq)

        # Matrix-like environments (pmatrix/bmatrix/vmatrix/Bmatrix/matrix/
        # array/cases) are intentionally NOT collapsed to a fixed placeholder
        # here anymore. matplotlib mathtext genuinely cannot render
        # \begin{...} environments at all, but the old behavior of replacing
        # their *contents* with a fixed "\cdots" string meant every matrix
        # equation normalized down to the same handful of strings regardless
        # of what was actually inside them (e.g. a matrix of fractions and a
        # matrix of dots rendered identically). The real content is now kept
        # intact through normalize() and drawn by a dedicated grid renderer
        # at render time (see XMindBuilder._find_matrix_blocks /
        # _render_matrix_image). The old placeholder logic is kept only as
        # an exception-safety fallback (XMindBuilder._collapse_matrix_placeholders).
        MATRIX_GRID_ENVS = ('pmatrix', 'bmatrix', 'vmatrix', 'Vmatrix', 'Bmatrix', 'matrix',
                            'smallmatrix', 'array', 'cases', 'aligned', 'align')

        # The `\\` row separator inside these environments must survive the
        # backslash-collapse pass further down (`\\+` -> `\`), which would
        # otherwise merge every matrix row into a single row. Swap `\\`
        # occurrences inside matrix-like blocks for a placeholder token that
        # contains no backslash characters, and restore it at the very end.
        ROW_SEP_TOKEN = '\uE000ROWSEP\uE000'

        def _protect_row_seps(m):
            block = m.group(0)
            # Any run of 2+ backslashes not immediately followed by a
            # letter is a row separator -- never a command name (those are
            # always followed by a letter, e.g. \\frac, \\end), regardless
            # of whether it arrived as a clean 2-char "\\" or double-escaped
            # to 4+ chars (the JSON-style "\\\\" convention these hierarchy
            # text files commonly use for a literal "\\"). Collapsing the
            # whole run to one token -- restored to exactly two backslashes
            # below -- handles both cases the same way instead of only the
            # already-correct 2-char one.
            return re.sub(r'\\{2,}(?![a-zA-Z])', ROW_SEP_TOKEN, block)

        eq = re.sub(
            r'\\begin\{(' + '|'.join(MATRIX_GRID_ENVS) + r')\}.*?\\end\{\1\}',
            _protect_row_seps, eq, flags=re.DOTALL,
        )

        # NOTE: \begin{aligned}/\begin{align} used to be swapped wholesale
        # for a fixed "\mathrm{aligned}" placeholder here, which discarded
        # every equation inside a system-of-equations block (e.g. "X &= f(x)
        # \\ Y &= g(x)") and replaced it with the literal word "aligned".
        # That's now fixed: aligned/align are included in MATRIX_GRID_ENVS
        # above (so their row separators survive), and the UNSUPPORTED map
        # below converts \begin{aligned}/\begin{align} to \begin{array}{rcl}
        # (which the dedicated grid renderer in XMindBuilder already knows
        # how to draw), so the real content is preserved and rendered
        # instead of thrown away.

        # Generic catch-all: ANY remaining \begin{xxx}...\end{xxx} environment we
        # didn't explicitly anticipate (smallmatrix, split, gather, multline,
        # eqnarray, subarray, ...) gets swapped for a safe plain-text
        # placeholder instead of crashing the renderer. Matrix-grid
        # environments are excluded here since their content passes through
        # untouched for the dedicated grid renderer to handle.
        eq = re.sub(
            r'\\begin\{(?!(?:' + '|'.join(MATRIX_GRID_ENVS) + r')\})(\w+?)\}.*?\\end\{\1\}',
            lambda m: r'\mathrm{' + m.group(1) + '}',
            eq, flags=re.DOTALL,
        )

        # Process longest keys first: plain dict order previously let e.g.
        # '\big' (processed before '\bigg') match as a literal substring
        # inside '\bigg'/'\Bigg', stripping only the "\big" prefix and
        # leaving a stray trailing "g" behind (turning "\bigg( x \bigg)"
        # into the corrupted "g( x g)"). Sorting by descending key length
        # guarantees the longer, more specific pattern always wins.
        for bad, good in sorted(cls.UNSUPPORTED.items(), key=lambda kv: -len(kv[0])):
            eq = eq.replace(bad, good)
        for old, new in cls.ALIAS_MAP.items():
            eq = re.sub(re.escape(old) + r'(?![a-zA-Z])', lambda m: new, eq)
        for wrong, correct in cls.TYPO_MAP.items():
            eq = re.sub(re.escape(wrong) + r'(?![a-zA-Z])', lambda m: correct, eq)
        eq = re.sub(r'\\leftt+', r'\\left', eq)
        eq = re.sub(r'\\rightt+', r'\\right', eq)
        eq = re.sub(r'\\(bar|dot|ddot|hat|tilde)\s*\\(bar|dot|ddot|hat|tilde)', r'\\\1', eq)
        eq = re.sub(r'\\(bar|dot|ddot|hat|tilde)\s*(?![a-zA-Z{])', '', eq)

        # --- Catch-all: defang any remaining unrecognized backslash-command ---
        # By this point every command this normalizer knows how to fix has
        # already been rewritten. Anything left of the form "\Word" or
        # "\<symbol>" that ISN'T a real, known command is almost always
        # either a custom macro from the user's own LaTeX preamble (e.g.
        # "\X"/"\Y" shorthand for bold variables, common in stats/ML notes)
        # or a stray/mistyped escape (e.g. "\=" left over from a text-mode
        # accent command). Matplotlib's mathtext parser has no idea what
        # these mean and raises a hard ValueError on them, which used to
        # take the whole line down to an unreadable plain-text fallback
        # (literally showing the backslash in the image). Stripping the
        # backslash here instead lets it degrade gracefully to the bare
        # letters/symbol, which is almost always what was intended.
        known = cls._known_commands()

        def _defang_word_cmd(m):
            if m.group(1) in known:
                return m.group(0)
            # Unrecognized command -> drop the backslash. If it's glued
            # directly onto a preceding letter run (e.g. "\left" immediately
            # followed by an unrecognized "\foo" with no space), stripping
            # the backslash naively would fuse the two into a single new
            # token ("leftfoo") that could itself accidentally match -- or
            # simply be sent on as one more unparseable command. A single
            # separating space guarantees that can never happen, at the
            # cost of a harmless extra space in the rendered output.
            prev = eq[m.start() - 1] if m.start() > 0 else ''
            return (' ' if prev.isalpha() else '') + m.group(1)

        eq = re.sub(r'\\([A-Za-z]+)', _defang_word_cmd, eq)
        eq = re.sub(
            r'\\([^A-Za-z{}\\])',
            lambda m: m.group(0) if m.group(1) in cls._KEEP_BARE_SYMBOLS else m.group(1),
            eq,
        )

        # Empty \frac{}{} / \sqrt{} -> safe defaults instead of a parser crash.
        eq = re.sub(r'\\frac\s*\{\s*\}\s*\{\s*\}', r'\\frac{0}{0}', eq)
        eq = re.sub(r'\\frac\s*\{\s*\}\s*\{([^{}]*)\}', r'\\frac{0}{\1}', eq)
        eq = re.sub(r'\\frac\s*\{([^{}]*)\}\s*\{\s*\}', r'\\frac{\1}{0}', eq)
        eq = re.sub(r'\\sqrt\s*\{\s*\}', r'\\sqrt{0}', eq)

        eq = cls._balance_braces(eq)
        eq = re.sub(r'\\+', r'\\', eq)
        eq = eq.replace(ROW_SEP_TOKEN, '\\\\')
        eq = cls._restore_text_args(eq, _text_contents)
        eq = re.sub(r'\{\s+', '{', eq)
        eq = re.sub(r'\s+\}', '}', eq)
        return eq.strip()

    @classmethod
    def _balance_braces(cls, eq: str) -> str:
        depth = 0
        for ch in eq:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
        return eq + '}' * max(0, depth)

    @classmethod
    def validate(cls, eq: str) -> tuple:
        warnings = []
        # \begin{...} is only genuinely "unsupported" if it's NOT one of the
        # matrix-grid environments XMindBuilder's dedicated grid renderer
        # (pmatrix/bmatrix/.../array/cases/aligned/align) already knows how
        # to draw -- flagging those here was a false alarm printed even on
        # equations that rendered correctly.
        grid_envs = getattr(globals().get('XMindBuilder'), 'MATRIX_GRID_ENVS', ())
        if r'\begin{' in eq and not re.search(r'\\begin\{(' + '|'.join(grid_envs) + r')\}', eq):
            warnings.append(r"unsupported \begin{}")
        if r'\text{' in eq:
            warnings.append(r"unsupported \text{}")
        if r'\omicron' in eq:
            warnings.append(r"unsupported \omicron")
        if r'\mathcal' in eq or r'\mathbb' in eq or r'\mathfrak' in eq:
            warnings.append(r"unsupported font command")
        depth = 0
        for ch in eq:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
            if depth < 0:
                return False, "unbalanced braces"
        if depth > 0:
            return False, f"unbalanced braces (+{depth})"
        return len(warnings) == 0, "; ".join(warnings) if warnings else "OK"

    @classmethod
    def auto_size(cls, latex: str) -> tuple:
        length = len(latex)
        if length < 15:
            return 160, 60, 18
        elif length < 30:
            return 220, 70, 18
        elif length < 50:
            return 280, 80, 18
        elif length < 80:
            return 350, 80, 16
        else:
            return 420, 90, 15

    @staticmethod
    def extract(raw: str) -> Optional[str]:
        if not raw:
            return None
        raw = raw.strip()
        # "equage" is the current field name; "equation" is kept as a legacy alias
        # so older saved hierarchies keep working. "eq" is a short alias too.
        key = r'(?:equage|equation)'
        m = re.search(key + r'\s*:\s*"((?:\\.|[^"\\])*)"', raw, re.IGNORECASE)
        if m:
            return m.group(1)
        m = re.search(r'\beq\b\s*:\s*"((?:\\.|[^"\\])*)"', raw, re.IGNORECASE)
        if m:
            return m.group(1)
        m = re.search(key + r"\s*:\s*'((?:\\.|[^'\\])*)'", raw, re.IGNORECASE)
        if m:
            return m.group(1)
        m = re.search(key + r'\s*:\s*\{([^}]+)\}', raw, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        m = re.search(key + r'\s*:\s*"([^",}]*)', raw, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if val:
                return val
        m = re.search(key + r'\s*:\s*([^,}]+?)(?=\s*(?:,|eq_|label|note|fill|text|border|line|\}|$))', raw, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if val:
                return val
        return None

# ============================================================
# Global temp file tracker
# ============================================================
_TEMP_FILES = []
def _register_temp(path):
    if path and path not in _TEMP_FILES:
        _TEMP_FILES.append(path)
def _cleanup_all_temps():
    for path in list(_TEMP_FILES):
        try:
            if os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass
        try:
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
        except Exception:
            pass
atexit.register(_cleanup_all_temps)

def _cleanup_stale_previews():
    """Sweep the temp folder for mindmap_preview_*.xmind files left over
    from earlier runs. _preview() writes one of these on every preview
    and relies on a background thread to delete it after a delay -- but
    if the app is closed before that delay elapses, or the external
    viewer still has the file open when the delete is attempted, that
    file is orphaned in the temp folder for good (the atexit cleanup
    above only knows about files _register_temp'd during THIS run, so it
    can't help with ones left behind by a previous run). Sweeping any
    pre-existing ones at startup, before this run creates its own, stops
    them from just accumulating forever."""
    try:
        tmp_dir = tempfile.gettempdir()
        for name in os.listdir(tmp_dir):
            if name.startswith("mindmap_preview_") and name.endswith(".xmind"):
                try:
                    os.remove(os.path.join(tmp_dir, name))
                except Exception:
                    pass
    except Exception:
        pass

# ============================================================
# Branch & Node shapes
# ============================================================
BRANCH_SHAPES = [
    ("Curve", "org.xmind.branchConnection.curve"),
    ("Arc", "org.xmind.branchConnection.arc"),
    ("Rounded", "org.xmind.branchConnection.roundedElbow"),
    ("Elbow", "org.xmind.branchConnection.elbow"),
    ("Straight", "org.xmind.branchConnection.straight"),
]
BRANCH_SHAPE_LABELS = [label for label, _ in BRANCH_SHAPES]
BRANCH_SHAPE_VALUES = {label: value for label, value in BRANCH_SHAPES}

NODE_SHAPES = [
    ("Rounded Rect", "org.xmind.topicShape.roundedRect"),
    ("Rectangle", "org.xmind.topicShape.rectangle"),
    ("Ellipse", "org.xmind.topicShape.ellipse"),
    ("Diamond", "org.xmind.topicShape.diamond"),
    ("Underline", "org.xmind.topicShape.underline"),
    ("Circle", "org.xmind.topicShape.circle"),
    ("Parallelogram", "org.xmind.topicShape.parallelogram"),
    ("Hexagon", "org.xmind.topicShape.hexagon"),
]
NODE_SHAPE_LABELS = [label for label, _ in NODE_SHAPES]
NODE_SHAPE_VALUES = {label: value for label, value in NODE_SHAPES}

STRUCTURE_DEFS = {
    "Mind Map": {
        "subs": {
            "Unbalanced": {"struct": "org.xmind.ui.map.unbalanced"},
            "Clockwise": {"struct": "org.xmind.ui.map.clockwise"},
            "Anticlockwise": {"struct": "org.xmind.ui.map.anticlockwise"},
        }
    },
    "Logic Chart": {
        "subs": {
            "Right": {"struct": "org.xmind.ui.logic.right"},
            "Left": {"struct": "org.xmind.ui.logic.left"},
        }
    },
    "Brace Map": {
        "subs": {
            "Right": {"struct": "org.xmind.ui.brace.right"},
            "Left": {"struct": "org.xmind.ui.brace.left"},
        }
    },
    "Tree Chart": {
        "subs": {
            "Right": {"struct": "org.xmind.ui.tree.right"},
            "Left": {"struct": "org.xmind.ui.tree.left"},
            "Balanced": {"struct": "org.xmind.ui.timeline.vertical"},
        }
    },
    "Org Chart": {
        "subs": {
            "Down": {"struct": "org.xmind.ui.org-chart.down"},
            "Up": {"struct": "org.xmind.ui.org-chart.up"},
        }
    },
    "Timeline": {
        "subs": {
            "Horizontal": {"struct": "org.xmind.ui.timeline.horizontal"},
            "Vertical": {"struct": "org.xmind.ui.timeline.vertical"},
        }
    },
    "Fishbone": {
        "subs": {
            "Right": {"struct": "org.xmind.ui.fishbone.leftHeaded"},
            "Left": {"struct": "org.xmind.ui.fishbone.rightHeaded"},
        }
    },
    "Matrix": {
        "subs": {
            "Row": {"struct": "org.xmind.ui.spreadsheet"},
            "Column": {"struct": "org.xmind.ui.spreadsheet.column"},
        }
    },
    "Tree Table": {
        "subs": {
            "Tile on top": {"struct": "org.xmind.ui.treetable.tileOnTop"},
            "Tile on left": {"struct": "org.xmind.ui.treetable.tileOnLeft"},
        }
    },
}

# ============================================================
# RTFText Widget
# ============================================================
class RTFText(tk.Text):
    def __init__(self, master=None, **kwargs):
        self._rtf_bg = kwargs.pop('rtf_bg', '#2d2d44')
        self._rtf_fg = kwargs.pop('rtf_fg', '#cdd6f4')
        self._rtf_font = kwargs.pop('rtf_font', ("Consolas", 11))
        super().__init__(master, **kwargs)
        self.config(bg=self._rtf_bg, fg=self._rtf_fg, font=self._rtf_font,
                   wrap=tk.WORD, padx=8, pady=8, relief=tk.FLAT)
        self._setup_tags()

    def _setup_tags(self):
        base_family = self._rtf_font[0]
        base_size = self._rtf_font[1] if len(self._rtf_font) > 1 else 11
        self.tag_configure("h1", font=(base_family, base_size + 13, "bold"), foreground="#b4befe")
        self.tag_configure("h2", font=(base_family, base_size + 9, "bold"), foreground="#b4befe")
        self.tag_configure("h3", font=(base_family, base_size + 6, "bold"), foreground="#b4befe")
        self.tag_configure("h4", font=(base_family, base_size + 3, "bold"), foreground="#b4befe")
        self.tag_configure("h5", font=(base_family, base_size + 1, "bold"), foreground="#b4befe")
        self.tag_configure("h6", font=(base_family, base_size, "bold"), foreground="#b4befe")
        self.tag_configure("b", font=(base_family, base_size, "bold"))
        self.tag_configure("i", font=(base_family, base_size, "italic"))
        self.tag_configure("u", underline=True)
        self.tag_configure("strong", font=(base_family, base_size, "bold"))
        self.tag_configure("em", font=(base_family, base_size, "italic"))
        self.tag_configure("code", font=("Courier", base_size))
        self.tag_configure("center", justify=tk.CENTER)

    def setRTF(self, rtf_text, pad=(8, 8), bg=None, font=None):
        self.delete("1.0", tk.END)
        if bg:
            self.config(bg=bg)
        if font:
            self.config(font=font)
            self._rtf_font = font
            self._setup_tags()
        import re
        pattern = re.compile(r'<(/?)([a-zA-Z0-9]+)(?::([^>]*))?>([^<]*)', re.IGNORECASE)
        pos = 0
        tag_stack = []
        while pos < len(rtf_text):
            match = pattern.search(rtf_text, pos)
            if not match:
                remaining = rtf_text[pos:]
                if remaining:
                    self.insert(tk.END, remaining, tuple(tag_stack) if tag_stack else '')
                break
            if match.start() > pos:
                text_before = rtf_text[pos:match.start()]
                if text_before:
                    self.insert(tk.END, text_before, tuple(tag_stack) if tag_stack else '')
            closing, tag_name, attr, after_text = match.groups()
            tag_name = tag_name.lower()
            if closing:
                if tag_name in tag_stack:
                    tag_stack.remove(tag_name)
            else:
                if tag_name in ('h1','h2','h3','h4','h5','h6',
                                'b','i','u','strong','em','code','center'):
                    tag_stack.append(tag_name)
                elif tag_name == 'br':
                    self.insert(tk.END, chr(10))
                elif tag_name == 'hr':
                    self.insert(tk.END, "─" * 40 + chr(10))
            if after_text and not closing:
                self.insert(tk.END, after_text, tuple(tag_stack) if tag_stack else '')
            pos = match.end()

class RTFScrolledText(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, bg=kwargs.pop('bg', '#1e1e2e'))
        self.text = RTFText(self, **kwargs)
        self.scrollbar = tk.Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    def setRTF(self, rtf_text, **kwargs):
        self.text.setRTF(rtf_text, **kwargs)
    def get(self, *args, **kwargs):
        return self.text.get(*args, **kwargs)
    def insert(self, *args, **kwargs):
        return self.text.insert(*args, **kwargs)
    def delete(self, *args, **kwargs):
        return self.text.delete(*args, **kwargs)

# ============================================================
# XMindBuilder (with eq_w/eq_h support and improved fallback)
# ============================================================
class XMindBuilder:
    def __init__(self, title: str = "Mind Map",
                 layout: str = "org.xmind.ui.map.unbalanced",
                 level_colors: Optional[List[Dict[str, Any]]] = None,
                 color_mode: Optional[List[str]] = None,
                 map_bg: str = DEFAULT_MAP_BG,
                 note_heading: bool = False,
                 default_img_fmt: str = DEFAULT_IMAGE_FMT,
                 eq_override_flags: Optional[Dict[str, bool]] = None,
                 eq_design: Optional[Dict[str, Any]] = None):
        self.title = title
        self.layout = layout
        self.level_colors = level_colors or [c.copy() for c in DEFAULT_LEVEL_PALETTE]
        self.color_mode = color_mode or ["fallback"] * len(self.level_colors)
        self.map_bg = map_bg
        self.note_heading = note_heading
        self.default_img_fmt = default_img_fmt
        self.eq_override_flags = eq_override_flags or {}
        self.eq_design = eq_design or {}
        self.topics: List[Dict[str, Any]] = []

    def uid(self) -> str:
        return str(uuid.uuid4())

    @staticmethod
    def split_equation_lines(latex: str) -> List[str]:
        # NOTE (v4 fix): previously this only tracked `{ }` depth, so a comma
        # sitting inside plain parentheses or brackets -- e.g. the "x,v" in
        # "D_{ij}(\mathbf{x},\mathbf{v})" -- was treated as a top-level comma
        # and split into a new "line". That silently chopped equations like
        # the Fokker-Planck one in half mid-\left[...\right], leaving a
        # dangling "\left[" with no matching "\right]" in the first half,
        # which is exactly what produced the
        # "ParseSyntaxException: Expected '\right', found end of text" error.
        # Now () and [] are tracked alongside {} so commas inside ANY of the
        # three bracket types are correctly ignored.
        #
        # NOTE (v5 fix): matrix-grid environments (pmatrix/bmatrix/.../
        # array/cases/aligned/align) are handled by a dedicated grid
        # renderer downstream (_render_line_composite / _find_matrix_blocks),
        # but only if they survive intact as a single "line" out of this
        # function. Piecewise "cases" branches very commonly contain
        # top-level commas (e.g. "x, & x > 0 \\ -x, & x \le 0"), and this
        # comma-split used to run with no awareness of \begin{...}\end{...}
        # spans at all -- shredding the block into broken fragments before
        # it ever reached the grid renderer, and producing exactly the kind
        # of "line '...' is invalid" fallback warnings this was meant to
        # avoid. Matrix-grid blocks are now protected as single opaque units
        # here first, so any commas inside them are ignored entirely.
        blocks = XMindBuilder._find_matrix_blocks(latex)
        protected = latex
        placeholders = {}
        if blocks:
            pieces = []
            cursor = 0
            for i, b in enumerate(blocks):
                token = f'\uE010BLOCK{i}\uE010'
                pieces.append(latex[cursor:b['start']])
                pieces.append(token)
                placeholders[token] = latex[b['start']:b['end']]
                cursor = b['end']
            pieces.append(latex[cursor:])
            protected = ''.join(pieces)

        lines = []
        current = []
        depth = 0
        for ch in protected:
            if ch in '{([':
                depth += 1
                current.append(ch)
            elif ch in '})]':
                depth -= 1
                current.append(ch)
            elif ch == ',' and depth == 0:
                if current and current[-1] == '\\':
                    # This comma belongs to \, (thin space), not a
                    # line-separator -- keep it attached to the backslash.
                    current.append(ch)
                else:
                    lines.append(''.join(current).strip())
                    current = []
            else:
                current.append(ch)
        if current:
            lines.append(''.join(current).strip())
        lines = [line for line in lines if line]
        if placeholders:
            restored = []
            for line in lines:
                for token, original in placeholders.items():
                    line = line.replace(token, original)
                restored.append(line)
            lines = restored
        return lines

    _equation_render_cache: Dict[tuple, bytes] = {}

    @staticmethod
    def render_equation(latex: str, fontsize: int = 18, text_color: str = "black",
                        bg_color: str = "#ffffff", fmt: str = "png",
                        width: Optional[int] = None, height: Optional[int] = None) -> bytes:
        # Cache on every parameter that changes the rendered pixels. Preview
        # (and the Eq Adjuster) re-render the whole map's equations on every
        # call even when most nodes haven't changed since the last preview;
        # this cache turns those repeat renders into a dict lookup instead
        # of a fresh matplotlib figure + savefig, which is what made preview
        # noticeably slower the more equations a map had.
        cache_key = (latex, fontsize, text_color, bg_color, fmt, width, height)
        cached = XMindBuilder._equation_render_cache.get(cache_key)
        if cached is not None:
            return cached
        result = XMindBuilder._render_equation_uncached(
            latex, fontsize, text_color, bg_color, fmt, width, height)
        # Simple unbounded-but-capped cache: clear if it grows too large
        # rather than tracking per-entry LRU, since equations are small text
        # keys and previews rarely churn through thousands of variants.
        if len(XMindBuilder._equation_render_cache) > 2000:
            XMindBuilder._equation_render_cache.clear()
        XMindBuilder._equation_render_cache[cache_key] = result
        return result

    @staticmethod
    def _render_equation_uncached(latex: str, fontsize: int = 18, text_color: str = "black",
                        bg_color: str = "#ffffff", fmt: str = "png",
                        width: Optional[int] = None, height: Optional[int] = None) -> bytes:
        # Note: latex should already be normalized by HierarchyParser or ManualModeEditor
        is_valid, msg = EquationNormalizer.validate(latex)
        if not is_valid:
            print(f"[Equation Warning] {msg} — attempting fallback render")

        if fontsize > MAX_EQ_FONT:
            fontsize = MAX_EQ_FONT
        if fmt.lower() in ("jpg", "jpeg") and bg_color == "none":
            bg_color = "#ffffff"

        # Determine figure size (in inches) from user dimensions or auto
        if width is not None and height is not None:
            fig_width = max(1.0, width / 100.0)
            fig_height = max(1.0, height / 100.0)
        else:
            fig_width = max(6.0, len(latex) * 0.2 + 2.0)
            fig_height = max(1.5, fontsize / 12 + 0.8)
        # Safety caps
        max_fig_width = 40.0
        max_fig_height = 20.0
        if fig_width > max_fig_width:
            fig_width = max_fig_width
        if fig_height > max_fig_height:
            fig_height = max_fig_height

        # Use higher DPI for better quality
        dpi = 150

        lines = XMindBuilder.split_equation_lines(latex)
        if len(lines) > 1:
            needed_height = max(fig_height, len(lines) * (fontsize / 14 + 0.5))
            figsize = (fig_width, needed_height)
            return XMindBuilder._render_multiline_equations(lines, fontsize, text_color, bg_color, fmt, figsize, dpi)
        else:
            figsize = (fig_width, fig_height)
            try:
                # Matrix-like environments (pmatrix/bmatrix/vmatrix/Bmatrix/
                # matrix/array/cases) can't be handed to mathtext at all --
                # it has no support for \begin{...}. If this line contains
                # one, render it as a real grid (with each cell rendered
                # independently, so \frac, \cdots, \vdots, \ddots, etc.
                # inside cells all still work) instead of collapsing it to a
                # fixed placeholder string.
                composite = XMindBuilder._render_line_composite(
                    latex, fontsize, text_color, bg_color, fmt, dpi)
                if composite is not None:
                    return composite
                return XMindBuilder._render_latex(latex, fontsize, text_color, bg_color, fmt, figsize, dpi)
            except Exception as e:
                print(f"[Equation Render Error] '{latex}': {e}")
                stripped = re.sub(r'\\left[\(\[\{]', '(', latex)
                stripped = re.sub(r'\\right[\)\]\}]', ')', stripped)
                try:
                    return XMindBuilder._render_latex(stripped, fontsize, text_color, bg_color, fmt, figsize, dpi)
                except Exception as e2:
                    print(f"[Equation Render Fallback Error] '{stripped}': {e2}")
                    # Exception-safety fallback only: collapse any matrix-like
                    # environments to the old fixed placeholder strings (e.g.
                    # "\left( \cdots \right)") so the equation at least
                    # renders as *something* recognizable instead of raising,
                    # rather than being the normal behavior for every matrix.
                    placeholder_eq = XMindBuilder._collapse_matrix_placeholders(latex)
                    if placeholder_eq != latex:
                        try:
                            return XMindBuilder._render_latex(placeholder_eq, fontsize, text_color, bg_color, fmt, figsize, dpi)
                        except Exception as e3:
                            print(f"[Equation Render Placeholder Fallback Error] '{placeholder_eq}': {e3}")
                    return XMindBuilder._render_equation_fallback(latex, fontsize, text_color, bg_color, fmt, dpi)

    @staticmethod
    def _safe_mathtext_line(line: str, fontsize: int, dpi: int) -> str:
        """Return a version of `line` guaranteed to render in mathtext.
        Tries the line as-is, then with \\left/\\right stripped (matching the
        single-equation fallback), then gives up and returns it WITHOUT the
        surrounding $ so it's drawn as plain text -- broken, visibly, but
        without raising and taking the rest of the multi-line image down
        with it."""
        import matplotlib.mathtext as mathtext
        parser = mathtext.MathTextParser("agg")
        candidates = [line]
        stripped = re.sub(r'\\left[\(\[\{]', '(', line)
        stripped = re.sub(r'\\right[\)\]\}]', ')', stripped)
        if stripped != line:
            candidates.append(stripped)
        for cand in candidates:
            try:
                parser.parse(f"${cand}$", dpi=dpi, prop=None)
                return f"${cand}$"
            except Exception:
                continue
        print(f"[Equation Render Error] line '{line}' is invalid — showing as plain text instead of failing the whole equation")
        return line

    @staticmethod
    def _render_multiline_equations(lines: List[str], fontsize: int, text_color: str, bg_color: str, fmt: str, figsize: tuple, dpi: int) -> bytes:
        # BUGFIX: a matrix-grid environment (pmatrix/bmatrix/.../cases) that
        # ends up sharing a line-list with anything else -- e.g. two
        # matrices separated by a top-level comma, which is exactly what
        # split_equation_lines() treats as a "new line" -- used to be handed
        # straight to _safe_mathtext_line() below, which can only try
        # mathtext on the raw \begin{...}...\end{...} text and fail, since
        # mathtext has no support for \begin{} at all. That silently
        # degraded every such matrix to broken, unrendered plain text
        # instead of the real per-cell grid the single-line path already
        # knows how to draw (see _render_line_composite / _find_matrix_blocks).
        # Detect that case first and, only when at least one line actually
        # needs it, render the whole thing as a stack of PIL images (reusing
        # the same per-line grid builder as the single-line path) instead of
        # the plain matplotlib ax.text() path below.
        line_images = [XMindBuilder._build_line_image(line, fontsize, text_color, dpi) for line in lines]
        if any(img is not None for img in line_images):
            for i, line in enumerate(lines):
                if line_images[i] is None:
                    # Plain line living alongside a matrix line elsewhere in
                    # this equation -- render through the same safe-mathtext
                    # cell path used for ordinary matrix cells, for a
                    # consistent look and the same crash-safety.
                    line_images[i] = XMindBuilder._render_cell_image(line, fontsize, text_color, dpi)
            return XMindBuilder._compose_stacked_lines(line_images, bg_color, fmt)

        n_lines = len(lines)
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        if bg_color == "none":
            fig.patch.set_alpha(0)
            ax.set_facecolor((0, 0, 0, 0))
        else:
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
        ax.axis("off")
        for i, line in enumerate(lines):
            y = 1.0 - (i + 0.5) / n_lines
            safe_text = XMindBuilder._safe_mathtext_line(line, fontsize, dpi)
            ax.text(0.5, y, safe_text,
                    fontsize=fontsize, ha="center", va="center",
                    color=text_color, transform=ax.transAxes)
        buf = io.BytesIO()
        save_fmt = "jpeg" if fmt.lower() in ("jpg", "jpeg") else fmt.lower()
        plt.savefig(buf, format=save_fmt, bbox_inches="tight",
                    transparent=(bg_color == "none"), dpi=dpi)
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    @staticmethod
    def _compose_stacked_lines(line_images: List['Image.Image'], bg_color: str, fmt: str) -> bytes:
        """Stack per-line PIL images (each either a plain safe-mathtext
        cell or a matrix-grid composite) vertically, centered, then apply
        the background fill and encode -- the same tail step
        _render_line_composite uses for a single line."""
        pad_y = max(4, line_images[0].height // 6) if line_images else 4
        total_w = max(im.width for im in line_images)
        total_h = sum(im.height for im in line_images) + pad_y * (len(line_images) - 1)
        combo = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
        y = 0
        for im in line_images:
            x = (total_w - im.width) // 2
            combo.alpha_composite(im, (x, y))
            y += im.height + pad_y

        is_jpeg = fmt.lower() in ("jpg", "jpeg")
        if bg_color == "none" and not is_jpeg:
            final_img = combo
        else:
            fill_color = bg_color if bg_color != "none" else "#ffffff"
            try:
                bg_rgb = ImageColor.getrgb(fill_color)
            except ValueError:
                bg_rgb = (255, 255, 255)
            bg = Image.new('RGBA', combo.size, bg_rgb + (255,))
            bg.alpha_composite(combo)
            final_img = bg
        if is_jpeg and final_img.mode != "RGB":
            final_img = final_img.convert("RGB")

        buf = io.BytesIO()
        save_fmt = "JPEG" if is_jpeg else fmt.upper()
        final_img.save(buf, format=save_fmt)
        buf.seek(0)
        return buf.read()

    @staticmethod
    def _render_latex(latex: str, fontsize: int, text_color: str, bg_color: str, fmt: str, figsize: tuple, dpi: int) -> bytes:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        if bg_color == "none":
            fig.patch.set_alpha(0)
            ax.set_facecolor((0, 0, 0, 0))
        else:
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
        ax.axis("off")
        ax.text(0.5, 0.5, f"${latex}$",
                fontsize=fontsize, ha="center", va="center",
                color=text_color, transform=ax.transAxes)
        buf = io.BytesIO()
        save_fmt = "jpeg" if fmt.lower() in ("jpg", "jpeg") else fmt.lower()
        plt.savefig(buf, format=save_fmt, bbox_inches="tight",
                    transparent=(bg_color == "none"), dpi=dpi)
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    @staticmethod
    def _render_equation_fallback(latex: str, fontsize: int, text_color: str, bg_color: str, fmt: str, dpi: int) -> bytes:
        if fmt.lower() in ("jpg", "jpeg") and bg_color == "none":
            bg_color = "#ffffff"
        fig, ax = plt.subplots(figsize=(8, 2.5), dpi=dpi)
        if bg_color == "none":
            fig.patch.set_alpha(0)
            ax.set_facecolor((0, 0, 0, 0))
        else:
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
        ax.axis("off")
        # Detect common malformed patterns for better error messaging
        is_malformed = any(pat in latex for pat in ['\\frac{}', '\\sqrt{}', '_{}', '^{}', '\\left( \\right)', '\\begin{}', '\\end{}'])
        if is_malformed:
            display = "[EQ ERROR] Malformed LaTeX"
        elif len(latex) > 80:
            display = f"[EQ] {latex[:77]}..."
        else:
            display = f"[EQ] {latex}"
        ax.text(0.5, 0.5, display,
                fontsize=max(10, fontsize - 4), ha="center", va="center",
                color=text_color, transform=ax.transAxes, family='monospace')
        buf = io.BytesIO()
        save_fmt = "jpeg" if fmt.lower() in ("jpg", "jpeg") else fmt.lower()
        plt.savefig(buf, format=save_fmt, bbox_inches="tight",
                    transparent=(bg_color == "none"), dpi=dpi)
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    # --------------------------------------------------------------
    # Matrix-grid rendering.
    #
    # matplotlib mathtext cannot parse \begin{...}/\end{...} environments
    # at all, so matrix-like equations (pmatrix, bmatrix, vmatrix, Bmatrix,
    # matrix, array, cases) can't just be handed to it. The methods below
    # locate those blocks, split them into real rows/cells, render each
    # cell as its own small mathtext image (so \frac, \cdots, \vdots,
    # \ddots etc. inside cells work normally), and lay the cells out into
    # an actual grid with hand-drawn delimiters -- instead of the old
    # approach of throwing the contents away and drawing a fixed
    # "\left( \cdots \right)"-style placeholder for every matrix.
    # --------------------------------------------------------------

    MATRIX_GRID_ENVS = ('pmatrix', 'bmatrix', 'vmatrix', 'Vmatrix', 'Bmatrix', 'matrix',
                        'smallmatrix', 'array', 'cases')

    # Sentinel meaning "no override supplied -- use the env's default
    # delimiter", distinct from an override of None (an explicit
    # invisible delimiter, e.g. \left. with no visible bracket).
    _NO_OVERRIDE = object()

    # Recognizes a \left<delim> immediately preceding a matrix block (so
    # it can be swallowed into the block instead of left as an orphaned,
    # unmatched \left with nothing to pair it with).
    _LEFT_DELIM_RE = re.compile(r'\\left\s*(\\\{|\\\||\(|\[|\.|\|)\s*$')
    # Recognizes a \right<delim> immediately following a matrix block,
    # for the same reason.
    _RIGHT_DELIM_RE = re.compile(r'^\s*\\right\s*(\\\}|\\\||\)|\]|\.|\|)')
    # An evaluation bar's \right often carries a trailing sub/superscript
    # right after the delimiter, e.g. \right|_{x=0} or \right|_0^1.
    _RIGHT_SUFFIX_RE = re.compile(r'^(?:_\{[^{}]*\}|\^\{[^{}]*\}|_[^\s{}\\]|\^[^\s{}\\])+')
    _DELIM_TOKEN_TO_CHAR = {
        '(': '(', ')': ')', '[': '[', ']': ']',
        '\\{': '{', '\\}': '}',
        '|': '|', '\\|': '|',
        '.': None,
    }

    @staticmethod
    def _find_matrix_blocks(latex: str) -> List[Dict[str, Any]]:
        """Find top-level, non-overlapping \\begin{ENV}...\\end{ENV} spans
        for the matrix-grid environments. Returns a list of dicts with
        start/end (character offsets into `latex`), env name, and the raw
        content between the begin/end tags, in left-to-right order."""
        begin_re = re.compile(r'\\begin\{(' + '|'.join(XMindBuilder.MATRIX_GRID_ENVS) + r')\}')
        blocks = []
        i = 0
        n = len(latex)
        while i < n:
            m = begin_re.search(latex, i)
            if not m:
                break
            env = m.group(1)
            start = m.start()
            after = m.end()
            if env == 'array':
                # Consume the optional [pos] and required {cols} args that
                # follow \begin{array} before the actual cell content starts.
                j = after
                while j < n and latex[j] in ' \t':
                    j += 1
                if j < n and latex[j] == '[':
                    k = latex.find(']', j)
                    if k == -1:
                        i = after
                        continue
                    j = k + 1
                while j < n and latex[j] in ' \t':
                    j += 1
                if j < n and latex[j] == '{':
                    close = EquationNormalizer._find_matching_brace(latex, j)
                    if close == -1:
                        i = after
                        continue
                    j = close + 1
                after = j
            begin_tag = r'\begin{' + env + '}'
            end_tag = r'\end{' + env + '}'
            # A nested matrix of the SAME env type (e.g. a pmatrix inside a
            # pmatrix) means the first \end{env} found after `after` is the
            # INNER matrix's closer, not this block's -- naively using it
            # truncates the outer block and leaves its real tail ("\\ f & g
            # \end{pmatrix}") dangling as unrelated trailing text. Track
            # nesting depth of same-named \begin/\end pairs so the match
            # here is always the one that actually closes this \begin.
            depth = 1
            search_from = after
            end_idx = -1
            while True:
                next_end = latex.find(end_tag, search_from)
                if next_end == -1:
                    break
                next_begin = latex.find(begin_tag, search_from)
                if next_begin != -1 and next_begin < next_end:
                    depth += 1
                    search_from = next_begin + len(begin_tag)
                    continue
                depth -= 1
                if depth == 0:
                    end_idx = next_end
                    break
                search_from = next_end + len(end_tag)
            if end_idx == -1:
                i = after
                continue
            block_end = end_idx + len(end_tag)
            raw_content = latex[after:end_idx]
            cleaned_content, gap_markers = XMindBuilder._extract_line_commands(raw_content)
            blocks.append({
                'start': start, 'end': block_end,
                'env': env, 'content': cleaned_content, 'gap_markers': gap_markers,
            })
            i = block_end
        return blocks

    _CLINE_RE = re.compile(r'\\cline\s*\{\s*(\d+)\s*-\s*(\d+)\s*\}')

    @staticmethod
    def _extract_line_commands(content: str):
        """Scan `content` for top-level \\hline / \\cline{a-b} tokens (only
        at brace/environment depth 0 -- i.e. not inside a nested cell) and
        pull them out, recording which row-gap each belongs to (gap 0 =
        above row 0, gap i = between row i-1 and row i, gap N = below the
        last row). \\hline/\\cline aren't real mathtext commands, so left
        in place they used to fall through to the generic cell renderer
        and get defanged into visible literal text ("hline", "cline12")
        instead of ever being drawn as an actual rule.

        Returns (content_with_tokens_removed, gap_markers) where
        gap_markers maps gap_index -> list of ('hline',) / ('cline', a, b)
        tuples (a/b are 1-indexed, inclusive column numbers)."""
        out = []
        gap_markers: Dict[int, list] = {}
        gap = 0
        i, n, depth = 0, len(content), 0
        while i < n:
            if content.startswith(r'\begin{', i) or content.startswith(r'\end{', i):
                is_begin = content.startswith(r'\begin{', i)
                close = content.find('}', i)
                if close == -1:
                    out.append(content[i]); i += 1
                    continue
                depth += 1 if is_begin else -1
                out.append(content[i:close + 1])
                i = close + 1
                continue
            ch = content[i]
            if ch in '{([':
                depth += 1; out.append(ch); i += 1
                continue
            if ch in '})]':
                depth -= 1; out.append(ch); i += 1
                continue
            if depth == 0 and content.startswith(r'\hline', i):
                gap_markers.setdefault(gap, []).append(('hline',))
                i += len(r'\hline')
                continue
            if depth == 0 and content.startswith(r'\cline', i):
                m = XMindBuilder._CLINE_RE.match(content, i)
                if m:
                    gap_markers.setdefault(gap, []).append(('cline', int(m.group(1)), int(m.group(2))))
                    i = m.end()
                    continue
            if depth == 0 and ch == '\\':
                j = i
                while j < n and content[j] == '\\':
                    j += 1
                run_len = j - i
                next_ch = content[j] if j < n else ''
                is_sep = (run_len >= 2 and not next_ch.isalpha()) or \
                         (run_len == 1 and next_ch in ('', ' ', '\t', '\r', '\n', '&'))
                if is_sep:
                    gap += 1
                    out.append(content[i:j])
                    i = j
                    continue
            out.append(ch); i += 1
        return ''.join(out), gap_markers

    @staticmethod
    def _split_matrix_rows(content: str) -> List[str]:
        """Split matrix content into rows on a top-level row separator
        (not nested inside {}, (), [], or a nested \\begin{...}\\end{...}
        environment -- e.g. a matrix placed inside another matrix's cell).

        A run of backslashes only counts as a row separator when it is NOT
        the leading backslash of a command -- i.e. not immediately
        followed by a letter. That keeps a doubled command backslash like
        '\\frac' or '\\end' (a common copy/paste artifact) glued to its
        content instead of being sheared off as a fake line break. A lone
        stray '\' immediately followed by whitespace or '&' is also
        accepted as a separator, to tolerate the equally common typo of a
        single backslash where '\\' was meant."""
        rows, current, depth, i, n = [], [], 0, 0, len(content)
        while i < n:
            if content.startswith(r'\begin{', i) or content.startswith(r'\end{', i):
                is_begin = content.startswith(r'\begin{', i)
                tag_start = i
                close = content.find('}', i)
                if close == -1:
                    current.append(content[i]); i += 1
                    continue
                depth += 1 if is_begin else -1
                current.append(content[tag_start:close + 1])
                i = close + 1
                continue
            ch = content[i]
            if ch in '{([':
                depth += 1
                current.append(ch); i += 1
            elif ch in '})]':
                depth -= 1
                current.append(ch); i += 1
            elif ch == '\\' and depth == 0:
                j = i
                while j < n and content[j] == '\\':
                    j += 1
                run_len = j - i
                next_ch = content[j] if j < n else ''
                is_sep = (run_len >= 2 and not next_ch.isalpha()) or \
                         (run_len == 1 and next_ch in ('', ' ', '\t', '\r', '\n', '&'))
                if is_sep:
                    rows.append(''.join(current))
                    current = []
                    i = j
                else:
                    current.append(ch); i += 1
            else:
                current.append(ch); i += 1
        rows.append(''.join(current))
        return [r for r in rows if r.strip()]

    @staticmethod
    def _split_matrix_cells(row: str) -> List[str]:
        """Split a single matrix row into cells on top-level `&` (not
        nested inside {}, (), [], or a nested \\begin{...}\\end{...}
        environment)."""
        cells, current, depth, i, n = [], [], 0, 0, len(row)
        while i < n:
            if row.startswith(r'\begin{', i) or row.startswith(r'\end{', i):
                is_begin = row.startswith(r'\begin{', i)
                tag_start = i
                close = row.find('}', i)
                if close == -1:
                    current.append(row[i]); i += 1
                    continue
                depth += 1 if is_begin else -1
                current.append(row[tag_start:close + 1])
                i = close + 1
                continue
            ch = row[i]
            if ch in '{([':
                depth += 1
                current.append(ch); i += 1
            elif ch in '})]':
                depth -= 1
                current.append(ch); i += 1
            elif ch == '&' and depth == 0:
                cells.append(''.join(current).strip())
                current = []
                i += 1
            else:
                current.append(ch); i += 1
        cells.append(''.join(current).strip())
        return cells

    @staticmethod
    def _render_cell_image(text: str, fontsize: int, text_color: str, dpi: int) -> Image.Image:
        """Render a single piece of LaTeX (a matrix cell, or a plain-text
        segment next to a matrix) as a tightly-cropped, transparent-background
        RGBA image, so it can be composited into a larger layout."""
        text = text.strip()
        if not text:
            text = r'\,'
        fig, ax = plt.subplots(figsize=(0.1, 0.1), dpi=dpi)
        fig.patch.set_alpha(0)
        ax.set_facecolor((0, 0, 0, 0))
        ax.axis('off')
        safe_text = XMindBuilder._safe_mathtext_line(text, fontsize, dpi)
        ax.text(0.5, 0.5, safe_text, fontsize=fontsize, ha='center', va='center',
                 color=text_color, transform=ax.transAxes)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.04,
                    transparent=True, dpi=dpi)
        plt.close(fig)
        buf.seek(0)
        return Image.open(buf).convert('RGBA')

    # --------------------------------------------------------------
    # Unicode text (CJK / Hangul / etc.) rendering.
    #
    # matplotlib mathtext draws \mathrm{}/\text{} content with its bundled
    # DejaVu Sans font, which has no CJK, Hangul, or various other-script
    # glyphs. Those characters silently degrade to a mathtext "dummy
    # symbol" tofu box (the "Font 'rm' does not have a glyph for ..."
    # warnings). The methods below detect that case and render just that
    # text with a real Unicode-capable system font instead, via the same
    # piece-by-piece compositing _build_line_image already uses for
    # matrix blocks.
    # --------------------------------------------------------------

    # Common system fonts with broad CJK/Hangul coverage, checked in order.
    # Not every machine has all of these installed; _find_unicode_font_path
    # skips any that don't exist and just uses the first one that does.
    _UNICODE_FONT_CANDIDATES = [
        # Windows
        r"C:\Windows\Fonts\msyh.ttc",        # Microsoft YaHei (Simplified Chinese)
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\meiryo.ttc",      # Meiryo (Japanese)
        r"C:\Windows\Fonts\YuGothM.ttc",     # Yu Gothic (Japanese)
        r"C:\Windows\Fonts\msgothic.ttc",    # MS Gothic (Japanese)
        r"C:\Windows\Fonts\malgun.ttf",      # Malgun Gothic (Korean)
        r"C:\Windows\Fonts\simsun.ttc",      # SimSun (Simplified Chinese)
        r"C:\Windows\Fonts\mingliu.ttc",     # MingLiU (Traditional Chinese)
        r"C:\Windows\Fonts\arialuni.ttf",    # Arial Unicode MS, if installed
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        # Linux (common CJK font packages)
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
    ]

    _dejavu_cmap_cache = None  # sentinel: None-not-yet-computed vs set()/None-unavailable
    _dejavu_cmap_computed = False
    _unicode_font_cmap_cache: Dict[str, Optional[set]] = {}
    _unicode_font_obj_cache: Dict[tuple, Any] = {}

    @staticmethod
    def _dejavu_sans_cmap() -> Optional[set]:
        """Character coverage of the DejaVu Sans font mathtext's 'rm'
        family uses to draw \\mathrm{}/\\text{} content. Computed once and
        cached; returns None if it can't be determined (in which case
        callers treat everything as covered, i.e. no-op)."""
        if XMindBuilder._dejavu_cmap_computed:
            return XMindBuilder._dejavu_cmap_cache
        XMindBuilder._dejavu_cmap_computed = True
        try:
            from fontTools.ttLib import TTFont
            font_path = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf', 'DejaVuSans.ttf')
            tt = TTFont(font_path, lazy=True)
            XMindBuilder._dejavu_cmap_cache = set(tt.getBestCmap().keys())
        except Exception:
            XMindBuilder._dejavu_cmap_cache = None
        return XMindBuilder._dejavu_cmap_cache

    @staticmethod
    def _needs_custom_font(text: str) -> bool:
        """True if `text` contains a character mathtext's 'rm' font has no
        glyph for (e.g. CJK ideographs, Hiragana/Katakana, Hangul)."""
        cmap = XMindBuilder._dejavu_sans_cmap()
        if cmap is None:
            return False
        return any((not ch.isspace()) and ord(ch) not in cmap for ch in text)

    @staticmethod
    def _font_cmap(path: str) -> Optional[set]:
        if path in XMindBuilder._unicode_font_cmap_cache:
            return XMindBuilder._unicode_font_cmap_cache[path]
        cmap = None
        try:
            from fontTools.ttLib import TTFont
            tt = TTFont(path, fontNumber=0, lazy=True) if path.lower().endswith(('.ttc', '.otc')) else TTFont(path, lazy=True)
            cmap = set(tt.getBestCmap().keys())
        except Exception:
            cmap = None
        XMindBuilder._unicode_font_cmap_cache[path] = cmap
        return cmap

    @staticmethod
    def _find_unicode_font_path(text: str) -> Optional[str]:
        needed = {ord(c) for c in text if not c.isspace()}
        first_installed = None
        if needed:
            for path in XMindBuilder._UNICODE_FONT_CANDIDATES:
                if not os.path.isfile(path):
                    continue
                if first_installed is None:
                    first_installed = path
                cmap = XMindBuilder._font_cmap(path)
                if cmap is not None and needed.issubset(cmap):
                    return path
        # No candidate covers every character (or we couldn't check) --
        # fall back to the first installed font anyway, so most of the
        # text still renders correctly instead of none of it.
        return first_installed

    @staticmethod
    def _load_unicode_font(text: str, px_size: int):
        path = XMindBuilder._find_unicode_font_path(text)
        if path is None:
            return None
        key = (path, px_size)
        if key not in XMindBuilder._unicode_font_obj_cache:
            try:
                XMindBuilder._unicode_font_obj_cache[key] = ImageFont.truetype(path, px_size, index=0)
            except Exception:
                XMindBuilder._unicode_font_obj_cache[key] = None
        return XMindBuilder._unicode_font_obj_cache[key]

    @staticmethod
    def _render_unicode_text_image(text: str, fontsize: int, text_color: str, dpi: int) -> Image.Image:
        """Render a plain-text segment with a real Unicode-capable font
        instead of mathtext, for scripts mathtext's bundled font can't
        draw. Falls back to the normal mathtext cell renderer (same tofu
        degradation as before) if no suitable system font is installed."""
        text = text.strip()
        if not text:
            text = ' '
        px_size = max(8, int(fontsize * dpi / 72))
        font = XMindBuilder._load_unicode_font(text, px_size)
        if font is None:
            print(f"[Equation Warning] no Unicode-capable font found on this system to render '{text}' — it may show as a placeholder glyph")
            return XMindBuilder._render_cell_image(r'\mathrm{' + text + '}', fontsize, text_color, dpi)
        try:
            rgb_color = ImageColor.getrgb(text_color)
        except ValueError:
            rgb_color = (0, 0, 0)
        tmp = Image.new('RGBA', (10, 10), (0, 0, 0, 0))
        bbox = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=font)
        pad = 2
        w = max(1, bbox[2] - bbox[0]) + pad * 2
        h = max(1, bbox[3] - bbox[1]) + pad * 2
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=rgb_color + (255,))
        return img

    @staticmethod
    def _render_cell_image_smart(text: str, fontsize: int, text_color: str, dpi: int) -> Image.Image:
        """Like _render_cell_image, but first checks whether `text` itself
        needs recursive handling -- either a nested matrix environment
        (a matrix placed inside another matrix's cell) or a \\mathrm{} run
        needing a real Unicode font. Both cases route through
        _build_line_image, which already knows how to find and render
        both kinds of block; a cell with neither falls back to the plain
        mathtext cell renderer as before."""
        composite = XMindBuilder._build_line_image(text, fontsize, text_color, dpi)
        if composite is not None:
            return composite
        return XMindBuilder._render_cell_image(text, fontsize, text_color, dpi)

    @staticmethod
    def _find_unicode_text_blocks(latex: str) -> List[Dict[str, Any]]:
        """Find \\mathrm{...} spans (balanced-brace) whose content needs a
        custom font, so _build_line_image can route just those spans to
        _render_unicode_text_image instead of mathtext."""
        blocks = []
        marker = r'\mathrm{'
        i = 0
        while True:
            idx = latex.find(marker, i)
            if idx == -1:
                break
            open_brace = idx + len(marker) - 1
            close = EquationNormalizer._find_matching_brace(latex, open_brace)
            if close == -1:
                i = idx + len(marker)
                continue
            content = latex[open_brace + 1:close]
            if XMindBuilder._needs_custom_font(content):
                blocks.append({'start': idx, 'end': close + 1, 'content': content})
            i = close + 1
        return blocks

    # \xrightarrow{over} / \xrightarrow[under]{over} and the \xleftarrow
    # equivalents (amsmath's extensible arrows). Matplotlib mathtext has
    # no support for these at all (confirmed: it raises "Unknown symbol"
    # even after the backslash survives normalize()), so -- like the
    # matrix-grid environments -- they get a dedicated hand-drawn
    # renderer instead of ever being handed to mathtext.
    _XARROW_CMD_RE = re.compile(r'\\x(right|left)arrow\b')

    @staticmethod
    def _find_xarrow_blocks(latex: str) -> List[Dict[str, Any]]:
        """Find \\x(right|left)arrow spans, with their optional [under]
        and required {over} labels (balanced-brace parsed so nested
        content like \\xrightarrow{\\mathrm{combustion}} works)."""
        blocks = []
        i, n = 0, len(latex)
        while i < n:
            m = XMindBuilder._XARROW_CMD_RE.search(latex, i)
            if not m:
                break
            direction = m.group(1)
            start = m.start()
            j = m.end()
            under_text = ''
            if j < n and latex[j] == '[':
                close = latex.find(']', j)
                if close != -1:
                    under_text = latex[j + 1:close]
                    j = close + 1
            k = j
            while k < n and latex[k] in ' \t':
                k += 1
            over_text = ''
            end = j
            if k < n and latex[k] == '{':
                close = EquationNormalizer._find_matching_brace(latex, k)
                if close != -1:
                    over_text = latex[k + 1:close]
                    end = close + 1
            blocks.append({
                'start': start, 'end': end,
                'direction': direction, 'over': over_text, 'under': under_text,
            })
            i = max(end, m.end())
        return blocks

    @staticmethod
    def _render_xarrow_image(direction: str, over_text: str, under_text: str,
                              fontsize: int, text_color: str, dpi: int) -> 'Image.Image':
        """Hand-draw an extensible arrow with an optional label above
        and/or below, sized to comfortably fit whichever label is wider."""
        label_fontsize = max(8, int(fontsize * 0.72))
        over_img = XMindBuilder._render_cell_image_smart(over_text, label_fontsize, text_color, dpi) \
            if over_text.strip() else None
        under_img = XMindBuilder._render_cell_image_smart(under_text, label_fontsize, text_color, dpi) \
            if under_text.strip() else None

        try:
            rgb_color = ImageColor.getrgb(text_color)
        except ValueError:
            rgb_color = (0, 0, 0)

        min_shaft_w = max(int(dpi * 0.45), int(fontsize * dpi / 72 * 1.4))
        label_w = max((over_img.width if over_img else 0), (under_img.width if under_img else 0))
        shaft_w = max(min_shaft_w, label_w + int(dpi * 0.06))
        head_w = max(8, int(dpi * 0.11))
        head_h = max(8, int(dpi * 0.15))
        shaft_thick = max(2, int(dpi * 0.025))
        pad = max(2, int(dpi * 0.03))

        top_h = (over_img.height + pad) if over_img else 0
        bot_h = (under_img.height + pad) if under_img else 0
        arrow_row_h = max(shaft_thick, head_h)
        total_h = top_h + arrow_row_h + bot_h

        img = Image.new('RGBA', (shaft_w, total_h), (0, 0, 0, 0))
        if over_img:
            img.alpha_composite(over_img, ((shaft_w - over_img.width) // 2, 0))
        draw = ImageDraw.Draw(img)
        ay = top_h + arrow_row_h // 2
        if direction == 'right':
            draw.line([(2, ay), (shaft_w - head_w - 1, ay)], fill=rgb_color, width=shaft_thick)
            draw.polygon([(shaft_w - head_w, ay - head_h // 2),
                          (shaft_w - 2, ay),
                          (shaft_w - head_w, ay + head_h // 2)], fill=rgb_color)
        else:
            draw.line([(head_w + 1, ay), (shaft_w - 2, ay)], fill=rgb_color, width=shaft_thick)
            draw.polygon([(head_w, ay - head_h // 2),
                          (2, ay),
                          (head_w, ay + head_h // 2)], fill=rgb_color)
        if under_img:
            img.alpha_composite(under_img, ((shaft_w - under_img.width) // 2, top_h + arrow_row_h))
        return img

    # \overbrace{expr}^{label} / \underbrace{expr}_{label} (label optional),
    # \boxed{expr}, \cancel{expr}, \bcancel{expr}, \cancelto{value}{expr} --
    # none of these are mathtext commands at all (confirmed: every one of
    # them raises a hard "Unknown symbol" even in their bare, label-less
    # form), so -- like the matrix environments and extensible arrows --
    # they get dedicated hand-drawn renderers instead of ever reaching
    # mathtext.
    _DECO_CMD_RE = re.compile(r'\\(overbrace|underbrace|boxed|cancelto|bcancel|cancel|underline)\b')

    @staticmethod
    def _find_deco_blocks(latex: str) -> List[Dict[str, Any]]:
        """Find \\overbrace/\\underbrace/\\boxed/\\cancel/\\bcancel/\\cancelto
        spans, balanced-brace parsing their argument(s) and -- for
        overbrace/underbrace -- an optional trailing ^{label} / _{label}."""
        blocks = []
        i, n = 0, len(latex)
        while i < n:
            m = XMindBuilder._DECO_CMD_RE.search(latex, i)
            if not m:
                break
            kind = m.group(1)
            start = m.start()
            j = m.end()
            nargs = 2 if kind == 'cancelto' else 1
            args, end = EquationNormalizer._consume_braced_args(latex, j, nargs)
            if len(args) != nargs:
                i = m.end()
                continue
            label, label_side = '', None
            if kind in ('overbrace', 'underbrace'):
                k = end
                while k < n and latex[k] in ' \t':
                    k += 1
                if k < n and latex[k] in ('^', '_'):
                    side = latex[k]
                    k2 = k + 1
                    while k2 < n and latex[k2] in ' \t':
                        k2 += 1
                    if k2 < n and latex[k2] == '{':
                        close = EquationNormalizer._find_matching_brace(latex, k2)
                        if close != -1:
                            label = latex[k2 + 1:close]
                            label_side = side
                            end = close + 1
            blocks.append({'start': start, 'end': end, 'kind': kind, 'args': args,
                            'label': label, 'label_side': label_side})
            i = end
        return blocks

    @staticmethod
    def _draw_horizontal_brace(draw: 'ImageDraw.ImageDraw', x0: int, y0: int,
                                w: int, h: int, point_down: bool, thickness: int, color) -> None:
        """Draw a horizontal over/underbrace across width w -- the same
        normalized-parameter curve technique as the vertical braces in
        _draw_delim, rotated 90 degrees, with a small central tick where
        the two halves meet."""
        n = max(12, int(w / 6))
        pts = []
        for i in range(n + 1):
            t = i / n
            peak = max(0.0, 1 - abs(2 * t - 1))
            depth = peak ** 1.6
            x = x0 + w * t
            y = y0 + (h * depth if point_down else h * (1 - depth))
            pts.append((x, y))
        draw.line(pts, fill=color, width=thickness, joint='curve')
        mid_x = x0 + w / 2
        tick_y = y0 + (h * 0.98 if point_down else h * 0.02)
        draw.line([(mid_x - w * 0.015, tick_y), (mid_x + w * 0.015, tick_y)], fill=color, width=thickness)

    @staticmethod
    def _render_brace_deco_image(direction: str, expr_text: str, label_text: str,
                                  fontsize: int, text_color: str, dpi: int) -> 'Image.Image':
        inner = XMindBuilder._render_cell_image_smart(expr_text, fontsize, text_color, dpi)
        try:
            rgb_color = ImageColor.getrgb(text_color)
        except ValueError:
            rgb_color = (0, 0, 0)
        thickness = max(2, int(dpi * 0.02))
        brace_h = max(8, int(dpi * 0.14))
        gap = max(2, int(dpi * 0.025))
        label_img = None
        if label_text.strip():
            label_img = XMindBuilder._render_cell_image_smart(
                label_text, max(8, int(fontsize * 0.68)), text_color, dpi)

        w = max(inner.width, label_img.width if label_img else 0) + gap * 2
        label_block_h = (label_img.height + gap) if label_img else 0
        h = inner.height + gap + brace_h + label_block_h
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        brace_x = (w - inner.width) // 2

        if direction == 'under':
            img.alpha_composite(inner, ((w - inner.width) // 2, 0))
            by = inner.height + gap
            draw = ImageDraw.Draw(img)
            XMindBuilder._draw_horizontal_brace(draw, brace_x, by, inner.width, brace_h, True, thickness, rgb_color)
            if label_img:
                img.alpha_composite(label_img, ((w - label_img.width) // 2, by + brace_h + gap))
        else:
            by = 0
            if label_img:
                img.alpha_composite(label_img, ((w - label_img.width) // 2, 0))
                by = label_img.height + gap
            draw = ImageDraw.Draw(img)
            XMindBuilder._draw_horizontal_brace(draw, brace_x, by, inner.width, brace_h, False, thickness, rgb_color)
            img.alpha_composite(inner, ((w - inner.width) // 2, by + brace_h + gap))
        return img

    @staticmethod
    def _render_underline_image(expr_text: str, fontsize: int, text_color: str, dpi: int) -> 'Image.Image':
        inner = XMindBuilder._render_cell_image_smart(expr_text, fontsize, text_color, dpi)
        pad = max(3, int(dpi * 0.03))
        thickness = max(2, int(dpi * 0.018))
        w, h = inner.width, inner.height + pad + thickness
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        img.alpha_composite(inner, (0, 0))
        try:
            rgb_color = ImageColor.getrgb(text_color)
        except ValueError:
            rgb_color = (0, 0, 0)
        draw = ImageDraw.Draw(img)
        y = inner.height + pad
        draw.line([(0, y), (w, y)], fill=rgb_color, width=thickness)
        return img

    @staticmethod
    def _render_boxed_image(expr_text: str, fontsize: int, text_color: str, dpi: int) -> 'Image.Image':
        inner = XMindBuilder._render_cell_image_smart(expr_text, fontsize, text_color, dpi)
        pad = max(6, int(dpi * 0.1))
        thickness = max(2, int(dpi * 0.02))
        w, h = inner.width + pad * 2, inner.height + pad * 2
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        img.alpha_composite(inner, (pad, pad))
        try:
            rgb_color = ImageColor.getrgb(text_color)
        except ValueError:
            rgb_color = (0, 0, 0)
        draw = ImageDraw.Draw(img)
        half = max(1, thickness // 2)
        draw.rectangle([half, half, w - 1 - half, h - 1 - half], outline=rgb_color, width=thickness)
        return img

    @staticmethod
    def _render_cancel_image(kind: str, expr_text: str, value_text: str,
                              fontsize: int, text_color: str, dpi: int) -> 'Image.Image':
        inner = XMindBuilder._render_cell_image_smart(expr_text, fontsize, text_color, dpi)
        try:
            rgb_color = ImageColor.getrgb(text_color)
        except ValueError:
            rgb_color = (0, 0, 0)
        thickness = max(2, int(dpi * 0.018))
        margin = max(4, int(dpi * 0.05))
        extra = max(20, int(dpi * 0.3)) if kind == 'cancelto' else 0

        w = inner.width + margin * 2 + extra
        h = inner.height + margin * 2 + extra
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ox = margin
        oy = margin + (extra if kind == 'cancelto' else 0)
        img.alpha_composite(inner, (ox, oy))
        draw = ImageDraw.Draw(img)

        if kind == 'bcancel':
            draw.line([(ox, oy), (ox + inner.width, oy + inner.height)], fill=rgb_color, width=thickness)
        else:
            x0, y0 = ox, oy + inner.height
            x1, y1 = ox + inner.width, oy
            if kind == 'cancelto':
                x1 += extra
                y1 -= extra
            draw.line([(x0, y0), (x1, y1)], fill=rgb_color, width=thickness)
            if kind == 'cancelto':
                import math
                dx, dy = x1 - x0, y1 - y0
                length = math.hypot(dx, dy) or 1
                ux, uy = dx / length, dy / length
                px, py = -uy, ux
                head = max(6, int(dpi * 0.09))
                back_x, back_y = x1 - ux * head, y1 - uy * head
                p1 = (back_x + px * head * 0.5, back_y + py * head * 0.5)
                p2 = (back_x - px * head * 0.5, back_y - py * head * 0.5)
                draw.polygon([(x1, y1), p1, p2], fill=rgb_color)
                if value_text.strip():
                    val_img = XMindBuilder._render_cell_image_smart(
                        value_text, max(8, int(fontsize * 0.6)), text_color, dpi)
                    vx = min(max(0, int(x1 - val_img.width // 2)), w - val_img.width)
                    vy = min(max(0, int(y1 - val_img.height)), h - val_img.height)
                    img.alpha_composite(val_img, (vx, vy))
        return img

    @staticmethod
    def _draw_delim(draw: 'ImageDraw.ImageDraw', char: str, x0: int, y0: int,
                     w: int, h: int, thickness: int, color) -> None:
        """Hand-draw a single delimiter glyph (one of '(', ')', '[', ']',
        '|', '\u2016' (double bar), '{', '}') stretched to span the given
        box, since matplotlib mathtext glyphs don't stretch to arbitrary
        matrix heights.

        '(' / ')' / '{' / '}' are drawn as a curve parameterized by a
        normalized t = y / h in [0, 1], rather than a single fixed-angle
        arc spanning the whole box. An arc's curvature flattens out --
        becomes visually a near-straight line -- as height grows much
        larger than width (e.g. a matrix whose own cells are matrices,
        making it far taller than a normal one), which made these
        brackets nearly invisible on tall content even though something
        was technically being drawn. Driving the curve off a fraction of
        the height instead keeps the same visible bulge no matter how
        tall the box is.
        """
        import math
        if char in ('(', ')'):
            n = max(12, int(h / 6))
            pts = []
            for i in range(n + 1):
                t = i / n
                bulge = math.sin(math.pi * t)  # 0 at both ends, 1 at the middle
                x = x0 + w * ((1 - bulge) if char == '(' else bulge)
                y = y0 + h * t
                pts.append((x, y))
            draw.line(pts, fill=color, width=thickness, joint='curve')
        elif char == '[':
            draw.line([(x0 + w * 0.6, y0), (x0 + w * 0.2, y0)], fill=color, width=thickness)
            draw.line([(x0 + w * 0.2, y0), (x0 + w * 0.2, y0 + h)], fill=color, width=thickness)
            draw.line([(x0 + w * 0.2, y0 + h), (x0 + w * 0.6, y0 + h)], fill=color, width=thickness)
        elif char == ']':
            draw.line([(x0 + w * 0.4, y0), (x0 + w * 0.8, y0)], fill=color, width=thickness)
            draw.line([(x0 + w * 0.8, y0), (x0 + w * 0.8, y0 + h)], fill=color, width=thickness)
            draw.line([(x0 + w * 0.8, y0 + h), (x0 + w * 0.4, y0 + h)], fill=color, width=thickness)
        elif char == '|':
            draw.line([(x0 + w * 0.5, y0), (x0 + w * 0.5, y0 + h)], fill=color, width=thickness)
        elif char == '\u2016':
            # Vmatrix's double vertical bar (norm notation) -- two plain
            # bars, close together, spanning the box like '|' does.
            gap = max(2, int(w * 0.26))
            cx = x0 + w * 0.5
            draw.line([(cx - gap / 2, y0), (cx - gap / 2, y0 + h)], fill=color, width=thickness)
            draw.line([(cx + gap / 2, y0), (cx + gap / 2, y0 + h)], fill=color, width=thickness)
        elif char in ('{', '}'):
            n = max(12, int(h / 6))
            pts = []
            for i in range(n + 1):
                t = i / n
                # A brace's belly pulls in sharply right at the middle
                # (t=0.5) and stays close to the outer edge everywhere
                # else, unlike a paren's single smooth curve -- approximate
                # that with a peaked function of t.
                peak = max(0.0, 1 - abs(2 * t - 1))
                bulge = peak ** 1.6
                x = x0 + w * ((1 - 0.75 * bulge) if char == '{' else (0.25 + 0.75 * bulge))
                y = y0 + h * t
                pts.append((x, y))
            draw.line(pts, fill=color, width=thickness, joint='curve')
            # small tick (the brace's central "spike") at the very middle
            mid = y0 + h / 2
            tick_x = x0 + (w * 0.02 if char == '{' else w * 0.98)
            draw.line([(tick_x, mid - h * 0.015), (tick_x, mid + h * 0.015)], fill=color, width=thickness)

    @staticmethod
    def _parse_multicolumn(cell_text: str):
        """If `cell_text` (one already-split-out matrix cell) is a
        \\multicolumn{n}{align}{content} entry, return (n, content) so the
        grid renderer can treat it as a single cell spanning n columns
        instead of leaving the literal \\multicolumn command text to be
        defanged into visible plain text. Returns None for an ordinary
        cell."""
        s = cell_text.strip()
        if not s.startswith(r'\multicolumn'):
            return None
        args, _ = EquationNormalizer._consume_braced_args(s, len(r'\multicolumn'), 3)
        if len(args) != 3:
            return None
        try:
            n = int(args[0].strip())
        except ValueError:
            return None
        return max(1, n), args[2]

    @staticmethod
    def _render_matrix_image(rows_cells: List[List[str]], env: str, fontsize: int,
                              text_color: str, dpi: int,
                              outer_left=_NO_OVERRIDE, outer_right=_NO_OVERRIDE,
                              line_markers: Optional[Dict[int, list]] = None) -> Image.Image:
        """Lay real per-cell content out into a grid image and draw the
        correct delimiters (parens/brackets/bars/braces) for the matrix
        type -- unlike the old fixed-placeholder behavior, two matrices
        with different contents now produce different images.

        outer_left/outer_right are for the separate case where the whole
        environment is additionally wrapped in an explicit \\left<delim>
        ... \\right<delim> in the source (see
        _extend_matrix_block_with_left_right) -- e.g. an evaluation bar
        around a pmatrix. In real LaTeX \\left/\\right is an independent
        delimiter layer from whatever the environment itself draws, so a
        pmatrix keeps its own parens either way; outer_left/outer_right
        (None for an explicit invisible \\left./\\right., or the sentinel
        _NO_OVERRIDE meaning no such wrap was present at all) add a
        second bracket layer around the whole matrix rather than
        replacing its own."""
        # smallmatrix is LaTeX's compact, inline variant (rendered at
        # \scriptstyle size with tighter spacing) -- shrink its cell font
        # and padding to match instead of drawing it at full matrix size.
        is_small = (env == 'smallmatrix')
        cell_fontsize = max(6, int(fontsize * 0.68)) if is_small else fontsize

        # Unwrap any \multicolumn{n}{align}{content} cell into a real
        # spanning entry (col_start, span, rendered image) instead of
        # leaving it as one literal cell whose \multicolumn command text
        # would otherwise reach the cell renderer unrendered.
        expanded_rows = []
        for row in rows_cells:
            erow = []
            for cell in row:
                mc = XMindBuilder._parse_multicolumn(cell)
                erow.append(mc if mc else (1, cell))
            expanded_rows.append(erow)

        n_rows = len(expanded_rows)
        n_cols = max((sum(span for span, _ in row) for row in expanded_rows), default=1)

        cell_entries = []  # list of rows; each entry: {'col_start','span','img'}
        for row in expanded_rows:
            col_cursor = 0
            erow = []
            for span, text in row:
                img = XMindBuilder._render_cell_image_smart(text, cell_fontsize, text_color, dpi)
                erow.append({'col_start': col_cursor, 'span': max(1, min(span, n_cols)), 'img': img})
                col_cursor += span
            cell_entries.append(erow)

        cell_pad_x = max(2, int(dpi * (0.05 if is_small else 0.12)))
        cell_pad_y = max(2, int(dpi * (0.03 if is_small else 0.08)))

        # Column widths come from single-span (span == 1) cells only. A
        # column that's only ever covered by a spanning cell (never has
        # its own single-span cell in any row) gets a small fallback
        # width here, widened below if a spanning cell needs more room.
        min_col_w = max(10, int(dpi * 0.15))
        col_widths = [min_col_w] * n_cols
        for erow in cell_entries:
            for entry in erow:
                if entry['span'] == 1:
                    j = entry['col_start']
                    col_widths[j] = max(col_widths[j], entry['img'].width)
        for erow in cell_entries:
            for entry in erow:
                if entry['span'] > 1:
                    j0, span = entry['col_start'], entry['span']
                    combined = sum(col_widths[j0:j0 + span]) + cell_pad_x * (span - 1)
                    if entry['img'].width > combined:
                        col_widths[j0 + span - 1] += entry['img'].width - combined

        row_heights = [max((e['img'].height for e in erow), default=1) for erow in cell_entries]
        grid_w = sum(col_widths) + cell_pad_x * (n_cols + 1)
        grid_h = sum(row_heights) + cell_pad_y * (n_rows + 1)

        col_lefts, col_rights = [], []
        cx0 = cell_pad_x
        for j in range(n_cols):
            col_lefts.append(cx0)
            col_rights.append(cx0 + col_widths[j])
            cx0 += col_widths[j] + cell_pad_x

        grid_img = Image.new('RGBA', (grid_w, grid_h), (0, 0, 0, 0))
        row_tops, row_bottoms = [], []
        y = cell_pad_y
        for i, erow in enumerate(cell_entries):
            row_tops.append(y)
            for entry in erow:
                j0, span, img = entry['col_start'], entry['span'], entry['img']
                region_left = col_lefts[j0]
                region_right = col_rights[j0 + span - 1]
                cx = region_left + (region_right - region_left - img.width) // 2
                cy = y + (row_heights[i] - img.height) // 2
                grid_img.alpha_composite(img, (cx, cy))
            row_bottoms.append(y + row_heights[i])
            y += row_heights[i] + cell_pad_y

        try:
            rgb_color = ImageColor.getrgb(text_color)
        except ValueError:
            rgb_color = (0, 0, 0)
        thickness = max(2, int(dpi * 0.02))

        # \hline / \cline: draw them as real horizontal rules across the
        # grid instead of leaving them as stray, unrenderable command
        # text. line_markers maps a row-gap index (0 = above row 0, i =
        # between row i-1 and i, n_rows = below the last row) to a list
        # of ('hline',) / ('cline', a, b) tuples extracted from the
        # source by _extract_line_commands.
        if line_markers:
            line_draw = ImageDraw.Draw(grid_img)
            line_thickness = max(1, int(dpi * 0.012))
            for gap_idx, markers in line_markers.items():
                if gap_idx <= 0:
                    ly = line_thickness
                elif gap_idx >= n_rows:
                    ly = grid_h - line_thickness
                else:
                    ly = (row_bottoms[gap_idx - 1] + row_tops[gap_idx]) / 2
                for marker in markers:
                    if marker[0] == 'hline':
                        line_draw.line([(0, ly), (grid_w, ly)], fill=rgb_color, width=line_thickness)
                    elif marker[0] == 'cline':
                        _, a, b = marker
                        a = max(1, min(a, n_cols))
                        b = max(1, min(b, n_cols))
                        if a > b:
                            a, b = b, a
                        lx0 = col_lefts[a - 1] - cell_pad_x * 0.3
                        lx1 = col_rights[b - 1] + cell_pad_x * 0.3
                        line_draw.line([(lx0, ly), (lx1, ly)], fill=rgb_color, width=line_thickness)

        # Layer 1: the environment's own inherent delimiter (pmatrix's
        # parens, bmatrix's brackets, etc; matrix/array have none).
        delim_map = {
            'pmatrix': ('(', ')'), 'bmatrix': ('[', ']'), 'vmatrix': ('|', '|'),
            'Vmatrix': ('\u2016', '\u2016'),
            'Bmatrix': ('{', '}'), 'matrix': (None, None), 'array': (None, None),
            'cases': ('{', None), 'smallmatrix': (None, None),
        }
        left, right = delim_map.get(env, (None, None))
        bracket_w = max(6, int(dpi * 0.3)) if (left or right) else 0
        total_w = grid_w + (bracket_w if left else 0) + (bracket_w if right else 0)
        core = Image.new('RGBA', (total_w, grid_h), (0, 0, 0, 0))
        offset_x = bracket_w if left else 0
        core.alpha_composite(grid_img, (offset_x, 0))
        draw = ImageDraw.Draw(core)
        if left:
            XMindBuilder._draw_delim(draw, left, 0, 0, bracket_w, grid_h, thickness, rgb_color)
        if right:
            XMindBuilder._draw_delim(draw, right, offset_x + grid_w, 0, bracket_w, grid_h, thickness, rgb_color)

        # Layer 2: an outer \left...\right wrap, if the source had one --
        # independent of layer 1, so e.g. a pmatrix keeps its own parens
        # AND gets an extra bar drawn outside them for "\right|_{x=0}".
        has_outer_wrap = not (outer_left is XMindBuilder._NO_OVERRIDE and outer_right is XMindBuilder._NO_OVERRIDE)
        if not has_outer_wrap:
            return core
        o_left = None if outer_left is XMindBuilder._NO_OVERRIDE else outer_left
        o_right = None if outer_right is XMindBuilder._NO_OVERRIDE else outer_right
        outer_bracket_w = max(6, int(dpi * 0.3)) if (o_left or o_right) else 0
        if outer_bracket_w == 0:
            return core
        outer_total_w = core.width + (outer_bracket_w if o_left else 0) + (outer_bracket_w if o_right else 0)
        final = Image.new('RGBA', (outer_total_w, core.height), (0, 0, 0, 0))
        ox = outer_bracket_w if o_left else 0
        final.alpha_composite(core, (ox, 0))
        draw2 = ImageDraw.Draw(final)
        if o_left:
            XMindBuilder._draw_delim(draw2, o_left, 0, 0, outer_bracket_w, core.height, thickness, rgb_color)
        if o_right:
            XMindBuilder._draw_delim(draw2, o_right, ox + core.width, 0, outer_bracket_w, core.height, thickness, rgb_color)
        return final

    @staticmethod
    def _extend_matrix_block_with_left_right(latex: str, block: Dict[str, Any]) -> Dict[str, Any]:
        """If a matrix-grid block is directly wrapped in \\left<delim> ...
        \\right<delim>, extend the block's start/end to swallow those
        tokens (plus any trailing sub/superscript on \\right, e.g. an
        evaluation bar's \\right|_{x=0}) and record the delimiter
        override so _render_matrix_image draws that delimiter instead of
        the env's default. Without this, "\\left." and "\\right|_{x=0}"
        end up as orphaned text pieces next to the matrix -- each only
        half of a \\left/\\right pair -- which mathtext rejects outright
        since it has no matching counterpart to pair with."""
        block = dict(block)
        prefix = latex[:block['start']]
        lm = XMindBuilder._LEFT_DELIM_RE.search(prefix)
        if lm:
            block['start'] = lm.start()
            block['left_override'] = XMindBuilder._DELIM_TOKEN_TO_CHAR.get(lm.group(1))
        tail = latex[block['end']:]
        rm = XMindBuilder._RIGHT_DELIM_RE.match(tail)
        if rm:
            consumed = rm.end()
            block['right_override'] = XMindBuilder._DELIM_TOKEN_TO_CHAR.get(rm.group(1))
            sm = XMindBuilder._RIGHT_SUFFIX_RE.match(tail[consumed:])
            if sm:
                block['right_suffix'] = sm.group(0)
                consumed += sm.end()
            block['end'] = block['end'] + consumed
        return block

    @staticmethod
    def _build_line_image(latex: str, fontsize: int, text_color: str, dpi: int) -> Optional['Image.Image']:
        """If `latex` contains one or more matrix-grid environments, build
        the whole line as a composite of plain-mathtext segments and real
        matrix-grid images placed side by side, and return it as a plain
        (transparent-background, unencoded) PIL Image. Returns None if no
        matrix-grid environment is present, so callers can fall back to
        their own handling of plain lines."""
        matrix_blocks = XMindBuilder._find_matrix_blocks(latex)
        matrix_blocks = [XMindBuilder._extend_matrix_block_with_left_right(latex, b) for b in matrix_blocks]
        unicode_blocks = XMindBuilder._find_unicode_text_blocks(latex)
        xarrow_blocks = XMindBuilder._find_xarrow_blocks(latex)
        deco_blocks = XMindBuilder._find_deco_blocks(latex)

        all_blocks = (
            [dict(b, _kind='matrix') for b in matrix_blocks] +
            [dict(b, _kind='unicode') for b in unicode_blocks] +
            [dict(b, _kind='xarrow') for b in xarrow_blocks] +
            [dict(b, _kind='deco') for b in deco_blocks]
        )

        # Drop any block fully contained within another block's span --
        # e.g. a \xrightarrow{} or a nested matrix sitting inside a
        # \boxed{}'s argument, or a matrix cell containing a \cancel{}.
        # Whichever block contains the other renders its own
        # argument/cell text recursively (via _render_cell_image_smart ->
        # _build_line_image), so the contained block doesn't need --  and
        # must not get -- a second, separate top-level cut here.
        def _contains(outer, inner):
            return outer is not inner and outer['start'] <= inner['start'] and inner['end'] <= outer['end']

        blocks = sorted(
            [b for b in all_blocks if not any(_contains(o, b) for o in all_blocks)],
            key=lambda b: b['start'],
        )
        if not blocks:
            return None

        segments = []
        cursor = 0
        for b in blocks:
            if b['start'] > cursor:
                plain = latex[cursor:b['start']]
                if plain.strip():
                    segments.append(('text', plain))
            segments.append((b['_kind'], b))
            cursor = b['end']
        if cursor < len(latex):
            plain = latex[cursor:]
            if plain.strip():
                segments.append(('text', plain))
        if not segments:
            return None

        piece_images = []
        for kind, val in segments:
            if kind == 'text':
                piece_images.append(XMindBuilder._render_cell_image(val, fontsize, text_color, dpi))
            elif kind == 'unicode':
                piece_images.append(XMindBuilder._render_unicode_text_image(val['content'], fontsize, text_color, dpi))
            elif kind == 'xarrow':
                piece_images.append(XMindBuilder._render_xarrow_image(
                    val['direction'], val['over'], val['under'], fontsize, text_color, dpi))
            elif kind == 'deco':
                dkind = val['kind']
                if dkind in ('overbrace', 'underbrace'):
                    direction = 'under' if dkind == 'underbrace' else 'over'
                    piece_images.append(XMindBuilder._render_brace_deco_image(
                        direction, val['args'][0], val['label'], fontsize, text_color, dpi))
                elif dkind == 'boxed':
                    piece_images.append(XMindBuilder._render_boxed_image(
                        val['args'][0], fontsize, text_color, dpi))
                elif dkind == 'underline':
                    piece_images.append(XMindBuilder._render_underline_image(
                        val['args'][0], fontsize, text_color, dpi))
                else:  # cancel / bcancel / cancelto
                    expr = val['args'][-1]
                    value = val['args'][0] if dkind == 'cancelto' else ''
                    piece_images.append(XMindBuilder._render_cancel_image(
                        dkind, expr, value, fontsize, text_color, dpi))
            else:
                rows = XMindBuilder._split_matrix_rows(val['content'])
                if not rows:
                    rows = ['']
                rows_cells = [XMindBuilder._split_matrix_cells(r) for r in rows]
                mat_img = XMindBuilder._render_matrix_image(
                    rows_cells, val['env'], fontsize, text_color, dpi,
                    outer_left=val.get('left_override', XMindBuilder._NO_OVERRIDE),
                    outer_right=val.get('right_override', XMindBuilder._NO_OVERRIDE),
                    line_markers=val.get('gap_markers'),
                )
                suffix = val.get('right_suffix')
                if suffix:
                    # An evaluation bar's trailing sub/superscript (e.g.
                    # \right|_{x=0}) has no base of its own to attach to
                    # once the matrix is drawn separately -- mathtext
                    # requires *something* before a bare _/^. An empty
                    # group "{}" supplies an invisible one.
                    suf_img = XMindBuilder._render_cell_image_smart(
                        '{}' + suffix, max(10, int(fontsize * 0.75)), text_color, dpi)
                    combo_h = max(mat_img.height, suf_img.height)
                    combo = Image.new('RGBA', (mat_img.width + suf_img.width, combo_h), (0, 0, 0, 0))
                    combo.alpha_composite(mat_img, (0, (combo_h - mat_img.height) // 2))
                    combo.alpha_composite(suf_img, (mat_img.width, combo_h - suf_img.height))
                    piece_images.append(combo)
                else:
                    piece_images.append(mat_img)

        pad = max(4, int(dpi * 0.06))
        total_w = sum(im.width for im in piece_images) + pad * (len(piece_images) - 1)
        total_h = max(im.height for im in piece_images)
        combo = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
        x = 0
        for im in piece_images:
            y = (total_h - im.height) // 2
            combo.alpha_composite(im, (x, y))
            x += im.width + pad
        return combo

    @staticmethod
    def _render_line_composite(latex: str, fontsize: int, text_color: str,
                                bg_color: str, fmt: str, dpi: int) -> Optional[bytes]:
        """If `latex` contains one or more matrix-grid environments, render
        the whole line as a composite of plain-mathtext segments and
        real matrix-grid images placed side by side. Returns None (so the
        caller falls back to the normal mathtext path) if no matrix-grid
        environment is present."""
        combo = XMindBuilder._build_line_image(latex, fontsize, text_color, dpi)
        if combo is None:
            return None

        is_jpeg = fmt.lower() in ("jpg", "jpeg")
        if bg_color == "none" and not is_jpeg:
            final_img = combo
        else:
            fill_color = bg_color if bg_color != "none" else "#ffffff"
            try:
                bg_rgb = ImageColor.getrgb(fill_color)
            except ValueError:
                bg_rgb = (255, 255, 255)
            bg = Image.new('RGBA', combo.size, bg_rgb + (255,))
            bg.alpha_composite(combo)
            final_img = bg
        if is_jpeg and final_img.mode != "RGB":
            final_img = final_img.convert("RGB")

        buf = io.BytesIO()
        save_fmt = "JPEG" if is_jpeg else fmt.upper()
        final_img.save(buf, format=save_fmt)
        buf.seek(0)
        return buf.read()

    @staticmethod
    def _collapse_matrix_placeholders(eq: str) -> str:
        """The OLD normalize()-era behavior of throwing away matrix content
        and replacing it with a fixed placeholder string. No longer used
        during normal rendering -- kept only as a last-resort,
        exception-safety fallback if the real grid renderer above ever
        raises on some pathological input."""
        env_replacements = [
            (r'\\begin\{pmatrix\}.*?\\end\{pmatrix\}', r'\\left( \cdots \\right)'),
            (r'\\begin\{bmatrix\}.*?\\end\{bmatrix\}', r'\\left[ \cdots \\right]'),
            (r'\\begin\{vmatrix\}.*?\\end\{vmatrix\}', r'\\left| \cdots \\right|'),
            (r'\\begin\{Bmatrix\}.*?\\end\{Bmatrix\}', r'\\left\{ \cdots \\right\}'),
            (r'\\begin\{matrix\}.*?\\end\{matrix\}', r'\\left[ \cdots \\right]'),
            (r'\\begin\{array\}(\[.*?\])?\{.*?\}.*?\\end\{array\}', r'\\mathrm{array}'),
            (r'\\begin\{cases\}.*?\\end\{cases\}', r'\\mathrm{cases}'),
        ]
        for pattern, replacement in env_replacements:
            eq = re.sub(pattern, lambda m: replacement, eq, flags=re.DOTALL)
        eq = re.sub(
            r'\\begin\{(\w+?)\}.*?\\end\{\1\}',
            lambda m: r'\mathrm{' + m.group(1) + '}',
            eq, flags=re.DOTALL,
        )
        return eq

    def _resolve_colors(self, level: int, inline: Optional[Dict[str, str]]) -> Dict[str, Any]:
        idx = (level - 1) % len(self.level_colors)
        default = self.level_colors[idx]
        mode = self.color_mode[idx] if idx < len(self.color_mode) else "fallback"
        if mode == "overwrite":
            return default.copy()
        elif mode == "fallback":
            result = default.copy()
            if inline:
                for key, val in inline.items():
                    if val and val.strip():
                        result[key] = val
            return result
        else:
            if inline:
                return {k: v for k, v in inline.items() if v and v.strip()}
            return {}

    def _make_topic(self, title: str, note: Optional[str] = None,
                    labels: Optional[List[str]] = None,
                    children: Optional[List[Dict]] = None,
                    level: int = 0, is_root: bool = False,
                    custom_colors: Optional[Dict[str, Any]] = None,
                    equation: Optional[str] = None,
                    eq_width: int = 200, eq_height: int = 100,
                    eq_color: str = "black", eq_bg: str = "#ffffff",
                    eq_font: int = 50,
                    img_fmt: str = None) -> Dict[str, Any]:
        if img_fmt is None:
            img_fmt = self.default_img_fmt

        # Apply safety caps
        if eq_width > MAX_EQ_WIDTH:
            eq_width = MAX_EQ_WIDTH
        if eq_height > MAX_EQ_HEIGHT:
            eq_height = MAX_EQ_HEIGHT
        if eq_font > MAX_EQ_FONT:
            eq_font = MAX_EQ_FONT

        topic = {
            "id": self.uid(),
            "class": "topic",
            "title": title,
        }
        if labels:
            topic["labels"] = labels
        if note is not None and note != "":
            topic["notes"] = {
                "plain": {"content": note + "\n"},
                "realHTML": {"content": "<div>" + note + "</div>"}
            }
        if children:
            topic["children"] = {"attached": children}

        colors = self._resolve_colors(level, custom_colors)
        props = {}

        font_size = colors.get("font_size", max(10, 20 - level))
        if isinstance(font_size, str):
            font_size = int(font_size) if font_size.isdigit() else 14
        props["fo:font-size"] = f"{font_size}pt"

        line_width_val = colors.get("line_width", 1)
        if isinstance(line_width_val, str):
            line_width_val = int(line_width_val) if line_width_val.isdigit() else 1
        line_width_pt = WIDTH_TO_PT.get(line_width_val, "1pt")

        border_width_val = colors.get("border_width", 2)
        if isinstance(border_width_val, str):
            border_width_val = int(border_width_val) if border_width_val.isdigit() else 2
        border_width_pt = WIDTH_TO_PT.get(border_width_val, "1pt")

        fill_color = self._hex_with_opacity(colors.get("fill"), colors.get("fill_opacity", 100))
        if fill_color:
            props["svg:fill"] = fill_color
            props["fill-pattern"] = "solid"
        if colors.get("text"):
            props["fo:color"] = colors["text"]

        border_color = self._hex_with_opacity(colors.get("border"), colors.get("border_opacity", 100))
        if border_color:
            props["border-line-color"] = border_color
        elif fill_color:
            props["border-line-color"] = fill_color
        props["border-line-width"] = border_width_pt
        props["border-line-pattern"] = "solid"

        line_color = self._hex_with_opacity(colors.get("line"), colors.get("line_opacity", 100))
        if line_color:
            props["line-color"] = line_color
            props["line-width"] = line_width_pt
        elif fill_color:
            props["line-color"] = fill_color
            props["line-width"] = line_width_pt

        branch_shape_label = colors.get("branch_shape", "Rounded")
        branch_shape_value = BRANCH_SHAPE_VALUES.get(branch_shape_label, "org.xmind.branchConnection.curve")
        props["line-class"] = branch_shape_value

        node_shape_label = colors.get("node_shape", "Rounded Rect")
        node_shape_value = NODE_SHAPE_VALUES.get(node_shape_label, "org.xmind.topicShape.roundedRect")

        if is_root:
            props["fo:font-weight"] = "bold"
            props["shape-class"] = node_shape_value
            topic["structureClass"] = self.layout
        else:
            props["shape-class"] = node_shape_value

        # ── Equation embedding ──
        if equation:
            if eq_width == 200 and eq_height == 100:
                auto_w, auto_h, auto_font = EquationNormalizer.auto_size(equation)
                eq_width = auto_w
                eq_height = auto_h
                if eq_font == 50:
                    eq_font = auto_font

            if self.eq_override_flags.get('color', False) and self.eq_design.get('eq_color'):
                eq_color = self.eq_design['eq_color']
            if self.eq_override_flags.get('bg', False) and self.eq_design.get('eq_bg'):
                eq_bg = self.eq_design['eq_bg']
            if self.eq_override_flags.get('w', False) and self.eq_design.get('eq_w'):
                eq_width = self.eq_design['eq_w']
            if self.eq_override_flags.get('h', False) and self.eq_design.get('eq_h'):
                eq_height = self.eq_design['eq_h']
            if self.eq_override_flags.get('font', False) and self.eq_design.get('eq_font'):
                eq_font = self.eq_design['eq_font']
            if self.eq_override_flags.get('fmt', False) and self.eq_design.get('eq_fmt'):
                img_fmt = self.eq_design['eq_fmt']

            try:
                img_id = self.uid()
                ext = img_fmt if img_fmt in IMAGE_FORMATS else "jpg"
                img_filename = f"resources/{img_id}.{ext}"
                img_bytes = self.render_equation(equation, text_color=eq_color, bg_color=eq_bg, fmt=img_fmt,
                                                 fontsize=eq_font, width=eq_width, height=eq_height)
                topic["image"] = {"src": f"xap:{img_filename}", "width": eq_width, "height": eq_height}
                topic["__img_filename"] = img_filename
                topic["__img_bytes"] = img_bytes
            except Exception as e:
                print(f"[Equation Render Error] {equation}: {e}")
                try:
                    img_id = self.uid()
                    ext = "png"
                    img_filename = f"resources/{img_id}.{ext}"
                    img_bytes = self._render_equation_fallback(equation, eq_font, eq_color, eq_bg, "png", 150)
                    topic["image"] = {"src": f"xap:{img_filename}", "width": eq_width, "height": eq_height}
                    topic["__img_filename"] = img_filename
                    topic["__img_bytes"] = img_bytes
                except Exception as e2:
                    print(f"[Fallback render also failed: {e2}]")
                    topic["title"] = f"{title} [EQ ERROR]"

        if props:
            topic["style"] = {"id": self.uid(), "properties": props}
        return topic

    def _build_theme(self) -> Dict[str, Any]:
        l0 = self.level_colors[0] if self.level_colors else DEFAULT_LEVEL_PALETTE[0]
        l1 = self.level_colors[1] if len(self.level_colors) > 1 else DEFAULT_LEVEL_PALETTE[1]
        l2 = self.level_colors[2] if len(self.level_colors) > 2 else DEFAULT_LEVEL_PALETTE[2]

        def get_pt(val, default_key):
            v = val.get(default_key, 2) if isinstance(val, dict) else 2
            if isinstance(v, str):
                v = int(v) if v.isdigit() else 2
            return WIDTH_TO_PT.get(v, "1pt")

        def get_fs(val, default_key):
            v = val.get(default_key, 14) if isinstance(val, dict) else 14
            if isinstance(v, str):
                v = int(v) if v.isdigit() else 14
            return f"{v}pt"

        def get_branch(val):
            return BRANCH_SHAPE_VALUES.get(val.get("branch_shape", "Rounded"), "org.xmind.branchConnection.roundedElbow")

        def get_node(val):
            return NODE_SHAPE_VALUES.get(val.get("node_shape", "Rounded Rect"), "org.xmind.topicShape.roundedRect")

        return {
            "map": {"id": self.uid(), "properties": {"svg:fill": self.map_bg}},
            "centralTopic": {
                "id": self.uid(),
                "properties": {
                    "svg:fill": self._hex_with_opacity(l0.get("fill", "#e63946"), l0.get("fill_opacity", 100)),
                    "fill-pattern": "solid",
                    "fo:color": l0.get("text", "#ffffff"),
                    "fo:font-size": get_fs(l0, "font_size"),
                    "fo:font-weight": "bold",
                    "border-line-color": self._hex_with_opacity(l0.get("border", l0.get("fill", "#e63946")), l0.get("border_opacity", 100)),
                    "border-line-width": get_pt(l0, "border_width"),
                    "border-line-pattern": "solid",
                    "line-color": self._hex_with_opacity(l0.get("line", "#e63946"), l0.get("line_opacity", 100)),
                    "line-width": get_pt(l0, "line_width"),
                    "line-class": get_branch(l0),
                    "shape-class": get_node(l0)
                }
            },
            "mainTopic": {
                "id": self.uid(),
                "properties": {
                    "svg:fill": self._hex_with_opacity(l1.get("fill", "#457b9d"), l1.get("fill_opacity", 100)),
                    "fill-pattern": "solid",
                    "fo:color": l1.get("text", "#ffffff"),
                    "fo:font-size": get_fs(l1, "font_size"),
                    "border-line-color": self._hex_with_opacity(l1.get("border", l1.get("fill", "#457b9d")), l1.get("border_opacity", 100)),
                    "border-line-width": get_pt(l1, "border_width"),
                    "border-line-pattern": "solid",
                    "line-color": self._hex_with_opacity(l1.get("line", "#457b9d"), l1.get("line_opacity", 100)),
                    "line-width": get_pt(l1, "line_width"),
                    "line-class": get_branch(l1),
                    "shape-class": get_node(l1)
                }
            },
            "subTopic": {
                "id": self.uid(),
                "properties": {
                    "svg:fill": self._hex_with_opacity(l2.get("fill", "#a8dadc"), l2.get("fill_opacity", 100)),
                    "fill-pattern": "solid",
                    "fo:color": l2.get("text", "#1d3557"),
                    "fo:font-size": get_fs(l2, "font_size"),
                    "border-line-color": self._hex_with_opacity(l2.get("border", l2.get("fill", "#a8dadc")), l2.get("border_opacity", 100)),
                    "border-line-width": get_pt(l2, "border_width"),
                    "border-line-pattern": "solid",
                    "line-color": self._hex_with_opacity(l2.get("line", "#a8dadc"), l2.get("line_opacity", 100)),
                    "line-width": get_pt(l2, "line_width"),
                    "line-class": get_branch(l2),
                    "shape-class": get_node(l2)
                }
            }
        }

    @staticmethod
    def _hex_with_opacity(hex_color: Optional[str], opacity_pct: Any) -> Optional[str]:
        if not hex_color:
            return hex_color
        try:
            op = int(opacity_pct) if opacity_pct is not None else 100
        except (ValueError, TypeError):
            return hex_color
        if op >= 100:
            return hex_color
        if not re.match(r'^#[0-9a-fA-F]{6}$', hex_color):
            return hex_color
        alpha = int(op * 255 / 100)
        return f"{hex_color}{alpha:02X}"

    def collect_images(self, t: Dict, images: Optional[Dict] = None) -> Dict:
        if images is None:
            images = {}
        if "__img_filename" in t:
            images[t.pop("__img_filename")] = t.pop("__img_bytes")
        for child in t.get("children", {}).get("attached", []):
            self.collect_images(child, images)
        return images

    def build(self, root_node: Dict[str, Any]) -> bytes:
        img_data = root_node.get("image_data") or {}
        root = self._make_topic(
            title=root_node["title"],
            note=root_node.get("note"),
            labels=root_node.get("labels"),
            children=root_node.get("children"),
            level=1,
            is_root=True,
            custom_colors=root_node.get("colors"),
            equation=img_data.get("equation"),
            eq_width=img_data.get("eq_w", 200),
            eq_height=img_data.get("eq_h", 100),
            eq_color=img_data.get("eq_color", "black"),
            eq_bg=img_data.get("eq_bg", "#ffffff"),
            eq_font=img_data.get("eq_font", 50),
            img_fmt=img_data.get("img_fmt")
        )
        theme = self._build_theme()
        content = [{
            "id": self.uid(),
            "class": "sheet",
            "title": self.title,
            "rootTopic": root,
            "theme": theme
        }]
        images = self.collect_images(root)
        file_entries = {"content.json": {}, "metadata.json": {}}
        for filepath in images:
            file_entries[filepath] = {}
        manifest = {"file-entries": file_entries}

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("content.json", json.dumps(content, ensure_ascii=False, indent=2))
            zf.writestr("metadata.json", '{"creator":{"name":"XMind","version":"23.07.202307032151"}}')
            zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            for filepath, data in images.items():
                zf.writestr(filepath, data)
        return buf.getvalue()

# ============================================================
# HierarchyParser
# ============================================================
class HierarchyParser:
    def __init__(self, text: str):
        self.text = text
        self.entries: List[Dict[str, Any]] = []

    @staticmethod
    def _parse_brace(raw: Optional[str]) -> tuple[Optional[str], List[str], Dict[str, str], Dict[str, Any]]:
        if not raw:
            return None, [], {}, {}
        note = None
        labels: List[str] = []
        colors = {}
        image_data: Dict[str, Any] = {}

        for pat in [r'note\s*:\s*"((?:\\.|[^"\\])*)"', r"note\s*:\s*'((?:\\.|[^'\\])*)'"]:
            m = re.search(pat, raw, re.IGNORECASE)
            if m:
                note = m.group(1).replace(r'\"', '"').replace(r"\'", "'")
                break
        if note is None:
            m = re.search(r'note\s*:\s*([^,}]+)', raw, re.IGNORECASE)
            if m:
                note = m.group(1).strip()

        m = re.search(r'label\s*:\s*"([^"]*)"', raw, re.IGNORECASE)
        if m:
            labels = [l.strip() for l in m.group(1).split(",") if l.strip()]

        for key in ("fill", "text", "line", "border"):
            pat = rf'{key}\s*:\s*"(#[0-9a-fA-F]{{6}})"'
            m = re.search(pat, raw, re.IGNORECASE)
            if m:
                colors[key] = m.group(1)

        eq = EquationNormalizer.extract(raw)
        if eq:
            image_data["equation"] = EquationNormalizer.normalize(eq)

        for key in ("eq_w", "eq_h", "eq_font"):
            pat = rf'{key}\s*:\s*(\d+)'
            m = re.search(pat, raw, re.IGNORECASE)
            if m:
                image_data[key] = int(m.group(1))

        m = re.search(r'eq_color\s*:\s*"([^"]*)"', raw, re.IGNORECASE)
        if m:
            image_data["eq_color"] = m.group(1)
        else:
            m = re.search(r'eq_color\s*:\s*(#[0-9a-fA-F]{6})', raw, re.IGNORECASE)
            if m:
                image_data["eq_color"] = m.group(1)

        m = re.search(r'eq_bg\s*:\s*"([^"]*)"', raw, re.IGNORECASE)
        if m:
            image_data["eq_bg"] = m.group(1)
        else:
            m = re.search(r'eq_bg\s*:\s*(#[0-9a-fA-F]{6}|none)', raw, re.IGNORECASE)
            if m:
                image_data["eq_bg"] = m.group(1)

        m = re.search(r'img_fmt\s*:\s*"?(\w+)"?', raw, re.IGNORECASE)
        if m:
            fmt = m.group(1).lower()
            if fmt == 'jpeg':
                fmt = 'jpg'
            if fmt in IMAGE_FORMATS:
                image_data["img_fmt"] = fmt
        else:
            image_data["img_fmt"] = None

        return note, labels, colors, image_data

    def _split_entries(self) -> List[str]:
        raw_entries = []
        current = ""
        brace_depth = 0
        for char in self.text:
            if char == "{":
                brace_depth += 1
                current += char
            elif char == "}":
                brace_depth -= 1
                current += char
            elif char == "\n" and brace_depth == 0:
                if current.strip():
                    raw_entries.append(current.strip())
                current = ""
            else:
                current += char
        if current.strip():
            raw_entries.append(current.strip())
        return raw_entries

    def parse(self) -> List[Dict[str, Any]]:
        raw_entries = self._split_entries()
        for raw in raw_entries:
            prefixes = []
            remaining = raw
            while True:
                m = re.match(r'^lvl(\d+)\[(\d+)\]', remaining, re.IGNORECASE)
                if not m:
                    break
                level = int(m.group(1))
                index = int(m.group(2))
                prefixes.append((level, index))
                remaining = remaining[m.end():]

            if not prefixes:
                continue

            actual_level, actual_index = prefixes[-1]

            title_match = re.match(r'^\s*(.*?)(?:\{(.*)\})?$', remaining, re.DOTALL)
            if not title_match:
                continue
            title = title_match.group(1).strip()
            brace = title_match.group(2)

            note, labels, colors, image_data = self._parse_brace(brace)
            if title:
                self.entries.append({
                    "level": actual_level,
                    "index": actual_index,
                    "title": title,
                    "note": note,
                    "labels": labels if labels else None,
                    "colors": colors if colors else None,
                    "image_data": image_data if image_data else None
                })
        return self.entries

    def build_tree(self) -> Optional[Dict[str, Any]]:
        entries = self.parse()
        if not entries:
            return None
        if entries[0]["level"] != 1 or entries[0]["index"] != 1:
            raise ValueError("First entry must be lvl1[1] -- it becomes the root node.")

        first = entries[0]
        root = {
            "title": first["title"],
            "note": first.get("note"),
            "labels": first.get("labels"),
            "colors": first.get("colors"),
            "image_data": first.get("image_data"),
            "children": []
        }

        last_at_level: Dict[int, Any] = {1: root}

        for entry in entries[1:]:
            level = entry["level"]
            node = {
                "title": entry["title"],
                "note": entry.get("note"),
                "labels": entry.get("labels"),
                "colors": entry.get("colors"),
                "image_data": entry.get("image_data"),
                "children": []
            }

            if level == 1:
                root["children"].append(node)
                last_at_level[1] = node
            else:
                parent_level = level - 1
                if parent_level in last_at_level:
                    parent = last_at_level[parent_level]
                    parent["children"].append(node)
                    last_at_level[level] = node
                else:
                    root["children"].append(node)
                    last_at_level[level] = node

        return root

    def get_max_level(self) -> int:
        entries = self.parse()
        if not entries:
            return 1
        return max(e["level"] for e in entries)

def build_tab_outline(root_node: Dict[str, Any]) -> str:
    lines = []
    def recurse(node: Dict[str, Any], depth: int):
        prefix = "\t" * depth
        lines.append(prefix + node["title"])
        for child in node.get("children", []):
            recurse(child, depth + 1)
    recurse(root_node, 0)
    return "\n".join(lines)

# ============================================================
# convert_to_xmind and build_xmind_bytes
# ============================================================
def convert_to_xmind(input_text: str,
                     output_path: str,
                     layout: str = "org.xmind.ui.map.unbalanced",
                     level_colors: Optional[List[Dict[str, Any]]] = None,
                     color_mode: Optional[List[str]] = None,
                     map_bg: str = DEFAULT_MAP_BG,
                     note_heading: bool = False,
                     default_img_fmt: str = DEFAULT_IMAGE_FMT,
                     eq_override_flags: Optional[Dict[str, bool]] = None,
                     eq_design: Optional[Dict[str, Any]] = None) -> str:
    parser = HierarchyParser(input_text)
    root_node = parser.build_tree()
    if root_node is None:
        raise ValueError("No valid entries found.")

    builder = XMindBuilder(title=root_node["title"], layout=layout,
                          level_colors=level_colors, color_mode=color_mode, map_bg=map_bg,
                          note_heading=note_heading, default_img_fmt=default_img_fmt,
                          eq_override_flags=eq_override_flags, eq_design=eq_design)

    def recurse(nodes: List[Dict], depth: int) -> List[Dict]:
        result = []
        for node in nodes:
            children = recurse(node.get("children", []), depth + 1) if node.get("children") else None
            img_data = node.get("image_data") or {}
            topic = builder._make_topic(
                title=node["title"],
                note=node.get("note"),
                labels=node.get("labels"),
                children=children,
                level=depth,
                is_root=False,
                custom_colors=node.get("colors"),
                equation=img_data.get("equation"),
                eq_width=img_data.get("eq_w", 200),
                eq_height=img_data.get("eq_h", 100),
                eq_color=img_data.get("eq_color", "black"),
                eq_bg=img_data.get("eq_bg", "#ffffff"),
                eq_font=img_data.get("eq_font", 50),
                img_fmt=img_data.get("img_fmt")
            )
            result.append(topic)
        return result

    if root_node.get("children"):
        root_node["children"] = recurse(root_node["children"], depth=2)

    xmind_bytes = builder.build(root_node)
    with open(output_path, "wb") as f:
        f.write(xmind_bytes)
    return os.path.abspath(output_path)

def build_xmind_bytes(input_text: str,
                      layout: str = "org.xmind.ui.map.unbalanced",
                      level_colors: Optional[List[Dict[str, Any]]] = None,
                      color_mode: Optional[List[str]] = None,
                      map_bg: str = DEFAULT_MAP_BG,
                      note_heading: bool = False,
                      default_img_fmt: str = DEFAULT_IMAGE_FMT,
                      eq_override_flags: Optional[Dict[str, bool]] = None,
                      eq_design: Optional[Dict[str, Any]] = None) -> bytes:
    parser = HierarchyParser(input_text)
    root_node = parser.build_tree()
    if root_node is None:
        raise ValueError("No valid entries found.")

    builder = XMindBuilder(title=root_node["title"], layout=layout,
                          level_colors=level_colors, color_mode=color_mode, map_bg=map_bg,
                          note_heading=note_heading, default_img_fmt=default_img_fmt,
                          eq_override_flags=eq_override_flags, eq_design=eq_design)

    def recurse(nodes: List[Dict], depth: int) -> List[Dict]:
        result = []
        for node in nodes:
            children = recurse(node.get("children", []), depth + 1) if node.get("children") else None
            img_data = node.get("image_data") or {}
            topic = builder._make_topic(
                title=node["title"],
                note=node.get("note"),
                labels=node.get("labels"),
                children=children,
                level=depth,
                is_root=False,
                custom_colors=node.get("colors"),
                equation=img_data.get("equation"),
                eq_width=img_data.get("eq_w", 200),
                eq_height=img_data.get("eq_h", 100),
                eq_color=img_data.get("eq_color", "black"),
                eq_bg=img_data.get("eq_bg", "#ffffff"),
                eq_font=img_data.get("eq_font", 50),
                img_fmt=img_data.get("img_fmt")
            )
            result.append(topic)
        return result

    if root_node.get("children"):
        root_node["children"] = recurse(root_node["children"], depth=2)

    return builder.build(root_node)

# ============================================================
# GUI helpers (spinbox mousewheel binding)
# ============================================================
def bind_mousewheel_to_spinbox(spinbox: tk.Spinbox):
    def _on_enter(event):
        spinbox.focus_set()
    def _on_mousewheel(event):
        if spinbox.focus_get() is not spinbox:
            return
        if event.delta > 0:
            spinbox.invoke("buttonup")
        elif event.delta < 0:
            spinbox.invoke("buttondown")
        return "break"
    def _on_linux_scroll_up(event):
        if spinbox.focus_get() is not spinbox:
            return
        spinbox.invoke("buttonup")
        return "break"
    def _on_linux_scroll_down(event):
        if spinbox.focus_get() is not spinbox:
            return
        spinbox.invoke("buttondown")
        return "break"
    spinbox.bind("<Enter>", _on_enter)
    spinbox.bind("<MouseWheel>", _on_mousewheel)
    spinbox.bind("<Button-4>", _on_linux_scroll_up)
    spinbox.bind("<Button-5>", _on_linux_scroll_down)

# ============================================================
# ColorRow
# ============================================================
class ColorRow:
    def __init__(self, parent: tk.Widget, level: int, default: Dict[str, Any],
                 check_var: tk.BooleanVar, theme_colors: Dict[str, str]):
        self.level = level
        self.check_var = check_var
        self.theme = theme_colors
        self.card = tk.Frame(parent, bg=theme_colors["bg"], highlightbackground=theme_colors["accent"],
                             highlightthickness=1)
        self.card.pack(fill=tk.X, pady=2, padx=1)

        row1 = tk.Frame(self.card, bg=theme_colors["bg"])
        row1.pack(fill=tk.X, padx=2, pady=(3, 1))
        self.chk = tk.Checkbutton(row1, variable=self.check_var, width=0,
                                   bg=theme_colors["bg"], activebackground=theme_colors["bg"],
                                   selectcolor=theme_colors["select"])
        self.chk.pack(side=tk.LEFT, padx=(0, 1))
        self.lbl = tk.Label(row1, text=f"{level}", width=4,
                            bg=theme_colors["bg"], fg=theme_colors["fg"],
                            font=("Helvetica", 13, "bold"))
        self.lbl.pack(side=tk.LEFT)

        self.fill_var, self.fill_prev, self.fill_opacity_var = self._make_color_picker(row1, "Fill", default.get("fill", "#e63946"), default.get("fill_opacity", 100), opacity_label="F%")
        self.font_var, self.font_prev = self._make_color_picker(row1, "Font", default.get("text", "#ffffff"), with_opacity=False)

        row2 = tk.Frame(self.card, bg=theme_colors["bg"])
        row2.pack(fill=tk.X, padx=2, pady=(1, 1))
        tk.Label(row2, text="", width=3, bg=theme_colors["bg"]).pack(side=tk.LEFT)
        self.border_var, self.border_prev, self.border_opacity_var = self._make_color_picker(row2, "Border", default.get("border", default.get("fill", "#e63946")), default.get("border_opacity", 100), opacity_label="B%")
        tk.Label(row2, text="B-W", bg=self.theme["bg"], fg=self.theme["fg"],
                 font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(1, 0))
        bw_default = default.get("border_width", 2)
        if isinstance(bw_default, str):
            bw_default = int(bw_default) if bw_default.isdigit() else 2
        self.border_width_var = tk.IntVar(value=bw_default)
        self.border_width_spin = tk.Spinbox(row2, from_=0, to=5, width=3,
                                             textvariable=self.border_width_var,
                                             bg=self.theme["entry_bg"], fg="#000000",
                                             font=("Consolas", 9), relief=tk.SOLID, bd=1)
        self.border_width_spin.pack(side=tk.LEFT, padx=(0, 1))
        bind_mousewheel_to_spinbox(self.border_width_spin)

        tk.Label(row2, text="F-Sz", bg=self.theme["bg"], fg=self.theme["fg"],
                 font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(1, 0))
        fs_default = default.get("font_size", 14)
        if isinstance(fs_default, str):
            fs_default = int(fs_default) if fs_default.isdigit() else 14
        self.font_size_var = tk.IntVar(value=fs_default)
        self.font_size_spin = tk.Spinbox(row2, from_=1, to=200, width=3,
                                          textvariable=self.font_size_var,
                                          bg=self.theme["entry_bg"], fg="#000000",
                                          font=("Consolas", 9), relief=tk.SOLID, bd=1)
        self.font_size_spin.pack(side=tk.LEFT, padx=(0, 1))
        bind_mousewheel_to_spinbox(self.font_size_spin)

        row3 = tk.Frame(self.card, bg=theme_colors["bg"])
        row3.pack(fill=tk.X, padx=2, pady=(1, 1))
        tk.Label(row3, text="", width=3, bg=theme_colors["bg"]).pack(side=tk.LEFT)
        self.line_var, self.line_prev, self.line_opacity_var = self._make_color_picker(row3, "Line", default.get("line", "#e63946"), default.get("line_opacity", 100), opacity_label="L%")
        tk.Label(row3, text="L-W", bg=self.theme["bg"], fg=self.theme["fg"],
                 font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(1, 0))
        lw_default = default.get("line_width", 1)
        if isinstance(lw_default, str):
            lw_default = int(lw_default) if lw_default.isdigit() else 1
        self.line_width_var = tk.IntVar(value=lw_default)
        self.line_width_spin = tk.Spinbox(row3, from_=1, to=5, width=3,
                                           textvariable=self.line_width_var,
                                           bg=self.theme["entry_bg"], fg="#000000",
                                           font=("Consolas", 9), relief=tk.SOLID, bd=1)
        self.line_width_spin.pack(side=tk.LEFT, padx=(0, 1))
        bind_mousewheel_to_spinbox(self.line_width_spin)

        row4 = tk.Frame(self.card, bg=theme_colors["bg"])
        row4.pack(fill=tk.X, padx=2, pady=(1, 3))
        right_container = tk.Frame(row4, bg=theme_colors["bg"])
        right_container.pack(side=tk.RIGHT)

        tk.Label(right_container, text="Branch design", bg=self.theme["bg"], fg=self.theme["fg"],
                 font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(0, 1))
        self.branch_shape_var = tk.StringVar(value=default.get("branch_shape", "Rounded"))
        self.branch_shape_combo = tk.OptionMenu(right_container, self.branch_shape_var, *BRANCH_SHAPE_LABELS)
        self._style_optionmenu(self.branch_shape_combo, self.branch_shape_var, BRANCH_SHAPE_LABELS)
        self.branch_shape_combo.pack(side=tk.LEFT, padx=(0, 6))

        tk.Label(right_container, text="Node design", bg=self.theme["bg"], fg=self.theme["fg"],
                 font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(0, 1))
        self.node_shape_var = tk.StringVar(value=default.get("node_shape", "Rounded Rect"))
        self.node_shape_combo = tk.OptionMenu(right_container, self.node_shape_var, *NODE_SHAPE_LABELS)
        self._style_optionmenu(self.node_shape_combo, self.node_shape_var, NODE_SHAPE_LABELS)
        self.node_shape_combo.pack(side=tk.LEFT, padx=(0, 1))

    def _make_color_picker(self, parent: tk.Frame, name: str, default_val: str, default_opacity: int = 100, with_opacity: bool = True, opacity_label: str = "%"):
        var = tk.StringVar(value=default_val)
        tk.Label(parent, text=name, bg=self.theme["bg"], fg=self.theme["fg"],
                 font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(1, 1))
        ent = tk.Entry(parent, textvariable=var, width=6,
                       bg=self.theme["entry_bg"], fg="#000000",
                       insertbackground="#000000",
                       relief=tk.SOLID, bd=1, font=("Consolas", 9))
        ent.pack(side=tk.LEFT)
        prev = tk.Label(parent, text="", bg=var.get(), relief=tk.RIDGE,
                        width=2, height=1, cursor="hand2")
        prev.pack(side=tk.LEFT, padx=(1, 1))
        prev.bind("<Button-1>", lambda e, v=var, p=prev: self._on_swatch_click(v, p))
        var.trace_add("write", lambda *args, v=var, p=prev: self._update_swatch(v, p))
        opacity_var = None
        if with_opacity:
            opacity_var = tk.IntVar(value=default_opacity)
            tk.Label(parent, text=opacity_label, bg=self.theme["bg"], fg=self.theme["fg"],
                     font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(1, 0))
            opacity_spin = tk.Spinbox(parent, from_=0, to=100, width=3,
                                      textvariable=opacity_var,
                                      bg=self.theme["entry_bg"], fg="#000000",
                                      font=("Consolas", 9), relief=tk.SOLID, bd=1)
            opacity_spin.pack(side=tk.LEFT, padx=(0, 1))
            bind_mousewheel_to_spinbox(opacity_spin)
        if with_opacity:
            return var, prev, opacity_var
        return var, prev

    def _on_swatch_click(self, var: tk.StringVar, prev: tk.Label):
        c = colorchooser.askcolor(color=var.get(), title=f"Level {self.level}")[1]
        if c:
            var.set(c.upper())
            prev.config(bg=c)

    def _update_swatch(self, var: tk.StringVar, prev: tk.Label):
        v = var.get()
        if re.match(r'^#[0-9a-fA-F]{6}$', v):
            prev.config(bg=v)
        elif v == "":
            prev.config(bg="#888888")

    def _style_optionmenu(self, optionmenu, var, options):
        menu = optionmenu["menu"]
        btn_bg = "#00b4d8"
        active_bg = "#00d2ff"
        optionmenu.config(bg=btn_bg, fg="#000000", activebackground=active_bg,
                          relief=tk.FLAT, font=("Helvetica", 8))
        menu.config(bg=self.theme["entry_bg"], fg="#000000",
                    activebackground=active_bg, activeforeground="#000000")
        def _update_highlight(*args):
            current = var.get()
            for i, opt in enumerate(options):
                if opt == current:
                    menu.entryconfig(i, background=btn_bg, foreground="#ffffff")
                else:
                    menu.entryconfig(i, background=self.theme["entry_bg"], foreground="#000000")
        var.trace_add("write", _update_highlight)
        menu.configure(postcommand=lambda: _update_highlight())
        _update_highlight()

    def get(self) -> Dict[str, Any]:
        return {
            "fill":  self.fill_var.get(),
            "fill_opacity": self.fill_opacity_var.get(),
            "text":  self.font_var.get(),
            "line":  self.line_var.get(),
            "line_opacity": self.line_opacity_var.get(),
            "border": self.border_var.get(),
            "border_opacity": self.border_opacity_var.get(),
            "font_size": self.font_size_var.get(),
            "line_width": self.line_width_var.get(),
            "border_width": self.border_width_var.get(),
            "branch_shape": self.branch_shape_var.get(),
            "node_shape": self.node_shape_var.get(),
        }

    def get_mode(self) -> str:
        return "overwrite" if self.check_var.get() else "fallback"

    def update_theme(self, colors: Dict[str, str]):
        self.theme = colors
        self.card.config(bg=colors["bg"], highlightbackground=colors["accent"])
        self.chk.config(bg=colors["bg"], activebackground=colors["bg"], selectcolor=colors["select"])
        self.lbl.config(bg=colors["bg"], fg=colors["fg"])
        for widget in self.card.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(bg=colors["bg"])
                for child in widget.winfo_children():
                    wtype = child.winfo_class()
                    if wtype == "Label":
                        if child not in [self.fill_prev, self.font_prev, self.line_prev, self.border_prev]:
                            child.config(bg=colors["bg"], fg=colors["fg"])
                    elif wtype == "Entry":
                        child.config(bg=colors["entry_bg"], fg="#000000", insertbackground="#000000")
                    elif wtype == "Spinbox":
                        child.config(bg=colors["entry_bg"], fg="#000000", insertbackground="#000000")
                    elif wtype == "Menu":
                        child.config(bg=colors["entry_bg"], fg="#000000",
                                     activebackground="#00d2ff", activeforeground="#000000")
                    elif wtype == "Menubutton":
                        child.config(bg="#00b4d8", fg="#000000",
                                     activebackground="#00d2ff")
        self._style_optionmenu(self.branch_shape_combo, self.branch_shape_var, BRANCH_SHAPE_LABELS)
        self._style_optionmenu(self.node_shape_combo, self.node_shape_var, NODE_SHAPE_LABELS)

# ============================================================
# Canvas Mode Editor (with text wrap and equation popup)
# ============================================================
class CanvasNode:
    def __init__(self, id, text, parent=None):
        self.id = id
        self.text = text
        self.parent = parent
        self.children = []
        self.collapsed = False
        self.note = ""
        self.equation = ""
        self.eq_font = 18
        self.width = 240
        self.height = 70
        self.x = 0
        self.y = 0

class CanvasModeEditor:
    CHART_TYPES = ["Logic Chart"]
    STRUCTURE_TYPES = ["Right"]

    def __init__(self, parent_frame, manual_editor, colors):
        self.parent = parent_frame
        self.manual_editor = manual_editor
        self.colors = colors
        self.active = False

        self.canvas_nodes = {}
        self.canvas_item_to_node = {}
        self.next_canvas_id = 1
        self.selected_canvas_node = None
        self.canvas_zoom = 1.0
        self.canvas_offset_x = 300
        self.canvas_offset_y = 300
        self.panning = False
        self.pan_start = None
        self.dragging = False
        self.drag_start = None

        self.current_chart = "Logic Chart"
        self.level_width = 280
        self.node_spacing = 100
        self.connector_color = "#7a8b9a"
        self.connector_width = 2

        self.editing_node = None
        self.edit_entry = None
        self.edit_rect = None

        self.note_popup = None
        self.note_text_widget = None
        self.note_popup_node = None
        self.is_note_open = False
        self._closing_note = False
        self._note_close_source = None
        self._note_draw_after_id = None

        self.eq_popup = None
        self.eq_text_widget = None
        self.eq_popup_node = None
        self.is_eq_open = False

        self.tooltip = None
        self.tooltip_after_id = None

        self.xbutton1_mode = False
        self.shift_lock = False
        self._shift_pressed = False

        self._build_ui()
        self._setup_bindings()

    # ── UI BUILDING ──
    def _build_ui(self):
        self.frame = tk.Frame(self.parent, bg=self.colors["bg"])

        toolbar = tk.Frame(self.frame, bg=self.colors["bg"])
        toolbar.pack(fill=tk.X, pady=(0, 4))

        tk.Button(toolbar, text="＋ Child", command=self._add_child,
                  bg="#00b894", fg="#ffffff", font=("Helvetica", 8, "bold"),
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="→ Sibling", command=self._add_sibling,
                  bg="#6c5ce7", fg="#ffffff", font=("Helvetica", 8, "bold"),
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="✎ Edit (F2)", command=self._start_inline_edit,
                  bg="#0984e3", fg="#ffffff", font=("Helvetica", 8, "bold"),
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="🗑 Delete", command=self._delete_node,
                  bg="#e74c3c", fg="#ffffff", font=("Helvetica", 8, "bold"),
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📝 Note (F4)", command=self._toggle_note,
                  bg="#fdcb6e", fg="#000000", font=("Helvetica", 8, "bold"),
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="∑ Eq (F3)", command=self._toggle_equation_popup,
                  bg="#00b4d8", fg="#000000", font=("Helvetica", 8, "bold"),
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Toggle ▶/▼", command=self._toggle_collapse,
                  bg=self.colors["btn_bg"], fg="#000000", font=("Helvetica", 8),
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="↺ Reset View", command=self._reset_view,
                  bg=self.colors["btn_bg"], fg="#000000", font=("Helvetica", 8),
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=(8, 2))

        self.canvas = tk.Canvas(self.frame, bg="#1e1e2e", highlightthickness=0,
                                scrollregion=(-200000, -200000, 200000, 200000))
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas_status = tk.Label(self.frame,
            text="Canvas: Click=select | Scroll=pan | F5=ZoomMode | F6=ShiftLock | Dbl-click/F2=edit | F3=eq | F4=note",
            bg=self.colors["bg"], fg="#888888", font=("Helvetica", 8), anchor=tk.W)
        self.canvas_status.pack(fill=tk.X, pady=(2, 0))

    def _setup_bindings(self):
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<B3-Motion>", self._on_right_drag)
        self.canvas.bind("<ButtonRelease-3>", self._on_right_release)
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        self.canvas.bind("<Button-4>", self._on_button4)
        self.canvas.bind("<Button-5>", self._on_button5)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<Shift_L>", lambda e: self._on_shift_press())
        self.canvas.bind("<Shift_R>", lambda e: self._on_shift_press())
        self.canvas.bind("<KeyRelease-Shift_L>", lambda e: self._on_shift_release())
        self.canvas.bind("<KeyRelease-Shift_R>", lambda e: self._on_shift_release())
        self.parent.bind("<Shift_L>", lambda e: self._on_shift_press(), add='+')
        self.parent.bind("<Shift_R>", lambda e: self._on_shift_press(), add='+')
        self.parent.bind("<KeyRelease-Shift_L>", lambda e: self._on_shift_release(), add='+')
        self.parent.bind("<KeyRelease-Shift_R>", lambda e: self._on_shift_release(), add='+')

        self.canvas.bind("<Delete>", lambda e: self._delete_node())
        self.canvas.bind("<F2>", lambda e: self._start_inline_edit())
        self.canvas.bind("<F3>", lambda e: self._toggle_equation_popup())
        self.canvas.bind("<F4>", lambda e: self._toggle_note())
        self.canvas.bind("<Insert>", lambda e: self._add_child())
        self.canvas.bind("<Escape>", lambda e: self._on_escape())
        self.canvas.bind("<Return>", lambda e: self._finish_inline_edit())
        self.canvas.bind("<Up>", lambda e: self._move_selection(0, -1))
        self.canvas.bind("<Down>", lambda e: self._move_selection(0, 1))
        self.canvas.bind("<Left>", lambda e: self._move_selection(-1, 0))
        self.canvas.bind("<Right>", lambda e: self._move_selection(1, 0))
        self.canvas.bind("<F5>", lambda e: self._toggle_mode())
        self.canvas.bind("<F6>", lambda e: self._handle_xbutton2())

    # ── MODE SYSTEM ──
    def _on_button4(self, event):
        if sys.platform == 'win32':
            self._toggle_mode()
            return "break"
        else:
            self._on_scroll_linux(event)

    def _on_button5(self, event):
        if sys.platform == 'win32':
            self._handle_xbutton2()
            return "break"
        else:
            self._on_scroll_linux(event)

    def _setup_xbutton_listener(self):
        if sys.platform != 'win32':
            return
        if hasattr(self, '_hook_id') and self._hook_id:
            try:
                import ctypes
                ctypes.windll.user32.UnhookWindowsHookEx(self._hook_id)
            except Exception:
                pass
            self._hook_id = None
        try:
            import ctypes
            from ctypes import wintypes
            WH_MOUSE_LL = 14
            WM_XBUTTONDOWN = 0x020B
            XBUTTON1 = 0x0001
            XBUTTON2 = 0x0002
            class MSLLHOOKSTRUCT(ctypes.Structure):
                _fields_ = [
                    ("pt", wintypes.POINT),
                    ("mouseData", wintypes.DWORD),
                    ("flags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.c_size_t),
                ]
            self._hook_id = None
            def hook_proc(nCode, wParam, lParam):
                try:
                    if nCode == 0 and wParam == WM_XBUTTONDOWN:
                        lp = ctypes.c_void_p(lParam & 0xFFFFFFFFFFFFFFFF)
                        msll = ctypes.cast(lp, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                        xbtn = (msll.mouseData >> 16) & 0xFFFF
                        if xbtn == XBUTTON1:
                            self.parent.after(0, self._toggle_mode)
                            return 1
                        elif xbtn == XBUTTON2:
                            self.parent.after(0, self._handle_xbutton2)
                            return 1
                except Exception:
                    pass
                # Fix 64-bit signed/unsigned LPARAM overflow
                lp_fixed = lParam & 0xFFFFFFFFFFFFFFFF
                if lp_fixed > 0x7FFFFFFFFFFFFFFF:
                    lp_fixed -= 0x10000000000000000
                return ctypes.windll.user32.CallNextHookEx(0, nCode, wParam, lp_fixed)
            HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)  # FIX: wintypes.LRESULT is missing on Python < 3.12
            self._hook_callback_ref = HOOKPROC(hook_proc)
            self._hook_id = ctypes.windll.user32.SetWindowsHookExW(
                WH_MOUSE_LL, self._hook_callback_ref,
                ctypes.windll.kernel32.GetModuleHandleW(None), 0
            )
            if self._hook_id:
                print(f"[Canvas] XButton hook installed (id={self._hook_id})")
            else:
                print("[Canvas] Failed to install XButton hook, using F5/F6")
        except Exception as e:
            print(f"[Canvas] XButton hook error: {e}, using F5/F6")

    def _remove_xbutton_hook(self):
        if hasattr(self, '_hook_id') and self._hook_id:
            try:
                import ctypes
                ctypes.windll.user32.UnhookWindowsHookEx(self._hook_id)
                self._hook_id = None
                print("[Canvas] XButton hook removed")
            except Exception:
                pass

    def _on_shift_press(self):
        self._shift_pressed = True

    def _on_shift_release(self):
        self._shift_pressed = False

    def _toggle_mode(self):
        self.xbutton1_mode = not self.xbutton1_mode
        mode_str = "ON" if self.xbutton1_mode else "OFF"
        desc = "scroll=zoom, R-drag=joystick, XB2=note" if self.xbutton1_mode else "scroll=vertical, XB2=toggle ShiftLock"
        self._show_tooltip(f"Mode {mode_str}\n{desc}")
        self._update_canvas_status()

    def _handle_xbutton2(self):
        if self.xbutton1_mode:
            self._toggle_note()
        else:
            self.shift_lock = not self.shift_lock
            state = "ON" if self.shift_lock else "OFF"
            self._show_tooltip(f"Shift Lock {state}")
            self._update_canvas_status()

    def _show_tooltip(self, text):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
        if self.tooltip_after_id:
            self.parent.after_cancel(self.tooltip_after_id)
            self.tooltip_after_id = None
        x = self.parent.winfo_pointerx() - self.parent.winfo_rootx()
        y = self.parent.winfo_pointery() - self.parent.winfo_rooty()
        tip = tk.Toplevel(self.parent)
        tip.overrideredirect(True)
        tip.wm_attributes("-topmost", True)
        tip.geometry(f"+{x+15}+{y+10}")
        label = tk.Label(tip, text=text, bg="#ffffcc", relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", 11, "bold"), padx=8, pady=4, justify=tk.CENTER)
        label.pack()
        self.tooltip = tip
        self.tooltip_after_id = self.parent.after(2000, self._hide_tooltip)

    def _hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
        self.tooltip_after_id = None

    def _update_canvas_status(self):
        mode_str = "ON" if self.xbutton1_mode else "OFF"
        if self.xbutton1_mode:
            scroll_info = "scroll=zoom"
            click_info = "LMB=note"
            xb2_info = "XB2=note"
        else:
            lock_str = "ON" if self.shift_lock else "OFF"
            scroll_info = f"scroll=vertical (ShiftLock {lock_str})"
            click_info = "LMB=select"
            xb2_info = "XB2=toggle ShiftLock"
        if self.selected_canvas_node:
            addr = self._get_node_address(self.selected_canvas_node)
            base_text = f"Mode: {mode_str} | {scroll_info} | {click_info} | {xb2_info} | {addr}"
        else:
            base_text = f"Mode: {mode_str} | {scroll_info} | {click_info} | {xb2_info} | Dbl-click=edit | R-drag={'joystick' if self.xbutton1_mode else 'pan'}"
        self.canvas_status.config(text=base_text)

    # ── SYNC ──
    def sync_from_manual(self):
        manual_nodes = self.manual_editor.nodes
        if not manual_nodes:
            self.canvas_nodes.clear()
            self.next_canvas_id = 1
            root = CanvasNode(0, "Root")
            self.canvas_nodes[0] = root
            self.selected_canvas_node = root
            self._auto_layout()
            if self.active:
                self._draw_canvas()
                self._update_scrollregion()
            return

        old_selected_path = None
        if self.selected_canvas_node:
            old_selected_path = self._get_node_address(self.selected_canvas_node)

        self.canvas_nodes.clear()
        self.next_canvas_id = 1
        path_to_node = {}

        for mnode in manual_nodes:
            path_tuple = tuple(tuple(p) for p in mnode["path"])
            cnode = CanvasNode(self.next_canvas_id, mnode.get("heading", ""))
            cnode.note = mnode.get("note", "")
            cnode.equation = mnode.get("equation", "")
            cnode.eq_font = mnode.get("eq_font", 18)
            self.canvas_nodes[self.next_canvas_id] = cnode
            path_to_node[path_tuple] = cnode
            self.next_canvas_id += 1

        for mnode in manual_nodes:
            path_tuple = tuple(tuple(p) for p in mnode["path"])
            cnode = path_to_node.get(path_tuple)
            if not cnode:
                continue
            if len(path_tuple) > 1:
                parent_path = path_tuple[:-1]
                parent = path_to_node.get(parent_path)
                if parent:
                    cnode.parent = parent
                    parent.children.append(cnode)
            else:
                cnode.parent = None

        root = None
        for cnode in self.canvas_nodes.values():
            if cnode.parent is None:
                root = cnode
                break
        if root is None and self.canvas_nodes:
            root = list(self.canvas_nodes.values())[0]
            root.parent = None

        self.selected_canvas_node = root
        if old_selected_path:
            for cnode in self.canvas_nodes.values():
                if self._get_node_address(cnode) == old_selected_path:
                    self.selected_canvas_node = cnode
                    break

        self._auto_layout()
        self._update_scrollregion()
        if self.active:
            self._draw_canvas()

    def sync_to_manual(self):
        self.manual_editor._nodes_before_sync = list(self.manual_editor.nodes)
        root = None
        for cnode in self.canvas_nodes.values():
            if cnode.parent is None:
                root = cnode
                break
        if not root:
            return
        manual_nodes = []
        def recurse(cnode, path, child_idx=1):
            level = len(path) + 1
            idx = child_idx if path else 1
            full_path = path + [(level, idx)]
            manual_nodes.append({
                "path": list(full_path),
                "heading": cnode.text,
                "note": cnode.note,
                "label": "",
                "equation": cnode.equation,
                "eq_w": 260, "eq_h": 70, "eq_font": cnode.eq_font,
            })
            for i, child in enumerate(cnode.children):
                recurse(child, full_path, i + 1)
        recurse(root, [], 1)
        self.manual_editor.nodes = manual_nodes

        old_path = None
        if self.manual_editor.current_node_idx >= 0:
            old_nodes = getattr(self.manual_editor, "_nodes_before_sync", [])
            if old_nodes and self.manual_editor.current_node_idx < len(old_nodes):
                old_path = old_nodes[self.manual_editor.current_node_idx].get("path")
        if old_path:
            for idx, node in enumerate(manual_nodes):
                if node.get("path") == old_path:
                    self.manual_editor.current_node_idx = idx
                    self.manual_editor.path = list(old_path)
                    break
            else:
                parent_path = old_path[:-1] if len(old_path) > 1 else None
                if parent_path:
                    for idx, node in enumerate(manual_nodes):
                        if node.get("path") == parent_path:
                            self.manual_editor.current_node_idx = idx
                            self.manual_editor.path = list(parent_path)
                            break
                    else:
                        self.manual_editor.current_node_idx = 0 if manual_nodes else -1
                        self.manual_editor.path = [(1, 1)]
                else:
                    self.manual_editor.current_node_idx = 0 if manual_nodes else -1
                    self.manual_editor.path = [(1, 1)]
        else:
            self.manual_editor.current_node_idx = 0 if manual_nodes else -1
            self.manual_editor.path = [(1, 1)]

        self.manual_editor._refresh_tree()
        self.manual_editor._update_address_display()
        self.manual_editor._update_field_indicator()

    def sync_text_from_manual(self):
        if not self.manual_editor or not self.canvas_nodes:
            return
        addr_to_canvas = {}
        for cnode in self.canvas_nodes.values():
            addr = self._get_node_address(cnode)
            addr_to_canvas[addr] = cnode
        manual_addrs = set()
        struct_changed = False
        for mnode in self.manual_editor.nodes:
            addr = "".join(f"lvl{lvl}[{idx}]" for lvl, idx in mnode["path"])
            manual_addrs.add(addr)
            if addr in addr_to_canvas:
                cnode = addr_to_canvas[addr]
                cnode.text = mnode.get("heading", "")
                cnode.note = mnode.get("note", "")
                cnode.equation = mnode.get("equation", "")
            else:
                struct_changed = True
        for addr in list(addr_to_canvas.keys()):
            if addr not in manual_addrs:
                struct_changed = True
        if struct_changed:
            self.sync_from_manual()
        elif self.active:
            self._draw_canvas()
            self._update_scrollregion()

    # ── LAYOUT ENGINE ──
    def _auto_layout(self):
        if not self.canvas_nodes:
            return
        root = None
        for n in self.canvas_nodes.values():
            if n.parent is None:
                root = n
                break
        if not root:
            return
        for node in self.canvas_nodes.values():
            node._layout_y = 0
            node._layout_x = 0
            node._subtree_height = 0
            node._leaf_count = 0
        self._compute_subtree_sizes(root)
        self._leaf_counter = 0
        self._assign_leaf_y_positions(root)
        self._center_parents(root)
        self._assign_x_positions(root, 0)
        for node in self.canvas_nodes.values():
            node.y = node._layout_y
            node.x = node._layout_x

    def _compute_subtree_sizes(self, node):
        if node.collapsed or not node.children:
            node._subtree_height = self.node_spacing
            node._leaf_count = 1
            return
        total_height = 0
        total_leaves = 0
        for child in node.children:
            self._compute_subtree_sizes(child)
            total_height += child._subtree_height
            total_leaves += child._leaf_count
        if len(node.children) > 1:
            total_height += (len(node.children) - 1) * (self.node_spacing * 0.5)
        node._subtree_height = max(total_height, self.node_spacing)
        node._leaf_count = max(total_leaves, 1)

    def _assign_leaf_y_positions(self, node):
        if node.collapsed:
            node._layout_y = self._leaf_counter * self.node_spacing
            self._leaf_counter += 1
            return
        if not node.children:
            node._layout_y = self._leaf_counter * self.node_spacing
            self._leaf_counter += 1
            return
        for child in node.children:
            self._assign_leaf_y_positions(child)

    def _center_parents(self, node):
        if node.collapsed or not node.children:
            return
        for child in node.children:
            self._center_parents(child)
        first_child = node.children[0]
        last_child = node.children[-1]
        node._layout_y = (first_child._layout_y + last_child._layout_y) / 2

    def _assign_x_positions(self, node, level):
        node._layout_x = level * (self.level_width + 40)
        if node.collapsed or not node.children:
            return
        for child in node.children:
            self._assign_x_positions(child, level + 1)

    # ── DRAWING ──
    def _get_screen_pos(self, node):
        return (node.x * self.canvas_zoom + self.canvas_offset_x,
                node.y * self.canvas_zoom + self.canvas_offset_y)

    def _get_node_address(self, node):
        if node is None:
            return ""
        raw_path = []
        current = node
        while current is not None:
            if current.parent is None:
                raw_path.append(1)
            else:
                siblings = current.parent.children
                idx = siblings.index(current) + 1
                raw_path.append(idx)
            current = current.parent
        raw_path.reverse()
        path = [(level, idx) for level, idx in enumerate(raw_path, 1)]
        return "".join(f"lvl{lvl}[{idx}]" for lvl, idx in path)

    def _sync_selection_to_manual(self, node):
        if node is None or not self.manual_editor:
            return
        raw_path = []
        current = node
        while current is not None:
            if current.parent is None:
                raw_path.append(1)
            else:
                siblings = current.parent.children
                try:
                    idx = siblings.index(current) + 1
                except ValueError:
                    idx = 1
                raw_path.append(idx)
            current = current.parent
        raw_path.reverse()
        path = [(level, idx) for level, idx in enumerate(raw_path, 1)]
        path_list = list(path)
        addr_str = "".join(f"lvl{lvl}[{idx}]" for lvl, idx in path)
        match_idx = -1
        for i, mnode in enumerate(self.manual_editor.nodes):
            mpath = mnode.get("path", [])
            if mpath == path_list:
                match_idx = i
                break
        if match_idx < 0:
            for i, mnode in enumerate(self.manual_editor.nodes):
                maddr = "".join(f"lvl{p[0]}[{p[1]}]" for p in mnode.get("path", []))
                if maddr == addr_str:
                    match_idx = i
                    break
        if match_idx >= 0:
            try:
                self.manual_editor._save_current_field()
            except Exception:
                pass
            self.manual_editor.current_node_idx = match_idx
            self.manual_editor.path = path_list
            self.manual_editor.current_field = 0
            self.manual_editor.last_action = None
            self.manual_editor._update_address_display()
            self.manual_editor._update_field_indicator()
            self.manual_editor._load_node_data()
            self.manual_editor._refresh_tree()
            self.canvas_status.config(text=f"Selected: {addr_str} — {node.text}")
        else:
            self.canvas_status.config(text=f"Selected: {addr_str} — {node.text} (not in manual)")

    def _draw_canvas(self):
        self.canvas.delete("all")
        self.canvas_item_to_node.clear()
        self._draw_grid()
        root = None
        for node in self.canvas_nodes.values():
            if node.parent is None:
                root = node
                break
        if root:
            self._draw_subtree(root)
        else:
            for node in self.canvas_nodes.values():
                if node != self.editing_node:
                    self._draw_node(node)

    def _draw_subtree(self, node):
        if node.parent is not None and not node.parent.collapsed:
            self._draw_connector(node.parent, node)
        if node != self.editing_node:
            self._draw_node(node)
        if node.note and node != self.editing_node:
            self._draw_note_indicator(node)
        if node.equation and node != self.editing_node:
            self._draw_equation_indicator(node)
        if not node.collapsed:
            for child in node.children:
                self._draw_subtree(child)

    def _draw_equation_indicator(self, node):
        x, y = self._get_screen_pos(node)
        w = node.width * self.canvas_zoom
        h = node.height * self.canvas_zoom
        ix = x - w/2 + 12 * self.canvas_zoom
        iy = y - h/2 + 12 * self.canvas_zoom
        size = max(6, 8 * self.canvas_zoom)
        for r in range(3, 0, -1):
            green = int(255 * (r / 3.5))
            color = f"#{green:02x}ff00"
            rad = size + (3-r)*2
            self.canvas.create_oval(
                ix - rad, iy - rad, ix + rad, iy + rad,
                fill="", outline=color, width=2
            )
        self.canvas.create_text(
            ix, iy, text="∑", fill="#00ff00", font=("Helvetica", int(size*1.2), "bold")
        )

    def _draw_grid(self):
        spacing = int(80 * self.canvas_zoom)
        if spacing < 16:
            return
        sr = self.canvas.cget("scrollregion")
        if sr:
            parts = sr.split()
            if len(parts) >= 4:
                sr_x1, sr_y1, sr_x2, sr_y2 = map(float, parts)
            else:
                sr_x1, sr_y1, sr_x2, sr_y2 = -200000, -200000, 200000, 200000
        else:
            sr_x1, sr_y1, sr_x2, sr_y2 = -200000, -200000, 200000, 200000
        ox = (self.canvas_offset_x % spacing) - spacing
        oy = (self.canvas_offset_y % spacing) - spacing
        x = sr_x1 - spacing
        while x < sr_x2 + spacing:
            self.canvas.create_line(x, sr_y1 - spacing, x, sr_y2 + spacing, fill="#252540", width=1)
            x += spacing
        y = sr_y1 - spacing
        while y < sr_y2 + spacing:
            self.canvas.create_line(sr_x1 - spacing, y, sr_x2 + spacing, y, fill="#252540", width=1)
            y += spacing

    def _draw_connector(self, parent, child):
        px, py = self._get_screen_pos(parent)
        cx, cy = self._get_screen_pos(child)
        pw = parent.width * self.canvas_zoom
        ph = parent.height * self.canvas_zoom
        cw = child.width * self.canvas_zoom
        ch = child.height * self.canvas_zoom
        lw = max(1.5, self.connector_width * self.canvas_zoom)
        x1 = px + pw / 2
        y1 = py
        x2 = cx - cw / 2
        y2 = cy
        mid_x = (x1 + x2) / 2
        self.canvas.create_line(x1, y1, mid_x, y1, mid_x, y2, x2, y2,
                               fill=self.connector_color, width=lw)
        r = max(2, 3 * self.canvas_zoom)
        self.canvas.create_oval(x2-r, y2-r, x2+r, y2+r,
                               fill=self.connector_color, outline="")

    def _draw_node(self, node):
        x, y = self._get_screen_pos(node)
        w = node.width * self.canvas_zoom
        # Compute height based on text lines
        text = node.text
        max_chars_per_line = 20
        lines = [text[i:i+max_chars_per_line] for i in range(0, len(text), max_chars_per_line)]
        line_count = len(lines)
        base_height = 70
        line_height = 18
        computed_height = max(base_height, line_count * line_height + 10)
        node.height = computed_height
        h = computed_height * self.canvas_zoom

        is_root = node.parent is None
        is_selected = node == self.selected_canvas_node
        has_eq = bool(node.equation)

        if is_selected:
            self.canvas.create_rectangle(
                x - w/2 - 5, y - h/2 - 5, x + w/2 + 5, y + h/2 + 5,
                fill="#4a90d9", outline="#2c5aa0", width=2, tags="select"
            )

        if is_root:
            fill_color = "#2c5aa0"
            outline_color = "#1a3a6e"
            text_color = "#ffffff"
        elif is_selected:
            fill_color = "#e3f2fd"
            outline_color = "#4a90d9"
            text_color = "#333333"
        else:
            fill_color = "#2d2d44"
            outline_color = "#4a4a6a"
            text_color = "#cdd6f4"

        if has_eq and not is_selected:
            for r in range(3, 0, -1):
                green = int(255 * (r / 3.5))
                color = f"#{green:02x}ff00"
                self.canvas.create_rectangle(
                    x - w/2 - 5 - (3-r)*2, y - h/2 - 5 - (3-r)*2,
                    x + w/2 + 5 + (3-r)*2, y + h/2 + 5 + (3-r)*2,
                    outline=color, width=1, tags="eq_glow"
                )

        r = min(8 * self.canvas_zoom, h/4)
        rect_id = self._draw_rounded_rect(x - w/2, y - h/2, x + w/2, y + h/2, r,
                               fill=fill_color, outline=outline_color,
                               width=max(1.5, 2 * self.canvas_zoom), 
                               tags=(f"cnode_{node.id}", "node"))
        if rect_id:
            self.canvas_item_to_node[rect_id] = node

        font_size = max(1, int(14 * self.canvas_zoom))
        weight = "bold" if is_root else "normal"
        text_width = w - 10
        for i, line in enumerate(lines):
            line_y = y - h/2 + 10 + i * line_height * self.canvas_zoom
            self.canvas.create_text(
                x, line_y, text=line, font=("Consolas", font_size, weight),
                fill=text_color, tags=(f"ctext_{node.id}", "node_text"), width=text_width, justify=tk.CENTER
            )

        if node.children:
            ind_x = x + w/2 + 14 * self.canvas_zoom
            ind_y = y
            ind_r = max(6, 9 * self.canvas_zoom)
            ind_color = "#4a90d9" if not node.collapsed else "#7a8b9a"
            self.canvas.create_oval(
                ind_x - ind_r, ind_y - ind_r, ind_x + ind_r, ind_y + ind_r,
                fill="white", outline=ind_color, width=max(1.5, 2 * self.canvas_zoom),
                tags=(f"ccollapse_btn_{node.id}", "collapse_btn")
            )
            line_len = ind_r * 0.5
            self.canvas.create_line(
                ind_x - line_len, ind_y, ind_x + line_len, ind_y,
                fill=ind_color, width=max(1, 1.5 * self.canvas_zoom), tags=f"ccollapse_{node.id}"
            )
            if node.collapsed:
                self.canvas.create_line(
                    ind_x, ind_y - line_len, ind_x, ind_y + line_len,
                    fill=ind_color, width=max(1, 1.5 * self.canvas_zoom), tags=f"ccollapse_{node.id}"
                )

    def _draw_note_indicator(self, node):
        x, y = self._get_screen_pos(node)
        w = node.width * self.canvas_zoom
        h = node.height * self.canvas_zoom
        ix = x + w/2 - 12 * self.canvas_zoom
        iy = y - h/2 + 12 * self.canvas_zoom
        size = max(5, 7 * self.canvas_zoom)
        self.canvas.create_rectangle(
            ix - size, iy - size*0.7, ix + size*0.5, iy + size*0.7,
            fill="#f1c40f", outline="#d4ac0d", width=1, tags=f"cnote_icon_{node.id}"
        )
        self.canvas.create_polygon(
            ix + size*0.2, iy - size*0.7,
            ix + size*0.5, iy - size*0.7,
            ix + size*0.5, iy - size*0.4,
            fill="#d4ac0d", outline="", tags=f"cnote_icon_{node.id}"
        )

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    # ── INTERACTION ──
    def _get_canvas_node_at(self, x, y):
        cx = self.canvas.canvasx(x)
        cy = self.canvas.canvasy(y)
        items = self.canvas.find_overlapping(cx-5, cy-5, cx+5, cy+5)
        for item_id in reversed(items):
            tags = self.canvas.gettags(item_id)
            for tag in tags:
                if tag.startswith("cnode_"):
                    node_id = int(tag.split("_")[-1])
                    for node in self.canvas_nodes.values():
                        if node.id == node_id:
                            if node.parent and node.parent.collapsed:
                                continue
                            return node
                if tag.startswith("ccollapse_btn_"):
                    node_id = int(tag.split("_")[-1])
                    for node in self.canvas_nodes.values():
                        if node.id == node_id:
                            return ("collapse", node)
        for node in self.canvas_nodes.values():
            if node.parent and node.parent.collapsed:
                continue
            nx, ny = self._get_screen_pos(node)
            w = node.width * self.canvas_zoom
            h = node.height * self.canvas_zoom
            if nx - w/2 <= cx <= nx + w/2 and ny - h/2 <= cy <= ny + h/2:
                return node
            if node.children:
                ind_x = nx + w/2 + 14 * self.canvas_zoom
                ind_y = ny
                ind_r = max(6, 9 * self.canvas_zoom)
                if (cx - ind_x)**2 + (cy - ind_y)**2 <= ind_r**2:
                    return ("collapse", node)
        return None

    def _on_canvas_click(self, event):
        if self.is_note_open:
            if self.note_popup:
                popup_x = self.note_popup.winfo_rootx()
                popup_y = self.note_popup.winfo_rooty()
                popup_w = self.note_popup.winfo_width()
                popup_h = self.note_popup.winfo_height()
                if (popup_x <= event.x_root <= popup_x + popup_w and
                    popup_y <= event.y_root <= popup_y + popup_h):
                    return
            self._note_close_source = "click"
            self._close_note_popup()
        if self.is_eq_open:
            if self.eq_popup:
                popup_x = self.eq_popup.winfo_rootx()
                popup_y = self.eq_popup.winfo_rooty()
                popup_w = self.eq_popup.winfo_width()
                popup_h = self.eq_popup.winfo_height()
                if (popup_x <= event.x_root <= popup_x + popup_w and
                    popup_y <= event.y_root <= popup_y + popup_h):
                    return
            self._close_eq_popup()

        if self.editing_node:
            ex, ey = self._get_screen_pos(self.editing_node)
            ew = self.editing_node.width * self.canvas_zoom
            eh = self.editing_node.height * self.canvas_zoom
            if not (ex - ew/2 - 10 <= event.x <= ex + ew/2 + 10 and
                    ey - eh/2 - 10 <= event.y <= ey + eh/2 + 10):
                self._finish_inline_edit()
                return
            else:
                return

        result = self._get_canvas_node_at(event.x, event.y)
        if result:
            if isinstance(result, tuple) and result[0] == "collapse":
                node = result[1]
                node.collapsed = not node.collapsed
                self._auto_layout()
                self._draw_canvas()
                return
            node = result
            self.selected_canvas_node = node
            self.dragging = True
            self.drag_start = (event.x, event.y, node.x, node.y)
            addr = self._get_node_address(node)
            self.canvas_status.config(text=f"Selected: {addr} — {node.text}")
            self._sync_selection_to_manual(node)
            self._draw_canvas()
        else:
            self.selected_canvas_node = None
            self.dragging = False
            self._update_canvas_status()
            self._draw_canvas()
        if self.manual_editor and hasattr(self.manual_editor, 'field_entry'):
            self.manual_editor.field_entry.focus_set()

    def _on_canvas_drag(self, event):
        if self.dragging and self.selected_canvas_node and self.selected_canvas_node.parent is not None:
            dx = (event.x - self.drag_start[0]) / self.canvas_zoom
            dy = (event.y - self.drag_start[1]) / self.canvas_zoom
            self.selected_canvas_node.x = self.drag_start[2] + dx
            self.selected_canvas_node.y = self.drag_start[3] + dy
            self._draw_canvas()

    def _on_canvas_release(self, event):
        if self.dragging and self.selected_canvas_node and self.selected_canvas_node.parent is not None:
            self._auto_layout()
            self._draw_canvas()
        self.dragging = False

    def _on_right_click(self, event):
        if self.xbutton1_mode:
            self.joystick_start = (event.x, event.y)
            self.panning = False
        else:
            self.panning = True
            self.pan_start = (event.x, event.y)

    def _on_right_drag(self, event):
        if self.xbutton1_mode:
            if not hasattr(self, 'joystick_start'):
                self.joystick_start = (event.x, event.y)
            dx = event.x - self.joystick_start[0]
            dy = event.y - self.joystick_start[1]
            threshold = 20
            if abs(dx) > abs(dy):
                if abs(dx) > threshold:
                    dir_x = 1 if dx > 0 else -1
                    self._move_selection(dir_x, 0)
                    self.joystick_start = (event.x, event.y)
            else:
                if abs(dy) > threshold:
                    dir_y = 1 if dy > 0 else -1
                    self._move_selection(0, dir_y)
                    self.joystick_start = (event.x, event.y)
        elif self.panning:
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            self.canvas_offset_x += dx
            self.canvas_offset_y += dy
            self.pan_start = (event.x, event.y)
            self._draw_canvas()

    def _on_right_release(self, event):
        self.panning = False
        if hasattr(self, 'joystick_start'):
            del self.joystick_start

    def _on_scroll(self, event):
        delta = 120 if event.delta > 0 else -120
        if self.xbutton1_mode:
            factor = 1.15 if event.delta > 0 else 0.87
            new_zoom = self.canvas_zoom * factor
            if 0.05 <= new_zoom <= 10.0:
                mx, my = event.x, event.y
                self.canvas_offset_x = mx - (mx - self.canvas_offset_x) * factor
                self.canvas_offset_y = my - (my - self.canvas_offset_y) * factor
                self.canvas_zoom = new_zoom
                self._draw_canvas()
        else:
            if self._shift_pressed or self.shift_lock:
                self.canvas_offset_x += delta
            else:
                self.canvas_offset_y += delta
            self._draw_canvas()

    def _on_scroll_linux(self, event):
        if self.xbutton1_mode:
            factor = 1.08 if event.num == 4 else 0.93
            new_zoom = self.canvas_zoom * factor
            if 0.2 <= new_zoom <= 4.0:
                mx, my = event.x, event.y
                self.canvas_offset_x = mx - (mx - self.canvas_offset_x) * factor
                self.canvas_offset_y = my - (my - self.canvas_offset_y) * factor
                self.canvas_zoom = new_zoom
                self._draw_canvas()
        else:
            delta = 30 if event.num == 4 else -30
            if self._shift_pressed or self.shift_lock:
                self.canvas_offset_x += delta
            else:
                self.canvas_offset_y += delta
            self._draw_canvas()

    def _on_double_click(self, event):
        self.dragging = False
        self.drag_start = None
        result = self._get_canvas_node_at(event.x, event.y)
        if result and not isinstance(result, tuple):
            self.selected_canvas_node = result
            addr = self._get_node_address(result)
            self.canvas_status.config(text=f"Selected: {addr} — {result.text}")
            self._draw_canvas()
            self._start_inline_edit()

    def _on_escape(self):
        if self.is_note_open:
            self._close_note_popup()
        elif self.is_eq_open:
            self._close_eq_popup()
        elif self.edit_entry:
            self._cancel_inline_edit()

    def _move_selection(self, dx, dy):
        if self.selected_canvas_node is None:
            return
        if self.is_note_open:
            self._close_note_popup(save_current=True)
        if self.is_eq_open:
            self._close_eq_popup()
        current = self.selected_canvas_node
        target = None
        if dx < 0:
            target = current.parent
        elif dx > 0:
            if current.children and not current.collapsed:
                target = current.children[0]
            else:
                if current.parent:
                    siblings = current.parent.children
                    idx = siblings.index(current)
                    if idx + 1 < len(siblings):
                        target = siblings[idx + 1]
        elif dy < 0:
            if current.parent:
                siblings = current.parent.children
                idx = siblings.index(current)
                if idx > 0:
                    target = siblings[idx - 1]
        elif dy > 0:
            if current.parent:
                siblings = current.parent.children
                idx = siblings.index(current)
                if idx + 1 < len(siblings):
                    target = siblings[idx + 1]
        if target:
            self.selected_canvas_node = target
            addr = self._get_node_address(target)
            self.canvas_status.config(text=f"Selected: {addr} — {target.text}")
            self._sync_selection_to_manual(target)
            self._draw_canvas()

    # ── INLINE EDITING ──
    def _start_inline_edit(self, node=None):
        if node is None:
            node = self.selected_canvas_node
        if node is None:
            return
        self._finish_inline_edit()
        self._close_note_popup()
        self._close_eq_popup()
        self.editing_node = node
        x, y = self._get_screen_pos(node)
        w = node.width * self.canvas_zoom
        h = node.height * self.canvas_zoom
        self.edit_rect = self.canvas.create_rectangle(
            x - w/2 - 2, y - h/2 - 2, x + w/2 + 2, y + h/2 + 2,
            fill="white", outline="#4a90d9", width=2, tags="edit_bg"
        )
        font_size = max(1, int(14 * self.canvas_zoom))
        self.edit_entry = tk.Entry(self.canvas, font=("Consolas", font_size),
                                   justify="center", relief=tk.FLAT,
                                   bg="white", fg="#333333",
                                   highlightthickness=0, borderwidth=0)
        self.edit_entry.insert(0, node.text)
        self.edit_entry.select_range(0, tk.END)
        self.canvas.create_window(x, y, window=self.edit_entry, width=w-8, height=h-8, tags="edit_window")
        self.edit_entry.focus_set()
        self.edit_entry.icursor(tk.END)
        self.edit_entry.bind("<Return>", lambda e: self._finish_inline_edit())
        self.edit_entry.bind("<Escape>", lambda e: self._cancel_inline_edit())
        self.edit_entry.bind("<FocusOut>", lambda e: self.canvas.after(100, self._finish_inline_edit))

    def _finish_inline_edit(self):
        if self.edit_entry and self.editing_node:
            new_text = self.edit_entry.get().strip()
            if new_text:
                self.editing_node.text = new_text
            self._cleanup_edit()
            self._draw_canvas()
            self._update_scrollregion()
            self.sync_to_manual()
            self.manual_editor._refresh_tree()
            if self.manual_editor.current_node_idx >= 0:
                self.manual_editor._load_node_data()

    def _cancel_inline_edit(self):
        self._cleanup_edit()
        self._draw_canvas()

    def _cleanup_edit(self):
        if self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None
        if self.edit_rect:
            self.canvas.delete(self.edit_rect)
            self.edit_rect = None
        self.canvas.delete("edit_window")
        self.canvas.delete("edit_bg")
        self.editing_node = None
        if self.active:
            self.canvas.focus_set()

    # ── NOTE POPUP ──
    def _toggle_note(self):
        if self.selected_canvas_node is None:
            if self.canvas_nodes:
                self.selected_canvas_node = list(self.canvas_nodes.values())[0]
                self._draw_canvas()
            else:
                return
        if self.is_note_open:
            self._close_note_popup()
        else:
            self._open_note_popup(self.selected_canvas_node)

    def _open_note_popup(self, node):
        if node is None:
            return
        if self.is_note_open:
            if self.note_popup_node == node:
                return
            self._close_note_popup(save_current=True)
        self.note_popup_node = node
        self.is_note_open = True
        try:
            nx, ny = self._get_screen_pos(node)
            popup_x = int(nx + node.width * self.canvas_zoom / 2 + 20)
            popup_y = int(ny - 80)
            screen_w = self.canvas.winfo_width()
            screen_h = self.canvas.winfo_height()
            if popup_x + 300 > screen_w:
                popup_x = int(nx - node.width * self.canvas_zoom / 2 - 310)
            if popup_x < 10:
                popup_x = 10
            if popup_y < 50:
                popup_y = 50
            if popup_y + 220 > screen_h:
                popup_y = screen_h - 230

            self.note_popup = tk.Toplevel(self.canvas)
            self.note_popup.overrideredirect(True)
            self.note_popup.configure(bg="#2d2d44", bd=1, relief=tk.SOLID)
            self.note_popup.geometry(f"280x200+{popup_x}+{popup_y}")
            self.note_popup.lift()
            self.note_popup.focus_set()
            self.note_popup.attributes('-topmost', True)

            header = tk.Frame(self.note_popup, bg="#3d3d5c", height=28)
            header.pack(fill=tk.X)
            header.pack_propagate(False)
            title_text = f"Note: {node.text[:28]}{'...' if len(node.text) > 28 else ''}"
            tk.Label(header, text=title_text, bg="#3d3d5c", fg="#cdd6f4",
                    font=("Consolas", 9, "bold")).pack(side=tk.LEFT, padx=10, pady=3)
            close_btn = tk.Label(header, text="✕", bg="#3d3d5c", fg="#888888",
                                font=("Consolas", 10), cursor="hand2")
            close_btn.pack(side=tk.RIGHT, padx=10, pady=3)
            close_btn.bind("<Button-1>", lambda e: self._close_note_popup_from_button())

            self.note_text_widget = tk.Text(self.note_popup, wrap=tk.WORD, height=7, width=32,
                                            font=("Consolas", 10), bg="#1e1e2e", fg="#cdd6f4",
                                            relief=tk.FLAT, padx=10, pady=8,
                                            insertbackground="#cdd6f4",
                                            selectbackground="#6c5ce7")
            self.note_text_widget.pack(fill=tk.BOTH, expand=True)
            self.note_text_widget.insert("1.0", node.note)
            self.note_text_widget.bind("<KeyRelease>", lambda e: self._auto_save_note())
            self.note_text_widget.bind("<FocusOut>", lambda e: self._on_note_focus_out())
            self.note_text_widget.focus_set()
            self.note_text_widget.mark_set(tk.INSERT, tk.END)
            self.note_text_widget.see(tk.END)

            self.canvas_status.config(text=f"Note open for: {node.text} | Type to edit")
        except Exception as e:
            self.is_note_open = False
            self.note_popup = None
            self.note_popup_node = None

    def _auto_save_note(self):
        if self.note_popup_node and self.note_text_widget:
            new_note = self.note_text_widget.get("1.0", tk.END).strip()
            self.note_popup_node.note = new_note
            if self.manual_editor and self.manual_editor.nodes:
                addr = self._get_node_address(self.note_popup_node)
                for mnode in self.manual_editor.nodes:
                    maddr = "".join(f"lvl{lvl}[{idx}]" for lvl, idx in mnode["path"])
                    if maddr == addr:
                        mnode["note"] = new_note
                        if self.manual_editor.current_node_idx >= 0:
                            current_path = self.manual_editor.nodes[self.manual_editor.current_node_idx]["path"]
                            if mnode["path"] == current_path:
                                self.manual_editor.field_vars[1].set(new_note)
                        break
            if hasattr(self, '_note_draw_after_id') and self._note_draw_after_id:
                self.parent.after_cancel(self._note_draw_after_id)
            self._note_draw_after_id = self.parent.after(300, self._do_note_draw)

    def _do_note_draw(self):
        self._note_draw_after_id = None
        if self.active:
            self._draw_canvas()

    def _on_note_focus_out(self, event=None):
        self.parent.after_idle(self._check_note_focus_lost)

    def _check_note_focus_lost(self):
        try:
            focus_widget = self.parent.focus_get()
            if focus_widget and self.note_popup:
                w = focus_widget
                while w:
                    if w == self.note_popup:
                        return
                    w = w.master
        except tk.TclError:
            pass
        if self.is_note_open:
            self._note_close_source = "focusout"
            self._close_note_popup(save_current=True)

    def _close_note_popup(self, save_current=True):
        if not self.is_note_open:
            return
        if hasattr(self, '_note_draw_after_id') and self._note_draw_after_id:
            self.parent.after_cancel(self._note_draw_after_id)
            self._note_draw_after_id = None
        if save_current and self.note_text_widget and self.note_popup_node:
            self.note_popup_node.note = self.note_text_widget.get("1.0", tk.END).strip()
        target_widget = None
        if self.manual_editor and hasattr(self.manual_editor, 'field_entry'):
            target_widget = self.manual_editor.field_entry
        elif self.active and self._note_close_source not in ("focusout", "click"):
            target_widget = self.canvas
        if target_widget:
            try:
                target_widget.focus_set()
            except tk.TclError:
                pass
        if self.note_popup:
            self.note_popup.destroy()
        self.note_popup = None
        self.note_text_widget = None
        self.note_popup_node = None
        self.is_note_open = False
        self._draw_canvas()
        self._update_scrollregion()
        self.sync_to_manual()
        self.manual_editor._refresh_tree()
        if self.manual_editor and self.manual_editor.current_node_idx >= 0:
            node = self.manual_editor.nodes[self.manual_editor.current_node_idx]
            self.manual_editor.field_vars[1].set(node.get("note", ""))
        self._note_close_source = None
        self._update_canvas_status()

    def _close_note_popup_from_button(self):
        self._note_close_source = "button"
        self._close_note_popup()

    # ── EQUATION POPUP ──
    def _toggle_equation_popup(self):
        if self.selected_canvas_node is None:
            if self.canvas_nodes:
                self.selected_canvas_node = list(self.canvas_nodes.values())[0]
                self._draw_canvas()
            else:
                return
        if self.is_eq_open:
            self._close_eq_popup()
        else:
            self._open_eq_popup(self.selected_canvas_node)

    def _open_eq_popup(self, node):
        if node is None:
            return
        if self.is_eq_open:
            if self.eq_popup_node == node:
                return
            self._close_eq_popup()
        self.eq_popup_node = node
        self.is_eq_open = True
        try:
            nx, ny = self._get_screen_pos(node)
            popup_x = int(nx + node.width * self.canvas_zoom / 2 + 20)
            popup_y = int(ny + 40)
            screen_w = self.canvas.winfo_width()
            screen_h = self.canvas.winfo_height()
            if popup_x + 300 > screen_w:
                popup_x = int(nx - node.width * self.canvas_zoom / 2 - 310)
            if popup_x < 10:
                popup_x = 10
            if popup_y < 50:
                popup_y = 50
            if popup_y + 160 > screen_h:
                popup_y = screen_h - 170

            self.eq_popup = tk.Toplevel(self.canvas)
            self.eq_popup.overrideredirect(True)
            self.eq_popup.configure(bg="#2d2d44", bd=1, relief=tk.SOLID)
            self.eq_popup.geometry(f"280x150+{popup_x}+{popup_y}")
            self.eq_popup.lift()
            self.eq_popup.focus_set()
            self.eq_popup.attributes('-topmost', True)

            header = tk.Frame(self.eq_popup, bg="#3d3d5c", height=28)
            header.pack(fill=tk.X)
            header.pack_propagate(False)
            title_text = f"Equation: {node.text[:24]}{'...' if len(node.text) > 24 else ''}"
            tk.Label(header, text=title_text, bg="#3d3d5c", fg="#00ff00",
                    font=("Consolas", 9, "bold")).pack(side=tk.LEFT, padx=10, pady=3)
            close_btn = tk.Label(header, text="✕", bg="#3d3d5c", fg="#888888",
                                font=("Consolas", 10), cursor="hand2")
            close_btn.pack(side=tk.RIGHT, padx=10, pady=3)
            close_btn.bind("<Button-1>", lambda e: self._close_eq_popup_from_button())

            self.eq_text_widget = tk.Text(self.eq_popup, wrap=tk.WORD, height=3, width=32,
                                          font=("Consolas", 11), bg="#1e1e2e", fg="#00ff00",
                                          relief=tk.FLAT, padx=10, pady=8,
                                          insertbackground="#00ff00",
                                          selectbackground="#6c5ce7")
            self.eq_text_widget.pack(fill=tk.BOTH, expand=True)
            self.eq_text_widget.insert("1.0", node.equation)
            self.eq_text_widget.bind("<KeyRelease>", lambda e: self._auto_save_eq())
            self.eq_text_widget.bind("<FocusOut>", lambda e: self._on_eq_focus_out())
            self.eq_text_widget.focus_set()
            self.eq_text_widget.mark_set(tk.INSERT, tk.END)
            self.eq_text_widget.see(tk.END)

            self.canvas_status.config(text=f"Equation open for: {node.text} | Type LaTeX")
        except Exception as e:
            self.is_eq_open = False
            self.eq_popup = None
            self.eq_popup_node = None

    def _auto_save_eq(self):
        if self.eq_popup_node and self.eq_text_widget:
            new_eq = self.eq_text_widget.get("1.0", tk.END).strip()
            self.eq_popup_node.equation = new_eq
            if self.manual_editor and self.manual_editor.nodes:
                addr = self._get_node_address(self.eq_popup_node)
                for mnode in self.manual_editor.nodes:
                    maddr = "".join(f"lvl{lvl}[{idx}]" for lvl, idx in mnode["path"])
                    if maddr == addr:
                        mnode["equation"] = new_eq
                        if self.manual_editor.current_node_idx >= 0:
                            current_path = self.manual_editor.nodes[self.manual_editor.current_node_idx]["path"]
                            if mnode["path"] == current_path:
                                self.manual_editor.field_vars[3].set(new_eq)
                        break
            if self.active:
                self._draw_canvas()

    def _on_eq_focus_out(self, event=None):
        self.parent.after_idle(self._check_eq_focus_lost)

    def _check_eq_focus_lost(self):
        try:
            focus_widget = self.parent.focus_get()
            if focus_widget and self.eq_popup:
                w = focus_widget
                while w:
                    if w == self.eq_popup:
                        return
                    w = w.master
        except tk.TclError:
            pass
        if self.is_eq_open:
            self._close_eq_popup()

    def _close_eq_popup(self):
        if not self.is_eq_open:
            return
        if self.eq_text_widget and self.eq_popup_node:
            self.eq_popup_node.equation = self.eq_text_widget.get("1.0", tk.END).strip()
        target_widget = None
        if self.manual_editor and hasattr(self.manual_editor, 'field_entry'):
            target_widget = self.manual_editor.field_entry
        elif self.active:
            target_widget = self.canvas
        if target_widget:
            try:
                target_widget.focus_set()
            except tk.TclError:
                pass
        if self.eq_popup:
            self.eq_popup.destroy()
        self.eq_popup = None
        self.eq_text_widget = None
        self.eq_popup_node = None
        self.is_eq_open = False
        self._draw_canvas()
        self._update_scrollregion()
        self.sync_to_manual()
        self.manual_editor._refresh_tree()
        if self.manual_editor and self.manual_editor.current_node_idx >= 0:
            node = self.manual_editor.nodes[self.manual_editor.current_node_idx]
            self.manual_editor.field_vars[3].set(node.get("equation", ""))
        self._update_canvas_status()

    def _close_eq_popup_from_button(self):
        self._close_eq_popup()

    # ── NODE OPERATIONS ──
    def _add_child(self):
        if not self.selected_canvas_node:
            if self.canvas_nodes:
                self.selected_canvas_node = list(self.canvas_nodes.values())[0]
            else:
                return
        self._finish_inline_edit()
        self._close_note_popup()
        self._close_eq_popup()
        parent = self.selected_canvas_node
        new_node = CanvasNode(self.next_canvas_id, "New Node", parent)
        self.canvas_nodes[self.next_canvas_id] = new_node
        parent.children.append(new_node)
        self.next_canvas_id += 1
        parent.collapsed = False
        self._auto_layout()
        self.selected_canvas_node = new_node
        addr = self._get_node_address(new_node)
        self.canvas_status.config(text=f"Selected: {addr} — {new_node.text}")
        self._draw_canvas()
        self._update_scrollregion()
        self.sync_to_manual()
        self.manual_editor._refresh_tree()
        if self.manual_editor.current_node_idx >= 0:
            self.manual_editor._load_node_data()
        self._start_inline_edit(new_node)

    def _add_sibling(self):
        if not self.selected_canvas_node or self.selected_canvas_node.parent is None:
            self.canvas_status.config(text="Select a non-root node")
            return
        self._finish_inline_edit()
        self._close_note_popup()
        self._close_eq_popup()
        parent = self.selected_canvas_node.parent
        idx = parent.children.index(self.selected_canvas_node) + 1
        new_node = CanvasNode(self.next_canvas_id, "New Node", parent)
        self.canvas_nodes[self.next_canvas_id] = new_node
        parent.children.insert(idx, new_node)
        self.next_canvas_id += 1
        self._auto_layout()
        self.selected_canvas_node = new_node
        addr = self._get_node_address(new_node)
        self.canvas_status.config(text=f"Selected: {addr} — {new_node.text}")
        self._draw_canvas()
        self._update_scrollregion()
        self.sync_to_manual()
        self.manual_editor._refresh_tree()
        if self.manual_editor.current_node_idx >= 0:
            self.manual_editor._load_node_data()
        self._start_inline_edit(new_node)

    def _delete_node(self):
        if not self.selected_canvas_node or self.selected_canvas_node.parent is None:
            self.canvas_status.config(text="Cannot delete root")
            return
        from tkinter import messagebox
        if messagebox.askyesno("Confirm Delete", f"Delete '{self.selected_canvas_node.text}' and all children?"):
            self._delete_recursive(self.selected_canvas_node)
            self.selected_canvas_node = None
            self._auto_layout()
            self._draw_canvas()
            self._update_scrollregion()
            self.sync_to_manual()
            self.manual_editor._refresh_tree()
        if self.manual_editor.current_node_idx >= 0:
            self.manual_editor._load_node_data()

    def _delete_recursive(self, node):
        for child in node.children[:]:
            self._delete_recursive(child)
        if node.parent:
            node.parent.children.remove(node)
        if node.id in self.canvas_nodes:
            del self.canvas_nodes[node.id]

    def _toggle_collapse(self):
        if not self.selected_canvas_node:
            return
        self._finish_inline_edit()
        self._close_note_popup()
        self._close_eq_popup()
        self.selected_canvas_node.collapsed = not self.selected_canvas_node.collapsed
        self._auto_layout()
        self._draw_canvas()
        self._update_scrollregion()

    def _reset_view(self):
        self._finish_inline_edit()
        self._close_note_popup()
        self._close_eq_popup()
        self.canvas_offset_x = self.canvas.winfo_width() / 3 if self.canvas.winfo_width() > 100 else 300
        self.canvas_offset_y = self.canvas.winfo_height() / 2 if self.canvas.winfo_height() > 100 else 300
        self.canvas_zoom = 1.0
        self._auto_layout()
        self._draw_canvas()

    def _update_scrollregion(self):
        if not self.canvas_nodes:
            self.canvas.configure(scrollregion=(-200000, -200000, 200000, 200000))
            return
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        for node in self.canvas_nodes.values():
            if node.parent and node.parent.collapsed:
                continue
            lx, ly = node.x, node.y
            w = node.width
            h = node.height
            min_x = min(min_x, lx - w/2)
            min_y = min(min_y, ly - h/2)
            max_x = max(max_x, lx + w/2)
            max_y = max(max_y, ly + h/2)
        padding = 500
        min_x -= padding
        min_y -= padding
        max_x += padding
        max_y += padding
        self.canvas.configure(scrollregion=(min_x, min_y, max_x, max_y))

    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.active = True
        self.canvas.update_idletasks()
        self.sync_from_manual()
        self._draw_canvas()
        self._update_scrollregion()
        self.canvas.focus_set()
        self._setup_xbutton_listener()

    def hide(self):
        if self.is_note_open:
            self._close_note_popup(save_current=True)
        if self.is_eq_open:
            self._close_eq_popup()
        self._remove_xbutton_hook()
        self.frame.pack_forget()
        self.active = False

# ============================================================
# ManualModeEditor
# ============================================================
class ManualModeEditor:
    def __init__(self, parent_frame, app, colors):
        self.parent = parent_frame
        self.app = app
        self.colors = colors
        self.active = False
        self.path = [(1, 1)]
        self.current_field = 0
        self.last_action = None
        self.field_names = ["Heading", "Note", "Label", "Equation"]
        self.field_vars = [tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()]
        self.nodes = []
        self.current_node_idx = -1

        self._build_ui()

    def _build_ui(self):
        self.frame = tk.Frame(self.parent, bg=self.colors["bg"])

        top = tk.Frame(self.frame, bg=self.colors["bg"])
        top.pack(fill=tk.X, pady=(0, 6))
        self.addr_lbl = tk.Label(
            top, text="lvl1[1]", font=("Consolas", 14, "bold"),
            bg=self.colors["bg"], fg="#b4befe"
        )
        self.addr_lbl.pack(side=tk.LEFT)
        help_text = "Enter/Tab=deeper (at root) | Enter=sibling | Tab=child (at lvl2+) | Shift=field | Backspace=delete"
        tk.Label(top, text=help_text, font=("Helvetica", 8),
                bg=self.colors["bg"], fg="#888888").pack(side=tk.RIGHT)

        self.field_indicator = tk.Label(
            self.frame, text="▶ Heading", font=("Helvetica", 10, "bold"),
            bg=self.colors["bg"], fg="#00b894"
        )
        self.field_indicator.pack(anchor=tk.W, pady=(0, 4))

        chk_frame = tk.Frame(self.frame, bg=self.colors["bg"])
        chk_frame.pack(fill=tk.X, pady=(0, 4))
        self.chk_note = tk.BooleanVar(value=True)
        self.chk_label = tk.BooleanVar(value=False)
        self.chk_equation = tk.BooleanVar(value=False)
        tk.Checkbutton(chk_frame, text="Note", variable=self.chk_note,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"],
                       selectcolor=self.colors["select"],
                       font=("Helvetica", 9)).pack(side=tk.LEFT, padx=4)
        tk.Checkbutton(chk_frame, text="Label", variable=self.chk_label,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"],
                       selectcolor=self.colors["select"],
                       font=("Helvetica", 9)).pack(side=tk.LEFT, padx=4)
        tk.Checkbutton(chk_frame, text="Equation", variable=self.chk_equation,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"],
                       selectcolor=self.colors["select"],
                       font=("Helvetica", 9)).pack(side=tk.LEFT, padx=4)

        input_frame = tk.Frame(self.frame, bg=self.colors["bg"])
        input_frame.pack(fill=tk.X, pady=(0, 6))
        self.field_entry = tk.Text(
            input_frame, height=1, font=("Consolas", 12),
            bg=self.colors["input_bg"], fg=self.colors["input_fg"],
            insertbackground=self.colors["input_fg"],
            relief=tk.SOLID, bd=1, wrap=tk.NONE
        )
        self.field_entry.pack(fill=tk.X, ipady=3)
        self.field_entry.focus_set()

        self.field_entry.bind("<Tab>", self._on_tab)
        self.field_entry.bind("<Shift-Tab>", self._on_shift_tab)
        self.field_entry.bind("<Return>", self._on_return)
        self.field_entry.bind("<Shift-Return>", self._on_shift_return)
        self.field_entry.bind("<BackSpace>", self._on_backspace)
        self.field_entry.bind("<KeyRelease>", self._on_field_changed)
        self.field_entry.bind("<FocusIn>", self._on_field_focus)
        self.field_entry.bind("<KeyRelease-Shift_L>", self._on_shift_release)
        self.field_entry.bind("<KeyRelease-Shift_R>", self._on_shift_release)
        self.frame.bind("<Tab>", self._on_tab)
        self.frame.bind("<Shift-Tab>", self._on_shift_tab)
        self.frame.bind("<Return>", self._on_return)
        self.frame.bind("<Shift-Return>", self._on_shift_return)
        self.shift_pressed = False
        self.shift_timer = None

        btn_frame = tk.Frame(self.frame, bg=self.colors["bg"])
        btn_frame.pack(fill=tk.X, pady=(0, 6))
        tk.Button(btn_frame, text="⬆ Up", command=self._go_up_level,
                  bg=self.colors["btn_bg"], fg="#000000", relief=tk.FLAT,
                  font=("Helvetica", 9), cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="⬇ Down", command=self._go_down_level,
                  bg=self.colors["btn_bg"], fg="#000000", relief=tk.FLAT,
                  font=("Helvetica", 9), cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="⬅ Prev", command=self._prev_sibling,
                  bg=self.colors["btn_bg"], fg="#000000", relief=tk.FLAT,
                  font=("Helvetica", 9), cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="➡ Next", command=self._next_sibling,
                  bg=self.colors["btn_bg"], fg="#000000", relief=tk.FLAT,
                  font=("Helvetica", 9), cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="⇄ Field", command=self._cycle_field,
                  bg="#6c5ce7", fg="#ffffff", relief=tk.FLAT,
                  font=("Helvetica", 9, "bold"), cursor="hand2").pack(side=tk.LEFT, padx=(10, 2))

        mode_toggle = tk.Frame(self.frame, bg=self.colors["bg"])
        mode_toggle.pack(fill=tk.X, pady=(0, 4))
        self.view_mode_var = tk.StringVar(value="spreadsheet")
        tk.Button(mode_toggle, text="📊 Spreadsheet", command=self._show_spreadsheet,
                  bg="#6c5ce7", fg="#ffffff", font=("Helvetica", 9, "bold"),
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(mode_toggle, text="🎨 Canvas", command=self._show_canvas,
                  bg=self.colors["btn_bg"], fg="#000000", font=("Helvetica", 9, "bold"),
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)

        self.view_container = tk.Frame(self.frame, bg=self.colors["bg"])
        self.view_container.pack(fill=tk.BOTH, expand=True)

        tree_outer = tk.LabelFrame(
            self.view_container, text=" Mind Map Hierarchy — click row to edit | ▶/▼ to expand/collapse ",
            bg=self.colors["bg"], fg=self.colors["fg"],
            font=("Helvetica", 9, "bold"), padx=4, pady=4
        )
        tree_outer.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.Treeview",
                        background=self.colors["input_bg"],
                        foreground=self.colors["input_fg"],
                        fieldbackground=self.colors["input_bg"],
                        rowheight=28)
        style.configure("Custom.Treeview.Heading",
                        background=self.colors["accent"],
                        foreground=self.colors["fg"],
                        font=("Helvetica", 9, "bold"))
        style.map("Custom.Treeview",
                  background=[("selected", "#6c5ce7")],
                  foreground=[("selected", "#ffffff")])

        self.tree_view = ttk.Treeview(
            tree_outer,
            columns=("address", "heading", "note", "label", "equation"),
            show="tree headings",
            style="Custom.Treeview",
            selectmode="browse"
        )
        self.tree_view.heading("#0", text="Lvl")
        self.tree_view.heading("address", text="Address")
        self.tree_view.heading("heading", text="Heading")
        self.tree_view.heading("note", text="Note")
        self.tree_view.heading("label", text="Label")
        self.tree_view.heading("equation", text="Equation")

        self.tree_view.column("#0", width=40, anchor="center", stretch=False)
        self.tree_view.column("address", width=100, anchor="w", stretch=False)
        self.tree_view.column("heading", width=150, anchor="w", stretch=True)
        self.tree_view.column("note", width=150, anchor="w", stretch=True)
        self.tree_view.column("label", width=80, anchor="w", stretch=True)
        self.tree_view.column("equation", width=100, anchor="w", stretch=True)

        tree_scroll_y = tk.Scrollbar(tree_outer, orient=tk.VERTICAL, command=self.tree_view.yview)
        tree_scroll_x = tk.Scrollbar(tree_outer, orient=tk.HORIZONTAL, command=self.tree_view.xview)
        self.tree_view.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.tree_view.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        tree_outer.grid_rowconfigure(0, weight=1)
        tree_outer.grid_columnconfigure(0, weight=1)

        self.tree_view.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree_view.bind("<Return>", self._on_tree_select)

        self.selected_tree_node = None
        self.canvas_editor = None

    # ── New method: reload from current raw text ──
    def reload_from_text(self):
        """Re‑parse the raw text from the main input and update internal nodes,
        preserving the current selection by path if possible."""
        raw_text = self.app.input_text.get("1.0", tk.END).strip()
        if not raw_text:
            self.nodes = []
            self.current_node_idx = -1
            self.path = [(1, 1)]
            self._refresh_tree()
            self._update_address_display()
            self._load_node_data()
            return

        try:
            # Parse the raw text exactly as in show()
            raw_entries = []
            current = ""
            brace_depth = 0
            for char in raw_text:
                if char == "{":
                    brace_depth += 1
                    current += char
                elif char == "}":
                    brace_depth -= 1
                    current += char
                elif char == "\n" and brace_depth == 0:
                    if current.strip():
                        raw_entries.append(current.strip())
                    current = ""
                else:
                    current += char
            if current.strip():
                raw_entries.append(current.strip())

            new_nodes = []
            for raw in raw_entries:
                path = []
                remaining = raw
                while True:
                    m = re.match(r'^lvl(\d+)\[(\d+)\]', remaining, re.IGNORECASE)
                    if not m:
                        break
                    level = int(m.group(1))
                    index = int(m.group(2))
                    path.append((level, index))
                    remaining = remaining[m.end():]
                if not path:
                    continue
                title_match = re.match(r'^\s*(.*?)(?:\{(.*)\})?$', remaining, re.DOTALL)
                if not title_match:
                    continue
                title = title_match.group(1).strip()
                brace = title_match.group(2)
                note = ""
                label = ""
                equation = ""
                eq_w = 260
                eq_h = 70
                eq_font = 18
                if brace:
                    m = re.search(r'note:\s*"([^"]*)"', brace)
                    if m:
                        note = m.group(1)
                    m = re.search(r'label:\s*"([^"]*)"', brace)
                    if m:
                        label = m.group(1)
                    eq_raw = EquationNormalizer.extract(brace)
                    if eq_raw:
                        equation = EquationNormalizer.normalize(eq_raw)
                    for key in ("eq_w", "eq_h", "eq_font"):
                        pat = rf'{key}\s*:\s*(\d+)'
                        m = re.search(pat, brace, re.IGNORECASE)
                        if m:
                            if key == "eq_w": eq_w = int(m.group(1))
                            elif key == "eq_h": eq_h = int(m.group(1))
                            elif key == "eq_font": eq_font = int(m.group(1))
                new_nodes.append({
                    "path": path,
                    "heading": title,
                    "note": note,
                    "label": label,
                    "equation": equation,
                    "eq_w": eq_w,
                    "eq_h": eq_h,
                    "eq_font": eq_font,
                })
            # Preserve selection if possible
            old_path = tuple(self.path) if self.path else None
            self.nodes = new_nodes
            if old_path:
                for idx, node in enumerate(self.nodes):
                    if tuple(node["path"]) == old_path:
                        self.current_node_idx = idx
                        self.path = list(old_path)
                        break
                else:
                    # fallback to root
                    self.current_node_idx = 0 if self.nodes else -1
                    self.path = [(1, 1)] if self.nodes else [(1, 1)]
            else:
                self.current_node_idx = 0 if self.nodes else -1
                self.path = [(1, 1)] if self.nodes else [(1, 1)]
            self._refresh_tree()
            self._update_address_display()
            self._load_node_data()
        except Exception as e:
            print(f"[ManualMode] reload_from_text error: {e}", file=sys.stderr)
            # Keep existing nodes as fallback

    def _update_address_display(self):
        addr = "".join(f"lvl{lvl}[{idx}]" for lvl, idx in self.path)
        self.addr_lbl.config(text=addr)

    def _update_field_indicator(self):
        name = self.field_names[self.current_field]
        colors = ["#00b894", "#0984e3", "#6c5ce7", "#00ff00"]
        self.field_indicator.config(text=f"▶ {name}", fg=colors[self.current_field])
        self.field_entry.delete("1.0", tk.END)
        self.field_entry.insert("1.0", self.field_vars[self.current_field].get())
        if self.current_field == 3:
            self.field_entry.config(fg="#00ff00")
        else:
            self.field_entry.config(fg=self.colors["input_fg"])

    def _save_current_field(self):
        text = self.field_entry.get("1.0", tk.END).strip()
        self.field_vars[self.current_field].set(text)
        if self.current_node_idx >= 0 and self.current_node_idx < len(self.nodes):
            node = self.nodes[self.current_node_idx]
            node["heading"] = self.field_vars[0].get()
            node["note"] = self.field_vars[1].get()
            node["label"] = self.field_vars[2].get()
            node["equation"] = self.field_vars[3].get()

    def _create_or_update_node(self):
        path_tuple = tuple(self.path)
        for i, node in enumerate(self.nodes):
            if tuple(node["path"]) == path_tuple:
                self.current_node_idx = i
                return
        new_node = {
            "path": list(self.path), "heading": "", "note": "", "label": "", "equation": "",
            "eq_w": 260, "eq_h": 70, "eq_font": 18,
        }
        self.nodes.append(new_node)
        self.current_node_idx = len(self.nodes) - 1

    def _load_node_data(self):
        if self.current_node_idx >= 0 and self.current_node_idx < len(self.nodes):
            node = self.nodes[self.current_node_idx]
            self.field_vars[0].set(node.get("heading", ""))
            self.field_vars[1].set(node.get("note", ""))
            self.field_vars[2].set(node.get("label", ""))
            self.field_vars[3].set(node.get("equation", ""))
        else:
            for v in self.field_vars:
                v.set("")
        self.field_entry.delete("1.0", tk.END)
        self.field_entry.insert("1.0", self.field_vars[self.current_field].get())
        if self.current_field == 3:
            self.field_entry.config(fg="#00ff00")
        else:
            self.field_entry.config(fg=self.colors["input_fg"])

    def _cycle_field(self):
        self._save_current_field()
        active_fields = [0]
        if self.chk_note.get():
            active_fields.append(1)
        if self.chk_label.get():
            active_fields.append(2)
        if self.chk_equation.get():
            active_fields.append(3)
        if len(active_fields) <= 1:
            return
        try:
            current_pos = active_fields.index(self.current_field)
        except ValueError:
            current_pos = -1
        next_pos = (current_pos + 1) % len(active_fields)
        self.current_field = active_fields[next_pos]
        self._update_field_indicator()
        self.field_entry.focus_set()
        self.field_entry.mark_set(tk.INSERT, tk.END)

    def _on_shift_release(self, event):
        if self.shift_timer:
            self.frame.after_cancel(self.shift_timer)
        self.shift_timer = self.frame.after(50, self._do_shift_cycle)

    def _do_shift_cycle(self):
        self._cycle_field()
        self.shift_timer = None

    def _on_field_changed(self, event=None):
        if event and event.keysym in ('Shift_L', 'Shift_R', 'Control_L', 'Control_R',
                                       'Alt_L', 'Alt_R', 'Caps_Lock', 'Num_Lock',
                                       'Left', 'Right', 'Up', 'Down', 'Home', 'End',
                                       'Page_Up', 'Page_Down', 'Insert', 'Delete',
                                       'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12'):
            return
        self._save_current_field()
        self._refresh_tree()
        if self.canvas_editor:
            self.canvas_editor.sync_text_from_manual()

    def _on_field_focus(self, event=None):
        self._save_current_field()
        if self.canvas_editor:
            self.canvas_editor.sync_text_from_manual()

    def _has_content(self):
        if self.current_node_idx >= 0 and self.current_node_idx < len(self.nodes):
            node = self.nodes[self.current_node_idx]
            heading = node.get("heading", "").strip()
            note = node.get("note", "").strip()
        else:
            heading = self.field_vars[0].get().strip()
            note = self.field_vars[1].get().strip()
        return bool(heading) or bool(note)

    def _on_tab(self, event):
        self._save_current_field()
        if not self._has_content():
            self.app.status_var.set("ERROR: Add a heading or note before creating a child.")
            return "break"
        current_level = self.path[-1][0]
        self.path.append((current_level + 1, 1))
        self.last_action = "tab"
        self._update_address_display()
        self.current_field = 0
        self._update_field_indicator()
        self._create_or_update_node()
        self._load_node_data()
        self._refresh_tree()
        if self.canvas_editor:
            self.canvas_editor.sync_from_manual()
        self.frame.after(10, lambda: self.field_entry.focus_set())
        self.frame.after(15, lambda: self.field_entry.mark_set(tk.INSERT, tk.END))
        return "break"

    def _on_shift_tab(self, event):
        self._save_current_field()
        if len(self.path) > 1:
            self.path.pop()
        self._update_address_display()
        self.current_field = 0
        self._update_field_indicator()
        self._create_or_update_node()
        self._load_node_data()
        self._refresh_tree()
        self.frame.after(10, lambda: self.field_entry.focus_set())
        return "break"

    def _on_return(self, event):
        self._save_current_field()
        if not self._has_content():
            self.app.status_var.set("ERROR: Add a heading or note before creating a sibling.")
            return "break"
        if len(self.path) == 1:
            current_level = self.path[-1][0]
            self.path.append((current_level + 1, 1))
            self.last_action = "enter"
            self._update_address_display()
            self.current_field = 0
            self._update_field_indicator()
            self._create_or_update_node()
            self._load_node_data()
            self._refresh_tree()
            if self.canvas_editor:
                self.canvas_editor.sync_from_manual()
            self.frame.after(10, lambda: self.field_entry.focus_set())
            self.frame.after(15, lambda: self.field_entry.mark_set(tk.INSERT, tk.END))
            return "break"
        current_level, current_idx = self.path[-1]
        self.path[-1] = (current_level, current_idx + 1)
        self.last_action = "enter"
        self._update_address_display()
        self.current_field = 0
        self._update_field_indicator()
        self._create_or_update_node()
        self._load_node_data()
        self._refresh_tree()
        if self.canvas_editor:
            self.canvas_editor.sync_from_manual()
        self.frame.after(10, lambda: self.field_entry.focus_set())
        self.frame.after(15, lambda: self.field_entry.mark_set(tk.INSERT, tk.END))
        return "break"

    def _on_shift_return(self, event):
        self._save_current_field()
        current_level, current_idx = self.path[-1]
        if current_idx > 1:
            self.path[-1] = (current_level, current_idx - 1)
        self._update_address_display()
        self.current_field = 0
        self._update_field_indicator()
        self._create_or_update_node()
        self._load_node_data()
        self._refresh_tree()
        self.frame.after(10, lambda: self.field_entry.focus_set())
        return "break"

    def _on_backspace(self, event):
        if self.field_entry.get("1.0", tk.END).strip():
            return
        if self.current_node_idx >= 0 and self.current_node_idx < len(self.nodes):
            self.nodes.pop(self.current_node_idx)
            if self.current_node_idx >= len(self.nodes):
                self.current_node_idx = max(0, len(self.nodes) - 1)
        current_level, current_idx = self.path[-1]
        if current_idx > 1:
            self.path[-1] = (current_level, current_idx - 1)
        elif len(self.path) > 1:
            self.path.pop()
        self._update_address_display()
        self.current_field = 0
        self._update_field_indicator()
        self._create_or_update_node()
        self._load_node_data()
        self._refresh_tree()
        self.frame.after(10, lambda: self.field_entry.focus_set())
        return "break"

    def _go_up_level(self):
        self._on_shift_tab(None)

    def _go_down_level(self):
        self._on_tab(None)

    def _prev_sibling(self):
        self._on_shift_return(None)

    def _next_sibling(self):
        self._on_return(None)

    def _edit_node_by_idx(self, idx):
        if idx < 0 or idx >= len(self.nodes):
            return
        self._save_current_field()
        self.current_node_idx = idx
        self.path = list(self.nodes[idx]["path"])
        self.current_field = 0
        self.last_action = None
        self._update_address_display()
        self._update_field_indicator()
        self._load_node_data()
        self.field_entry.focus_set()
        self._refresh_tree()
        self.app.status_var.set(f"Editing: {self.nodes[idx].get('heading', '')}")

    def _refresh_tree(self):
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)
        if not self.nodes:
            return
        path_to_iid = {}
        def _make_key(path):
            return tuple(tuple(p) for p in path)
        sorted_nodes = sorted(enumerate(self.nodes), key=lambda x: _make_key(x[1]["path"]))

        has_eq = set()
        for idx, node in enumerate(self.nodes):
            if node.get("equation", "").strip():
                has_eq.add(idx)

        for idx, node in sorted_nodes:
            heading = node.get("heading", "")
            display_heading = heading if heading else "(empty)"
            if node.get("equation"):
                display_heading += " ∑"
            path = node["path"]
            addr = "".join(f"lvl{lvl}[{i}]" for lvl, i in path)
            depth = len(path)
            note = node.get("note", "")
            label = node.get("label", "")
            equation = node.get("equation", "")

            parent_iid = ""
            if len(path) > 1:
                parent_path = _make_key(path[:-1])
                parent_iid = path_to_iid.get(parent_path, "")

            tags = ("selected" if idx == self.current_node_idx else "",)
            if idx in has_eq:
                tags = tags + ("has_eq",)

            iid = self.tree_view.insert(
                parent_iid,
                tk.END,
                text=str(depth),
                values=(addr, display_heading, note, label, equation),
                tags=tags
            )
            path_to_iid[_make_key(path)] = iid

        self.tree_view.tag_configure("has_eq", background="#2d4a2d", foreground="#00ff00")

        for iid in self.tree_view.get_children():
            self.tree_view.item(iid, open=True)
            self._expand_all(iid)

        if self.current_node_idx >= 0 and self.current_node_idx < len(self.nodes):
            target_key = _make_key(self.nodes[self.current_node_idx]["path"])
            for p, iid in path_to_iid.items():
                if p == target_key:
                    self.tree_view.selection_set(iid)
                    self.tree_view.see(iid)
                    break

    def _expand_all(self, parent):
        for child in self.tree_view.get_children(parent):
            self.tree_view.item(child, open=True)
            self._expand_all(child)

    def _on_tree_select(self, event=None):
        selection = self.tree_view.selection()
        if not selection:
            return
        iid = selection[0]
        values = self.tree_view.item(iid, "values")
        if not values:
            return
        addr = values[0]
        for idx, node in enumerate(self.nodes):
            node_addr = "".join(f"lvl{lvl}[{i}]" for lvl, i in node["path"])
            if node_addr == addr:
                self.selected_tree_node = idx
                if idx != self.current_node_idx:
                    self._edit_node_by_idx(idx)
                break

    def _show_spreadsheet(self):
        self.view_mode_var.set("spreadsheet")
        if hasattr(self, 'canvas_editor') and self.canvas_editor and self.canvas_editor.active:
            if self.canvas_editor.is_note_open:
                self.canvas_editor._close_note_popup(save_current=True)
            if self.canvas_editor.is_eq_open:
                self.canvas_editor._close_eq_popup()
            self.canvas_editor.sync_to_manual()
            self.canvas_editor.hide()
        self.view_container.pack(fill=tk.BOTH, expand=True)
        self._refresh_tree()
        if self.current_node_idx >= 0:
            self._load_node_data()
        self.app.status_var.set("Spreadsheet mode — click rows to edit")

    def _show_canvas(self):
        self.view_mode_var.set("canvas")
        self.view_container.pack_forget()
        if not hasattr(self, 'canvas_editor') or self.canvas_editor is None:
            self.canvas_editor = CanvasModeEditor(self.frame, self, self.colors)
        self._save_current_field()
        self.canvas_editor.sync_from_manual()
        self.canvas_editor.show()
        self.app.status_var.set("Canvas mode — click nodes to select | scroll to zoom | right-drag to pan")

    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.active = True
        if not hasattr(self, 'canvas_editor') or self.canvas_editor is None:
            self.canvas_editor = CanvasModeEditor(self.frame, self, self.colors)

        raw_text = self.app.input_text.get("1.0", tk.END).strip()
        if raw_text:
            try:
                raw_entries = []
                current = ""
                brace_depth = 0
                for char in raw_text:
                    if char == "{":
                        brace_depth += 1
                        current += char
                    elif char == "}":
                        brace_depth -= 1
                        current += char
                    elif char == "\n" and brace_depth == 0:
                        if current.strip():
                            raw_entries.append(current.strip())
                        current = ""
                    else:
                        current += char
                if current.strip():
                    raw_entries.append(current.strip())

                self.nodes = []
                for raw in raw_entries:
                    path = []
                    remaining = raw
                    while True:
                        m = re.match(r'^lvl(\d+)\[(\d+)\]', remaining, re.IGNORECASE)
                        if not m:
                            break
                        level = int(m.group(1))
                        index = int(m.group(2))
                        path.append((level, index))
                        remaining = remaining[m.end():]
                    if not path:
                        continue
                    title_match = re.match(r'^\s*(.*?)(?:\{(.*)\})?$', remaining, re.DOTALL)
                    if not title_match:
                        continue
                    title = title_match.group(1).strip()
                    brace = title_match.group(2)
                    note = None
                    label = ""
                    equation = ""
                    eq_w = 260
                    eq_h = 70
                    eq_font = 18
                    eq_color = "black"
                    eq_bg = "#ffffff"
                    img_fmt = "png"
                    if brace:
                        m = re.search(r'note:\s*"([^"]*)"', brace)
                        if m:
                            note = m.group(1)
                        m = re.search(r'label:\s*"([^"]*)"', brace)
                        if m:
                            label = m.group(1)
                        eq_raw = EquationNormalizer.extract(brace)
                        if eq_raw:
                            equation = EquationNormalizer.normalize(eq_raw)
                        for key in ("eq_w", "eq_h", "eq_font"):
                            pat = rf'{key}\s*:\s*(\d+)'
                            m = re.search(pat, brace, re.IGNORECASE)
                            if m:
                                if key == "eq_w": eq_w = int(m.group(1))
                                elif key == "eq_h": eq_h = int(m.group(1))
                                elif key == "eq_font": eq_font = int(m.group(1))
                        m = re.search(r'eq_color\s*:\s*"([^"]*)"', brace, re.IGNORECASE)
                        if m:
                            eq_color = m.group(1)
                        else:
                            m = re.search(r'eq_color\s*:\s*(#[0-9a-fA-F]{6})', brace, re.IGNORECASE)
                            if m:
                                eq_color = m.group(1)
                        m = re.search(r'eq_bg\s*:\s*"([^"]*)"', brace, re.IGNORECASE)
                        if m:
                            eq_bg = m.group(1)
                        else:
                            m = re.search(r'eq_bg\s*:\s*(#[0-9a-fA-F]{6}|none)', brace, re.IGNORECASE)
                            if m:
                                eq_bg = m.group(1)
                        m = re.search(r'img_fmt\s*:\s*"?(\w+)"?', brace, re.IGNORECASE)
                        if m:
                            fmt = m.group(1).lower()
                            if fmt == 'jpeg': fmt = 'jpg'
                            if fmt in IMAGE_FORMATS:
                                img_fmt = fmt
                    self.nodes.append({
                        "path": path,
                        "heading": title,
                        "note": note or "",
                        "label": label,
                        "equation": equation,
                        "eq_w": eq_w,
                        "eq_h": eq_h,
                        "eq_font": eq_font,
                        "eq_color": eq_color,
                        "eq_bg": eq_bg,
                        "img_fmt": img_fmt,
                    })
                if self.nodes:
                    self.current_node_idx = len(self.nodes) - 1
                    self.path = list(self.nodes[-1]["path"])
                    self.current_field = 0
                    self._update_address_display()
                    self._update_field_indicator()
                    self._load_node_data()
                    self._refresh_tree()
                    self.last_action = None
                    self.frame.after(10, lambda: self.field_entry.focus_set())
                    self.frame.after(15, lambda: self.field_entry.mark_set(tk.INSERT, tk.END))
                    self.app.status_var.set(f"Manual Mode: Loaded {len(self.nodes)} nodes from editor")
                    return
            except Exception as e:
                print(f"[ManualMode] Parse error on show: {e}", file=sys.stderr)

        self.path = [(1, 1)]
        self.current_field = 0
        self.nodes = []
        self.current_node_idx = -1
        self.selected_tree_node = None
        self.last_action = None
        self._create_or_update_node()
        self._update_address_display()
        self._update_field_indicator()
        self._load_node_data()
        self._refresh_tree()
        self.frame.after(10, lambda: self.field_entry.focus_set())
        self.frame.after(15, lambda: self.field_entry.mark_set(tk.INSERT, tk.END))

    def hide(self):
        self._save_current_field()
        if self.canvas_editor and self.canvas_editor.active:
            if self.canvas_editor.is_note_open:
                self.canvas_editor._close_note_popup(save_current=True)
            if self.canvas_editor.is_eq_open:
                self.canvas_editor._close_eq_popup()
            self.canvas_editor.sync_to_manual()
            self.canvas_editor.hide()

        lines = []
        for node in self.nodes:
            addr = "".join(f"lvl{lvl}[{idx}]" for lvl, idx in node["path"])
            heading = node.get("heading", "")
            if not heading:
                continue
            line = f"{addr}{heading}"
            parts = []
            if node.get("note"):
                parts.append(f'note:"{node["note"]}"')
            if node.get("label"):
                parts.append(f'label:"{node["label"]}"')
            if node.get("equation"):
                clean_eq = EquationNormalizer.normalize(node["equation"])
                parts.append(f'equation:"{clean_eq}"')
                if node.get("eq_w") and node["eq_w"] != 260:
                    parts.append(f'eq_w:{node["eq_w"]}')
                if node.get("eq_h") and node["eq_h"] != 70:
                    parts.append(f'eq_h:{node["eq_h"]}')
                if node.get("eq_font") and node["eq_font"] != 18:
                    parts.append(f'eq_font:{node["eq_font"]}')
                if node.get("eq_color"):
                    parts.append(f'eq_color:"{node["eq_color"]}"')
                if node.get("eq_bg"):
                    parts.append(f'eq_bg:"{node["eq_bg"]}"')
                if node.get("img_fmt") and node["img_fmt"] != DEFAULT_IMAGE_FMT:
                    parts.append(f'img_fmt:"{node["img_fmt"]}"')
            if parts:
                line += "{" + ",".join(parts) + "}"
            lines.append(line)

        text = "\n".join(lines)
        if text:
            self.app.input_text.delete("1.0", tk.END)
            self.app.input_text.insert("1.0", text)

        if self.canvas_editor and self.canvas_editor.active:
            self.canvas_editor.hide()
        self.frame.pack_forget()
        self.active = False

# ============================================================
# Eq Adjuster Panel (M3-82: Focus mode removed; searchable,
# collapsible node list added -- click any node to instantly
# see its equation, type to filter live)
# ============================================================
class EqAdjusterPanel(tk.Frame):
    def __init__(self, parent, app, nodes_with_eq, close_callback):
        super().__init__(parent, bg=app.colors["bg"])
        self.app = app
        self.nodes = nodes_with_eq
        self.close_callback = close_callback

        # filtered_indices holds indices into self.nodes for whatever subset
        # is currently shown in the list (all of them, or a search filter).
        self.filtered_indices = list(range(len(nodes_with_eq)))
        self.current_node_idx = 0 if nodes_with_eq else -1
        self.list_visible = True
        self.width_mode = False
        self.font_mode = False
        self.right_button_held = False
        self.left_click_drag = False
        self.canvas_zoom = 1.0
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self._current_image = None
        self._hook_id = None
        self._hook_callback_ref = None
        self._rmb_combo_active = False
        self._rmb_combo_done = False
        self._drag_start = None

        self._build_ui()
        self._setup_bindings()
        self._refresh_listbox()
        self._sync_list_selection()
        self._render_current()
        self.focus_set()
        self._update_values_display()
        self._update_mode_label()

    def _build_ui(self):
        top = tk.Frame(self, bg=self.app.colors["bg"])
        top.pack(fill=tk.X, pady=(4, 4))

        self.info_label = tk.Label(top, text="", bg=self.app.colors["bg"], fg=self.app.colors["fg"],
                                   font=("Helvetica", 10))
        self.info_label.pack(side=tk.LEFT, padx=8)

        btn_frame = tk.Frame(top, bg=self.app.colors["bg"])
        btn_frame.pack(side=tk.RIGHT, padx=8)
        self.list_toggle_btn = tk.Button(btn_frame, text="\u25c0 Hide List", command=self._toggle_list_visibility,
                                         bg="#555", fg="white", font=("Helvetica", 8, "bold"),
                                         relief=tk.FLAT, padx=6, pady=2)
        self.list_toggle_btn.pack(side=tk.LEFT, padx=2)
        self.width_btn = tk.Button(btn_frame, text="Width OFF", command=self._toggle_width_mode,
                                   bg="#555", fg="white", font=("Helvetica", 8, "bold"),
                                   relief=tk.FLAT, padx=6, pady=2)
        self.width_btn.pack(side=tk.LEFT, padx=2)
        self.font_btn = tk.Button(btn_frame, text="Font OFF", command=self._toggle_font_mode,
                                  bg="#555", fg="white", font=("Helvetica", 8, "bold"),
                                  relief=tk.FLAT, padx=6, pady=2)
        self.font_btn.pack(side=tk.LEFT, padx=2)

        self.status_label = tk.Label(top, text="", bg=self.app.colors["bg"], fg="#888888",
                                     font=("Helvetica", 9))
        self.status_label.pack(side=tk.RIGHT, padx=8)

        # Body: collapsible searchable list (left) + equation canvas (right)
        body = tk.Frame(self, bg=self.app.colors["bg"])
        body.pack(fill=tk.BOTH, expand=True)

        self.list_frame = tk.Frame(body, bg=self.app.colors["bg"], width=240)
        self.list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        self.list_frame.pack_propagate(False)

        search_row = tk.Frame(self.list_frame, bg=self.app.colors["bg"])
        search_row.pack(fill=tk.X, pady=(0, 4))
        tk.Label(search_row, text="Search:", bg=self.app.colors["bg"], fg=self.app.colors["fg"],
                 font=("Helvetica", 9)).pack(side=tk.LEFT)
        self.list_search_var = tk.StringVar()
        self.list_search_entry = tk.Entry(search_row, textvariable=self.list_search_var,
                                          bg=self.app.colors["entry_bg"], fg=self.app.colors["fg"],
                                          insertbackground=self.app.colors["fg"],
                                          relief=tk.SOLID, bd=1, font=("Consolas", 10))
        self.list_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        self.list_search_entry.bind("<KeyRelease>", self._on_search_key)

        list_body = tk.Frame(self.list_frame, bg=self.app.colors["bg"])
        list_body.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        list_scroll = tk.Scrollbar(list_body)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        # Custom bordered-row list: a plain tk.Listbox can't give each row
        # its own border color, so the list is a scrollable Canvas holding
        # one bordered Label per node instead.
        self.list_scroll_canvas = tk.Canvas(list_body, bg=self.app.colors["bg"],
                                            highlightthickness=0, yscrollcommand=list_scroll.set)
        self.list_scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.list_scroll_canvas.yview)
        self.list_inner = tk.Frame(self.list_scroll_canvas, bg=self.app.colors["bg"])
        self._list_inner_window = self.list_scroll_canvas.create_window((0, 0), window=self.list_inner, anchor="nw")
        self.list_inner.bind("<Configure>", lambda e: self.list_scroll_canvas.configure(
            scrollregion=self.list_scroll_canvas.bbox("all")))
        self.list_scroll_canvas.bind("<Configure>", lambda e: self.list_scroll_canvas.itemconfig(
            self._list_inner_window, width=e.width))
        for seq, amt in (("<MouseWheel>", None), ("<Button-4>", -1), ("<Button-5>", 1)):
            if amt is None:
                self.list_scroll_canvas.bind(seq, self._on_list_mousewheel)
            else:
                self.list_scroll_canvas.bind(seq, lambda e, a=amt: self.list_scroll_canvas.yview_scroll(a, "units"))

        self.row_widgets = []          # one Label per currently-visible (filtered) row
        self.selected_row_widget = None
        self._assign_border_colors()

        self.list_count_label = tk.Label(self.list_frame, text="", bg=self.app.colors["bg"], fg="#888888",
                                         font=("Helvetica", 8))
        self.list_count_label.pack(anchor=tk.W, pady=(2, 0))

        self.canvas = tk.Canvas(body, bg="#1e1e2e", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        val_frame = tk.Frame(self, bg=self.app.colors["bg"])
        val_frame.pack(fill=tk.X, pady=(4, 4))
        self.val_label = tk.Label(val_frame, text="", bg=self.app.colors["bg"], fg="#00ff00",
                                  font=("Consolas", 12, "bold"))
        self.val_label.pack(side=tk.LEFT, padx=8)

        tk.Label(val_frame, text="Step:", bg=self.app.colors["bg"], fg=self.app.colors["fg"],
                 font=("Helvetica", 9)).pack(side=tk.RIGHT, padx=(8, 2))
        self.step_var = tk.IntVar(value=2)
        self.step_spin = tk.Spinbox(val_frame, from_=1, to=50, width=4,
                                    textvariable=self.step_var,
                                    bg=self.app.colors["entry_bg"], fg="#000000",
                                    font=("Consolas", 9), relief=tk.SOLID, bd=1)
        self.step_spin.pack(side=tk.RIGHT, padx=(0, 8))
        bind_mousewheel_to_spinbox(self.step_spin)

        self.mode_label = tk.Label(val_frame, text="", bg=self.app.colors["bg"], fg="#ffaa00",
                                   font=("Consolas", 10, "bold"))
        self.mode_label.pack(side=tk.RIGHT, padx=8)

        bottom = tk.Frame(self, bg=self.app.colors["bg"])
        bottom.pack(fill=tk.X, pady=(4, 4))
        tk.Button(bottom, text="Close", command=self._close,
                  bg="#e74c3c", fg="#ffffff", activebackground="#c0392b",
                  relief=tk.FLAT, padx=12, pady=4).pack(side=tk.RIGHT, padx=8)
        instruction = "Click a node in the list, or Left/Right/RMB = navigate  |  Type to search the list  |  F6 = Width  |  F7 = Font  |  XB1/4 = Width  |  XB2/5 = Font  |  Scroll = adjust"
        tk.Label(bottom, text=instruction, bg=self.app.colors["bg"],
                 fg="#888888", font=("Helvetica", 9)).pack(side=tk.LEFT, padx=8)

        self._update_info()

    def _setup_bindings(self):
        self.canvas.bind("<Configure>", lambda e: self._render_current())
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<B1-Motion>", self._on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_left_release)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<B3-Motion>", self._on_right_drag)
        self.canvas.bind("<ButtonRelease-3>", self._on_right_release)
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        # On Windows, some mouse drivers map XButtons to Button-4/5 in tkinter.
        # Use them as fallback when the low-level hook doesn't catch XButtons.
        if sys.platform == 'win32':
            self.canvas.bind("<Button-4>", self._on_xbutton1_fallback)
            self.canvas.bind("<Button-5>", self._on_xbutton2_fallback)
        else:
            self.canvas.bind("<Button-4>", self._on_linux_scroll_up)
            self.canvas.bind("<Button-5>", self._on_linux_scroll_down)
        self.bind("<Escape>", self._on_escape)
        self.bind("<Left>", self._on_left)
        self.bind("<Right>", self._on_right)
        self.bind("<F6>", lambda e: self._toggle_width_mode())
        self.bind("<F7>", lambda e: self._toggle_font_mode())
        self._setup_xbutton_listener()

    def _on_xbutton1_fallback(self, event):
        """Fallback for XButton1 when low-level hook doesn't catch it."""
        self._toggle_width_mode()
        return "break"

    def _on_xbutton2_fallback(self, event):
        """Fallback for XButton2 when low-level hook doesn't catch it."""
        self._toggle_font_mode()
        return "break"

    def _setup_xbutton_listener(self):
        if sys.platform != 'win32':
            self.status_label.config(text="XButtons not supported on this OS")
            return
        if self._hook_id is not None:
            return
        try:
            import ctypes
            from ctypes import wintypes
            WH_MOUSE_LL = 14
            WM_XBUTTONDOWN = 0x020B
            XBUTTON1 = 0x0001
            XBUTTON2 = 0x0002

            class MSLLHOOKSTRUCT(ctypes.Structure):
                _fields_ = [
                    ("pt", wintypes.POINT),
                    ("mouseData", wintypes.DWORD),
                    ("flags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.c_size_t),
                ]

            # Use a closure that captures self directly.
            # The key is that the callback must be a plain function (not method/staticmethod)
            # and must keep a strong reference to self alive.
            _panel_ref = self

            def hook_proc(nCode, wParam, lParam):
                try:
                    if nCode == 0 and wParam == WM_XBUTTONDOWN:
                        lp = ctypes.c_void_p(lParam & 0xFFFFFFFFFFFFFFFF)
                        msll = ctypes.cast(lp, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                        xbtn = (msll.mouseData >> 16) & 0xFFFF
                        print(f"[EqAdjuster Hook] XBUTTON detected: {xbtn}")
                        if xbtn == XBUTTON1:
                            print("[EqAdjuster Hook] \u2192 Toggle Width")
                            _panel_ref.app.root.after(0, _panel_ref._toggle_width_mode)
                            return 1
                        elif xbtn == XBUTTON2:
                            print("[EqAdjuster Hook] \u2192 Toggle Font")
                            _panel_ref.app.root.after(0, _panel_ref._toggle_font_mode)
                            return 1
                except Exception as e:
                    print(f"[EqAdjuster Hook] Error: {e}")
                # Fix 64-bit signed/unsigned LPARAM overflow
                lp_fixed = lParam & 0xFFFFFFFFFFFFFFFF
                if lp_fixed > 0x7FFFFFFFFFFFFFFF:
                    lp_fixed -= 0x10000000000000000
                return ctypes.windll.user32.CallNextHookEx(0, nCode, wParam, lp_fixed)

            HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)  # FIX: wintypes.LRESULT is missing on Python < 3.12
            self._hook_callback_ref = HOOKPROC(hook_proc)

            # WH_MOUSE_LL must be global (dwThreadId=0)
            hMod = ctypes.windll.kernel32.GetModuleHandleW(None)
            self._hook_id = ctypes.windll.user32.SetWindowsHookExW(
                WH_MOUSE_LL, self._hook_callback_ref, hMod, 0
            )

            if self._hook_id:
                self.status_label.config(text="XButton hooks installed")
                print("[EqAdjuster] XButton hook installed")
            else:
                self.status_label.config(text="XButton hook failed \u2013 use F6/F7")
                print("[EqAdjuster] Failed to install XButton hook (fallback: F6/F7)")
                self._hook_id = None
        except Exception as e:
            self.status_label.config(text=f"XButton hook error: {e}")
            print(f"[EqAdjuster] XButton hook error: {e}")
            self._hook_id = None

    def _remove_xbutton_hook(self):
        if self._hook_id is not None:
            try:
                import ctypes
                ctypes.windll.user32.UnhookWindowsHookEx(self._hook_id)
                print("[EqAdjuster] XButton hook removed")
            except Exception:
                pass
            self._hook_id = None
            self._hook_callback_ref = None

    def _toggle_list_visibility(self):
        self.list_visible = not self.list_visible
        if self.list_visible:
            self.list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6), before=self.canvas)
            self.list_toggle_btn.config(text="\u25c0 Hide List")
        else:
            self.list_frame.pack_forget()
            self.list_toggle_btn.config(text="\u25b6 Show List")
        self._show_tooltip(f"List {'shown' if self.list_visible else 'hidden'}")
        self.canvas.after(10, self._render_current)

    def _toggle_width_mode(self):
        self.width_mode = not self.width_mode
        self.width_btn.config(text="Width ON" if self.width_mode else "Width OFF",
                              bg="#00b4d8" if self.width_mode else "#555")
        self._show_tooltip(f"Width mode {'ON' if self.width_mode else 'OFF'}")
        self.status_label.config(text=f"Width mode {'ON' if self.width_mode else 'OFF'}")
        self._update_mode_label()

    def _toggle_font_mode(self):
        self.font_mode = not self.font_mode
        self.font_btn.config(text="Font ON" if self.font_mode else "Font OFF",
                             bg="#ff6b6b" if self.font_mode else "#555")
        self._show_tooltip(f"Font mode {'ON' if self.font_mode else 'OFF'}")
        self.status_label.config(text=f"Font mode {'ON' if self.font_mode else 'OFF'}")
        self._update_mode_label()

    def _update_mode_label(self):
        modes = []
        if self.width_mode: modes.append("Width")
        if self.font_mode: modes.append("Font")
        mode_text = " | ".join(modes) if modes else "None"
        self.mode_label.config(text=f"Modes: {mode_text}")

    def _show_tooltip(self, text):
        try:
            x = self.winfo_pointerx() - self.winfo_rootx()
            y = self.winfo_pointery() - self.winfo_rooty()
            tip = tk.Toplevel(self)
            tip.overrideredirect(True)
            tip.wm_attributes("-topmost", True)
            tip.geometry(f"+{x+15}+{y+10}")
            label = tk.Label(tip, text=text, bg="#ffffcc", relief=tk.SOLID, borderwidth=1,
                             font=("Segoe UI", 11, "bold"), padx=8, pady=4)
            label.pack()
            self.after(1500, tip.destroy)
        except Exception:
            pass

    def _assign_border_colors(self):
        # One randomized border color per node, generated fresh here. The
        # module-level random.seed() call (near the top of the file) is
        # reseeded from the current time every time the script is launched,
        # so this palette differs from run to run.
        self.node_border_colors = [_random_border_color() for _ in self.nodes]

    def _on_list_mousewheel(self, event):
        delta = getattr(event, "delta", 0)
        if delta:
            self.list_scroll_canvas.yview_scroll(int(-delta / 120) or (-1 if delta > 0 else 1), "units")
        return "break"

    # ── Search / list ──
    def _on_search_key(self, event=None):
        query = self.list_search_var.get().strip().lower()
        if query:
            self.filtered_indices = [i for i, n in enumerate(self.nodes) if query in n['heading'].lower()]
        else:
            self.filtered_indices = list(range(len(self.nodes)))
        self._refresh_listbox()
        if self.filtered_indices:
            # Jump straight to the closest (top) match, image included, as
            # requested: typing "S" shows every S-node with the first one's
            # equation on screen immediately; typing further narrows it.
            self.current_node_idx = self.filtered_indices[0]
            self._update_info()
            self._render_current()
            self._update_values_display()
            self._sync_list_selection()
        else:
            self.current_node_idx = -1
            self.info_label.config(text="No matching equations")
            self.canvas.delete("all")
            self._current_image = None
            self.val_label.config(text="")

    def _refresh_listbox(self):
        for w in self.row_widgets:
            w.destroy()
        self.row_widgets = []
        self.selected_row_widget = None

        for i in self.filtered_indices:
            node = self.nodes[i]
            border_color = self.node_border_colors[i]
            row = tk.Label(self.list_inner, text=node['heading'],
                           bg=self.app.colors["entry_bg"], fg=self.app.colors["fg"],
                           anchor="w", font=("Consolas", 9),
                           padx=8, pady=5,
                           highlightthickness=2, highlightbackground=border_color,
                           highlightcolor=border_color, bd=0)
            row.pack(fill=tk.X, padx=3, pady=2)
            row.bind("<Button-1>", lambda e, idx=i: self._select_node(idx))
            for seq, amt in (("<MouseWheel>", None), ("<Button-4>", -1), ("<Button-5>", 1)):
                if amt is None:
                    row.bind(seq, self._on_list_mousewheel)
                else:
                    row.bind(seq, lambda e, a=amt: self.list_scroll_canvas.yview_scroll(a, "units"))
            self.row_widgets.append(row)

        total = len(self.nodes)
        shown = len(self.filtered_indices)
        self.list_count_label.config(text=f"{shown} of {total} node(s)" if shown != total else f"{total} node(s)")

    def _select_node(self, idx):
        self.current_node_idx = idx
        self._update_info()
        self._render_current()
        self._update_values_display()
        self._sync_list_selection()

    def _sync_list_selection(self):
        # Reset the previously selected row back to its normal look (its
        # border color is untouched -- only the selection background changes).
        if self.selected_row_widget is not None:
            try:
                self.selected_row_widget.config(bg=self.app.colors["entry_bg"], fg=self.app.colors["fg"])
            except tk.TclError:
                pass
            self.selected_row_widget = None

        if self.current_node_idx in self.filtered_indices:
            pos = self.filtered_indices.index(self.current_node_idx)
            row = self.row_widgets[pos]
            row.config(bg="#6c5ce7", fg="#ffffff")
            self.selected_row_widget = row
            self.list_inner.update_idletasks()
            total_h = max(self.list_inner.winfo_height(), 1)
            frac = max(0.0, (row.winfo_y() / total_h) - 0.05)
            self.list_scroll_canvas.yview_moveto(frac)


    def _on_left(self, event):
        self._navigate(-1)

    def _on_right(self, event):
        self._navigate(1)

    def _navigate(self, step):
        # Navigate within whatever subset the list is currently filtered to.
        if not self.filtered_indices:
            return
        if self.current_node_idx in self.filtered_indices:
            pos = self.filtered_indices.index(self.current_node_idx)
        else:
            pos = 0
        pos = (pos + step) % len(self.filtered_indices)
        self.current_node_idx = self.filtered_indices[pos]
        self._update_info()
        self._render_current()
        self._update_values_display()
        self._sync_list_selection()

    def _on_escape(self, event=None):
        self._close()

    def _on_left_click(self, event):
        # RMB hold + LMB = previous equation (left arrow)
        if self.right_button_held:
            self._rmb_combo_active = True
            self._rmb_combo_done = True
            self._navigate(-1)
            return "break"
        self.left_click_drag = False
        self._drag_start = (event.x, event.y)

    def _on_left_drag(self, event):
        if self._drag_start is None:
            self._drag_start = (event.x, event.y)
        else:
            dx = event.x - self._drag_start[0]
            dy = event.y - self._drag_start[1]
            if abs(dx) > 5 or abs(dy) > 5:
                self.left_click_drag = True
                self.canvas_offset_x += dx
                self.canvas_offset_y += dy
                self._drag_start = (event.x, event.y)
                self._render_current()

    def _on_left_release(self, event):
        if self._rmb_combo_done:
            self._rmb_combo_done = False
            self.left_click_drag = False
            self._drag_start = None
            return
        # LMB alone does nothing; only drag-pans canvas
        self._drag_start = None
        self.left_click_drag = False

    def _on_right_click(self, event):
        self.right_button_held = True
        self._rmb_combo_active = False
        self._rmb_combo_done = False

    def _on_right_drag(self, event):
        pass

    def _on_right_release(self, event):
        self.right_button_held = False
        if self._rmb_combo_active:
            # Combo (RMB+LMB) already handled prev in _on_left_click
            self._rmb_combo_active = False
        else:
            # RMB alone → next equation (right arrow)
            self._navigate(1)
        self._rmb_combo_done = False

    def _on_scroll(self, event):
        if not self.nodes or self.current_node_idx < 0:
            return
        delta = event.delta if hasattr(event, 'delta') else 0
        step = self.step_var.get()
        step = step if delta > 0 else -step
        node = self.nodes[self.current_node_idx]
        if self.font_mode:
            new_font = max(4, node['eq_font'] + step)
            node['eq_font'] = new_font
            self.status_label.config(text=f"Font: {new_font}")
        elif self.width_mode:
            new_w = max(50, node['eq_w'] + step * 2)
            node['eq_w'] = new_w
            self.status_label.config(text=f"Width: {new_w}")
        else:
            new_h = max(30, node['eq_h'] + step * 2)
            node['eq_h'] = new_h
            self.status_label.config(text=f"Height: {new_h}")
        self._render_current()
        self._update_values_display()

    def _on_linux_scroll_up(self, event):
        if not self.nodes or self.current_node_idx < 0:
            return
        step = self.step_var.get()
        node = self.nodes[self.current_node_idx]
        if self.font_mode:
            node['eq_font'] = max(4, node['eq_font'] + step)
            self.status_label.config(text=f"Font: {node['eq_font']}")
        elif self.width_mode:
            node['eq_w'] = max(50, node['eq_w'] + step * 2)
            self.status_label.config(text=f"Width: {node['eq_w']}")
        else:
            node['eq_h'] = max(30, node['eq_h'] + step * 2)
            self.status_label.config(text=f"Height: {node['eq_h']}")
        self._render_current()
        self._update_values_display()

    def _on_linux_scroll_down(self, event):
        if not self.nodes or self.current_node_idx < 0:
            return
        step = self.step_var.get()
        node = self.nodes[self.current_node_idx]
        if self.font_mode:
            node['eq_font'] = max(4, node['eq_font'] - step)
            self.status_label.config(text=f"Font: {node['eq_font']}")
        elif self.width_mode:
            node['eq_w'] = max(50, node['eq_w'] - step * 2)
            self.status_label.config(text=f"Width: {node['eq_w']}")
        else:
            node['eq_h'] = max(30, node['eq_h'] - step * 2)
            self.status_label.config(text=f"Height: {node['eq_h']}")
        self._render_current()
        self._update_values_display()

    def _update_info(self):
        if self.nodes and self.current_node_idx >= 0:
            node = self.nodes[self.current_node_idx]
            addr = "".join(f"lvl{lvl}[{idx}]" for lvl, idx in node['path'])
            total = len(self.nodes)
            self.info_label.config(text=f"{addr}  |  {node['heading']}  ({self.current_node_idx+1}/{total})")
        else:
            self.info_label.config(text="No equations found")

    def _update_values_display(self):
        if self.nodes and self.current_node_idx >= 0:
            node = self.nodes[self.current_node_idx]
            self.val_label.config(
                text=f"Font: {node['eq_font']}  |  Width: {node['eq_w']}  |  Height: {node['eq_h']}"
            )
        else:
            self.val_label.config(text="")

    def _render_current(self):
        self.canvas.delete("all")
        self._current_image = None
        if not self.nodes or self.current_node_idx < 0:
            return
        node = self.nodes[self.current_node_idx]
        eq_latex = node['equation']
        eq_w = node.get('eq_w', DEFAULT_EQ_W)
        eq_h = node.get('eq_h', DEFAULT_EQ_H)
        eq_font = node.get('eq_font', DEFAULT_EQ_FONT)

        try:
            img_bytes = XMindBuilder.render_equation(eq_latex, fontsize=eq_font,
                                                     text_color="white", bg_color="black",
                                                     fmt="png", width=eq_w, height=eq_h)
            img = Image.open(io.BytesIO(img_bytes))
            zoom = self.canvas_zoom
            display_w = int(eq_w * zoom * 0.8)
            display_h = int(eq_h * zoom * 0.8)
            if display_w < 10 or display_h < 10:
                display_w = 20
                display_h = 20

            # Clamp to the visible canvas so large equations scale down to
            # fit instead of clipping past the canvas edges. Leave margin for
            # the border and the heading label drawn below.
            canvas_w = max(self.canvas.winfo_width(), 100)
            canvas_h = max(self.canvas.winfo_height(), 100)
            max_w = canvas_w - 60
            max_h = canvas_h - 90
            if display_w > max_w or display_h > max_h:
                fit_scale = min(max_w / display_w, max_h / display_h)
                display_w = max(20, int(display_w * fit_scale))
                display_h = max(20, int(display_h * fit_scale))

            img = img.resize((display_w, display_h), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._current_image = photo

            cx = self.canvas.winfo_width() // 2 + self.canvas_offset_x
            cy = self.canvas.winfo_height() // 2 + self.canvas_offset_y
            self.canvas.create_image(cx, cy, image=photo, anchor=tk.CENTER)

            self.canvas.create_rectangle(
                cx - display_w//2 - 4, cy - display_h//2 - 4,
                cx + display_w//2 + 4, cy + display_h//2 + 4,
                outline="#4a90d9", width=2
            )
            self.canvas.create_text(cx, cy + display_h//2 + 25, text=node['heading'],
                                    fill="white", font=("Consolas", int(10*zoom)))
        except Exception as e:
            print(f"Render error for {node['heading']}: {e}")
            self.canvas.create_text(self.canvas.winfo_width()//2, self.canvas.winfo_height()//2,
                                    text="[Render Error]", fill="red", font=("Consolas", 20))

    def _close(self):
        self._remove_xbutton_hook()
        if self.close_callback:
            self.close_callback(self.nodes)
        self.destroy()

# ============================================================
# Main App
# ============================================================
class MindMapExporterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MindMap -> .xmind Exporter (M3-87)")
        self.root.state("zoomed")
        self.root.minsize(1400, 800)

        self.dark_colors = {
            "bg": "#1e1e2e",
            "fg": "#cdd6f4",
            "input_bg": "#2d2d44",
            "input_fg": "#cdd6f4",
            "accent": "#313244",
            "btn_bg": "#b4befe",
            "btn_fg": "#000000",
            "frame_bg": "#181825",
            "entry_bg": "#313244",
            "select": "#6c5ce7",
        }
        self.light_colors = {
            "bg": "#f8f9fa",
            "fg": "#212529",
            "input_bg": "#ffffff",
            "input_fg": "#212529",
            "accent": "#e9ecef",
            "btn_bg": "#dee2e6",
            "btn_fg": "#000000",
            "frame_bg": "#ffffff",
            "entry_bg": "#ffffff",
            "select": "#6c5ce7",
        }
        self._is_dark = True
        self.colors = self.dark_colors

        paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg=self.colors["bg"], sashwidth=4, sashrelief=tk.RAISED)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = tk.Frame(paned, bg=self.colors["bg"])
        paned.add(left, minsize=850)

        self.left_title = tk.Label(left,
            text="Hierarchy Data  —  lvlN[I] = cumulative path (lvl1[1] is root)",
            font=("Helvetica", 11, "bold"), bg=self.colors["bg"], fg=self.colors["fg"])
        self.left_title.pack(anchor=tk.W, pady=(0, 4))

        # Search bar
        self.search_frame = tk.Frame(left, bg=self.colors["bg"])
        self.search_entry = tk.Entry(self.search_frame, width=30,
                                     bg=self.colors["entry_bg"], fg=self.colors["fg"],
                                     insertbackground=self.colors["fg"],
                                     relief=tk.SOLID, bd=1, font=("Consolas", 10))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 4))
        self.search_entry.bind("<Return>", lambda e: self._search_find_all())
        self.search_btn = tk.Button(self.search_frame, text="Find All", command=self._search_find_all,
                                    bg="#6c5ce7", fg="#ffffff", activebackground="#a29bfe",
                                    relief=tk.FLAT, cursor="hand2", font=("Helvetica", 8, "bold"))
        self.search_btn.pack(side=tk.LEFT, padx=1)
        self.search_next_btn = tk.Button(self.search_frame, text="Next", command=self._search_next,
                                         bg="#0984e3", fg="#ffffff", activebackground="#74b9ff",
                                         relief=tk.FLAT, cursor="hand2", font=("Helvetica", 8))
        self.search_next_btn.pack(side=tk.LEFT, padx=1)
        self.search_prev_btn = tk.Button(self.search_frame, text="Prev", command=self._search_prev,
                                         bg="#0984e3", fg="#ffffff", activebackground="#74b9ff",
                                         relief=tk.FLAT, cursor="hand2", font=("Helvetica", 8))
        self.search_prev_btn.pack(side=tk.LEFT, padx=1)
        self.search_clear_btn = tk.Button(self.search_frame, text="Clear", command=self._search_clear,
                                          bg="#e74c3c", fg="#ffffff", activebackground="#ff6b6b",
                                          relief=tk.FLAT, cursor="hand2", font=("Helvetica", 8))
        self.search_clear_btn.pack(side=tk.LEFT, padx=1)
        self.search_status = tk.Label(self.search_frame, text="", bg=self.colors["bg"], fg="#888888",
                                      font=("Helvetica", 8))
        self.search_status.pack(side=tk.LEFT, padx=(8, 0))

        # Editor container (holds text or manual mode or eq adjuster)
        self.editor_container = tk.Frame(left, bg=self.colors["bg"])
        self.editor_container.pack(fill=tk.BOTH, expand=True)

        # The main text area (initially visible)
        self.input_text = RTFScrolledText(
            self.editor_container, wrap=tk.WORD, rtf_font=("Consolas", 11),
            rtf_bg=self.colors["input_bg"], rtf_fg=self.colors["input_fg"],
            insertbackground=self.colors["input_fg"],
            relief=tk.FLAT, padx=6, pady=6,
            bg=self.colors["bg"]
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        self.input_text.text.bind("<KeyRelease>", lambda e: self._update_level_counts())
        self.input_text.text.bind("<Control-f>", lambda e: self.search_entry.focus_set())

        # This frame will be used for the eq adjuster panel (hidden initially)
        self.eq_adjust_frame = None

        sample = """<h1>Paste or type your hierarchy here...</h1>

Format:
    lvl1[1]Root Title{note:"optional note", label:"tag1,tag2", fill:"#hex", text:"#hex", line:"#hex", border:"#hex"}
    lvl2[1]Main Topic
    lvl3[1]Subtopic
    lvl2[2]Another Main Topic

<strong>First entry MUST be lvl1[1]</strong> — it becomes the root node.

<h3>Equation tags (M3-87):</h3>
equation:"\\Delta G = \\Delta H - T \\Delta S"
eq_w:200 eq_h:100 | eq_color:"white" eq_bg:"none" | eq_font:50 | img_fmt:"jpg" (default)

<h3>Right-panel checkboxes:</h3>
☑ H1  → wraps every note with &lt;h1&gt; tags
☑ Bold → wraps every note with &lt;strong&gt; tags

<h3>Supported tags:</h3>
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<h3>Heading 3</h3>
<strong>Bold</strong> | <i>Italic</i> | <u>Underline</u>"""
        self.input_text.setRTF(sample)

        self.input_text.text.tag_configure("search_highlight", background="#ffff00", foreground="#000000")
        self._search_matches = []
        self._search_current = -1

        # Field-highlighting tags for Normal-mode hierarchy text: each
        # line's address ("lvl1[1]lvl2[3]..."), node name, and note/
        # equation/label field values get a distinct background so the
        # structure of a pasted (or Manual-mode-generated) line is easy
        # to read at a glance.
        self.input_text.text.tag_configure("hl_address", background="#000000", foreground="#ffffff")
        self.input_text.text.tag_configure("hl_nodename", background="#B9D9EB", foreground="#000000")
        self.input_text.text.tag_configure("hl_note", background="#C6F5C6", foreground="#000000")
        self.input_text.text.tag_configure("hl_equation", background="#4F38A7", foreground="#ffffff")
        self.input_text.text.tag_configure("hl_label", background="#FFF6B3", foreground="#000000")
        self.input_text.text.tag_raise("search_highlight")
        self.input_text.text.bind("<<Modified>>", self._on_input_text_modified)
        self._colorize_input_text()

        # Manual mode toggle
        manual_bar = tk.Frame(left, bg=self.colors["bg"])
        manual_bar.pack(fill=tk.X, pady=(0, 4))
        self.manual_mode_var = tk.BooleanVar(value=False)
        self.manual_btn = tk.Button(
            manual_bar, text="📝 Manual", command=self._toggle_manual_mode,
            bg="#6c5ce7", fg="#ffffff", activebackground="#a29bfe",
            font=("Helvetica", 13, "bold"), relief=tk.RAISED, padx=16, pady=6,
            cursor="hand2", bd=3
        )
        self.manual_btn.pack(side=tk.LEFT)
        self.manual_status = tk.Label(
            manual_bar, text="Normal Mode — type or paste hierarchy text freely",
            bg=self.colors["bg"], fg="#888888", font=("Helvetica", 9)
        )
        self.manual_status.pack(side=tk.LEFT, padx=(8, 0))

        # Eq Adjust button (far right)
        self.eq_adjust_btn = tk.Button(
            manual_bar, text="Eq Adjust", command=self._toggle_eq_adjuster,
            bg="#555555", fg="#888888", state=tk.DISABLED,
            font=("Helvetica", 10, "bold"), relief=tk.RAISED, padx=10, pady=4,
            cursor="hand2", bd=2
        )
        self.eq_adjust_btn.pack(side=tk.RIGHT, padx=(8, 0))

        self.manual_editor = None
        self.search_frame.pack(fill=tk.X, pady=(0, 2), before=self.manual_btn.master)

        bottom_bar = tk.Frame(left, bg=self.colors["bg"])
        bottom_bar.pack(fill=tk.X, pady=(6, 0))

        # level_counts_frame is packed directly into bottom_bar (not inside
        # bf_container) so it forms its own full-width row across the very
        # top of bottom_bar, above everything else. Its height starts at a
        # single line -- the normal case, since nearly all real maps only
        # have a handful of levels -- and _reflow_level_labels() grows it
        # (and shrinks it back) adaptively as content actually needs more
        # wrapped rows, e.g. the 50-level stress-test case. It's only ever
        # resized when the needed row count actually changes, not on every
        # keystroke, so bf_container below it doesn't jump/blink in the
        # common case where the level count doesn't change.
        self.level_counts_frame = tk.Frame(bottom_bar, bg=self.colors["bg"],
                                            height=22)
        self.level_counts_frame.pack(side=tk.TOP, anchor="w", fill=tk.X, pady=(0, 2))
        self.level_counts_frame.pack_propagate(False)
        self.level_counts_frame.bind("<Configure>", self._reflow_level_labels)
        self.level_count_labels = {}

        # bf_container stacks, top to bottom: the Copy/Paste/Clear/... button
        # row (bf), then the Total Nodes label -- packed below the level
        # counts row (left, top), separate from ef (the Export box beside
        # it).
        bf_container = tk.Frame(bottom_bar, bg=self.colors["bg"])
        bf_container.pack(side=tk.LEFT, anchor="s")  # "s" = bottom, "w" = left

        bf = tk.Frame(bf_container, bg=self.colors["bg"])
        bf.pack(side=tk.TOP, anchor="w")
        self.bf_buttons_frame = bf

        def make_btn(parent, text, cmd):
            return tk.Button(parent, text=text, command=cmd,
                bg=self.colors["btn_bg"], fg="#000000",
                activebackground=self.colors["accent"], activeforeground="#000000",
                relief=tk.FLAT, cursor="hand2", font=("Helvetica", 9))

        make_btn(bf, "📄 Copy", self._copy_raw).pack(side=tk.LEFT, padx=2)
        make_btn(bf, "📋 Paste", self._paste).pack(side=tk.LEFT, padx=2)
        make_btn(bf, "🗑 Clear", self._clear).pack(side=tk.LEFT, padx=2)
        make_btn(bf, "📂 Load", self._load).pack(side=tk.LEFT, padx=2)
        make_btn(bf, "🔍 Detect Levels", self._detect_levels).pack(side=tk.LEFT, padx=2)
        make_btn(bf, "➕", self._add_node).pack(side=tk.LEFT, padx=2)
        make_btn(bf, "➖", self._remove_node).pack(side=tk.LEFT, padx=2)

        # Total Nodes label: same font/color as the lvl count labels above,
        # centered under the button row, inside bf_container -- not under
        # the Export box beside it.
        self.total_nodes_var = tk.StringVar(value="Total Nodes: 0")
        self.total_nodes_label = tk.Label(
            bf_container, textvariable=self.total_nodes_var,
            bg=self.colors["bg"], fg="#888888",
            font=("Consolas", 9)
        )
        self.total_nodes_label.pack(side=tk.TOP, anchor="center", pady=(2, 0))
        self._update_level_counts()

        ef = tk.LabelFrame(bottom_bar, text=" Export ",
                           bg=self.colors["bg"], fg=self.colors["fg"],
                           font=("Helvetica", 9, "bold"), padx=8, pady=6)
        ef.pack(side=tk.RIGHT, anchor="n", padx=(6, 0))  # anchor="n" keeps it at top

        btn_font = ("Helvetica", 11, "bold")
        opt_font = ("Helvetica", 9)

        btn_row = tk.Frame(ef, bg=self.colors["bg"])
        btn_row.pack(fill=tk.X, pady=(0, 2))
        tk.Button(btn_row, text="👁  Preview", command=self._preview,
                  bg="#6c5ce7", fg="#ffffff", activebackground="#a29bfe",
                  font=btn_font, relief=tk.FLAT, padx=20, pady=6,
                  cursor="hand2").pack(side=tk.LEFT, padx=3, fill=tk.Y, expand=True)
        tk.Button(btn_row, text="📤  Export", command=self._export,
                  bg="#00b894", fg="#ffffff", activebackground="#55efc4",
                  font=btn_font, relief=tk.FLAT, padx=20, pady=6,
                  cursor="hand2").pack(side=tk.LEFT, padx=3, fill=tk.Y, expand=True)
        tk.Button(btn_row, text="📋  Copy", command=self._copy_to_clipboard,
                  bg="#0984e3", fg="#ffffff", activebackground="#74b9ff",
                  font=btn_font, relief=tk.FLAT, padx=20, pady=6,
                  cursor="hand2").pack(side=tk.LEFT, padx=3, fill=tk.Y, expand=True)

        opt_row = tk.Frame(ef, bg=self.colors["bg"])
        opt_row.pack(fill=tk.X, pady=(2, 0))

        preview_delay_frame = tk.Frame(opt_row, bg=self.colors["bg"])
        preview_delay_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
        tk.Label(preview_delay_frame, text="🕐 Auto-delete in ",
                 bg=self.colors["bg"], fg="#888888",
                 font=opt_font).pack(side=tk.LEFT)
        self._delay_seconds = 30
        self.preview_delay_var = tk.StringVar(value="30 seconds")
        self.preview_delay_spin = tk.Spinbox(
            preview_delay_frame, width=14,
            textvariable=self.preview_delay_var,
            bg=self.colors["entry_bg"], fg="#000000",
            font=("Consolas", 9), relief=tk.SOLID, bd=1,
            state="readonly"
        )
        self.preview_delay_spin.pack(side=tk.LEFT, padx=(2, 2))

        def _on_delay_wheel(event):
            if event.delta > 0:
                self._delay_seconds = self._next_delay_up(self._delay_seconds)
            elif event.delta < 0:
                self._delay_seconds = self._next_delay_down(self._delay_seconds)
            self.preview_delay_var.set(self._format_delay(self._delay_seconds))
            return "break"

        def _on_linux_delay_up(event):
            self._delay_seconds = self._next_delay_up(self._delay_seconds)
            self.preview_delay_var.set(self._format_delay(self._delay_seconds))
            return "break"

        def _on_linux_delay_down(event):
            self._delay_seconds = self._next_delay_down(self._delay_seconds)
            self.preview_delay_var.set(self._format_delay(self._delay_seconds))
            return "break"

        self.preview_delay_spin.bind("<MouseWheel>", _on_delay_wheel)
        self.preview_delay_spin.bind("<Button-4>", _on_linux_delay_up)
        self.preview_delay_spin.bind("<Button-5>", _on_linux_delay_down)

        def _format_delay(sec):
            if sec < 60:
                return f"{sec} seconds"
            elif sec == 60:
                return "1 minute"
            else:
                mins = sec / 60
                if mins == int(mins):
                    return f"{int(mins)} minutes"
                else:
                    return f"{mins} minutes"

        def _next_delay_up(sec):
            if sec < 60:
                steps = [10, 20, 30, 40, 50, 60]
                for s in steps:
                    if s > sec:
                        return s
                return 60
            else:
                mins = sec / 60
                next_mins = mins + 0.5
                return int(next_mins * 60)

        def _next_delay_down(sec):
            if sec <= 10:
                return 10
            if sec <= 60:
                steps = [60, 50, 40, 30, 20, 10]
                for s in steps:
                    if s < sec:
                        return s
                return 10
            else:
                mins = sec / 60
                next_mins = max(1.0, mins - 0.5)
                return int(next_mins * 60)

        self._format_delay = _format_delay
        self._next_delay_up = _next_delay_up
        self._next_delay_down = _next_delay_down

        open_after_frame = tk.Frame(opt_row, bg=self.colors["bg"])
        open_after_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
        self.open_after_export_var = tk.BooleanVar(value=False)
        tk.Checkbutton(open_after_frame, text="Open after export",
                       variable=self.open_after_export_var,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"],
                       selectcolor=self.colors["select"],
                       font=opt_font).pack(side=tk.LEFT)

        spacer_frame = tk.Frame(opt_row, bg=self.colors["bg"])
        spacer_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)

        self.status_var = tk.StringVar(value="Ready — lvl1[1] becomes root")
        self.status_lbl = tk.Label(ef, textvariable=self.status_var,
                  justify=tk.CENTER, bg=self.colors["bg"], fg="#888888",
                  font=("Helvetica", 8))
        self.status_lbl.pack(fill=tk.X, pady=(4, 0))

        # Right panel (unchanged)
        right = tk.Frame(paned, bg=self.colors["bg"])
        paned.add(right, minsize=720)

        right_canvas = tk.Canvas(right, bg=self.colors["bg"], highlightthickness=0)
        right_sb = tk.Scrollbar(right, orient=tk.VERTICAL, command=right_canvas.yview,
                                bg=self.colors["accent"], troughcolor=self.colors["bg"],
                                activebackground=self.colors["select"])
        right_canvas.configure(yscrollcommand=right_sb.set)
        right_sb.pack(side=tk.RIGHT, fill=tk.Y)
        right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_content = tk.Frame(right_canvas, bg=self.colors["bg"])
        right_content_window = right_canvas.create_window((0, 0), window=right_content, anchor="nw")

        def _on_right_content_configure(event=None):
            right_canvas.configure(scrollregion=right_canvas.bbox("all"))

        def _on_right_canvas_configure(event=None):
            canvas_width = event.width if event else right_canvas.winfo_width()
            if canvas_width > 1:
                right_canvas.itemconfig(right_content_window, width=canvas_width - 4)

        right_content.bind("<Configure>", _on_right_content_configure)
        right_canvas.bind("<Configure>", _on_right_canvas_configure)

        def _on_right_mousewheel(event):
            if event.delta > 0:
                right_canvas.yview_scroll(-3, "units")
            elif event.delta < 0:
                right_canvas.yview_scroll(3, "units")
            return "break"

        def _on_right_linux_up(event):
            right_canvas.yview_scroll(-3, "units")
            return "break"

        def _on_right_linux_down(event):
            right_canvas.yview_scroll(3, "units")
            return "break"

        right_canvas.bind("<MouseWheel>", _on_right_mousewheel)
        right_canvas.bind("<Button-4>", _on_right_linux_up)
        right_canvas.bind("<Button-5>", _on_right_linux_down)
        right_content.bind("<MouseWheel>", _on_right_mousewheel)
        right_content.bind("<Button-4>", _on_right_linux_up)
        right_content.bind("<Button-5>", _on_right_linux_down)

        theme_frame = tk.Frame(right_content, bg=self.colors["bg"])
        theme_frame.pack(fill=tk.X, pady=(0, 8))
        self.theme_btn = tk.Button(
            theme_frame, text="◐  Toggle Theme", command=self._toggle_theme,
            bg="#6c5ce7", fg="#ffffff", activebackground="#a29bfe",
            font=("Helvetica", 10, "bold"), relief=tk.FLAT, padx=10, pady=4, cursor="hand2"
        )
        self.theme_btn.pack(fill=tk.X)

        lay = tk.LabelFrame(right_content, text=" Structure / Layout ",
                            bg=self.colors["bg"], fg=self.colors["fg"],
                            font=("Helvetica", 9, "bold"), padx=8, pady=8)
        lay.pack(fill=tk.X, pady=(0, 8))

        cat_frame = tk.Frame(lay, bg=self.colors["bg"])
        cat_frame.pack(fill=tk.X, pady=(0, 4))
        tk.Label(cat_frame, text="Structure:", bg=self.colors["bg"], fg=self.colors["fg"], font=("Helvetica", 9)).pack(side=tk.LEFT)
        self.cat_var = tk.StringVar(value="Logic Chart")
        self.cat_combo = tk.OptionMenu(cat_frame, self.cat_var, *list(STRUCTURE_DEFS.keys()), command=self._on_cat_change)
        self._style_app_dropdown(self.cat_combo, self.cat_var, list(STRUCTURE_DEFS.keys()))
        self.cat_combo.pack(side=tk.LEFT, padx=(4, 0), fill=tk.X, expand=True)

        sub_frame = tk.Frame(lay, bg=self.colors["bg"])
        sub_frame.pack(fill=tk.X, pady=(4, 0))
        tk.Label(sub_frame, text="Type:", bg=self.colors["bg"], fg=self.colors["fg"], font=("Helvetica", 9)).pack(side=tk.LEFT)
        self.sub_var = tk.StringVar(value="Right")
        self.sub_combo = tk.OptionMenu(sub_frame, self.sub_var, "Right", command=self._on_sub_change)
        self._style_app_dropdown(self.sub_combo, self.sub_var, ["Right"])
        self.sub_combo.pack(side=tk.LEFT, padx=(4, 0), fill=tk.X, expand=True)
        self._update_sub_combo()

        bgf = tk.LabelFrame(right_content, text=" Canvas Background ",
                            bg=self.colors["bg"], fg=self.colors["fg"],
                            font=("Helvetica", 9, "bold"), padx=8, pady=8)
        bgf.pack(fill=tk.X, pady=(0, 8))

        bg_row = tk.Frame(bgf, bg=self.colors["bg"])
        bg_row.pack(fill=tk.X)
        tk.Label(bg_row, text="Color:", bg=self.colors["bg"], fg=self.colors["fg"], font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.map_bg_var = tk.StringVar(value=DEFAULT_MAP_BG)
        tk.Entry(bg_row, textvariable=self.map_bg_var, width=8,
                 bg=self.colors["entry_bg"], fg="#000000", insertbackground="#000000",
                 relief=tk.SOLID, bd=1, font=("Consolas", 9)).pack(side=tk.LEFT)
        self.map_bg_prev = tk.Label(bg_row, text="  ", bg=DEFAULT_MAP_BG, relief=tk.RIDGE, width=2)
        self.map_bg_prev.pack(side=tk.LEFT, padx=2)
        tk.Button(bg_row, text="🎨", width=2, command=self._pick_map_bg,
                  bg=self.colors["btn_bg"], fg="#000000", activebackground=self.colors["accent"],
                  relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(bg_row, text="🎲 Randomize BG", command=self._randomize_map_bg,
                  bg="#6c5ce7", fg="#ffffff", activebackground="#a29bfe",
                  relief=tk.FLAT, cursor="hand2", font=("Helvetica", 8, "bold")).pack(side=tk.LEFT, padx=(8, 2))
        self.map_bg_var.trace_add("write", lambda *args: self._update_map_bg())

        # Color Capacity Section
        capf = tk.LabelFrame(right_content, text=" Color Capacity Section ",
                             bg=self.colors["bg"], fg=self.colors["fg"],
                             font=("Helvetica", 9, "bold"), padx=8, pady=8)
        capf.pack(fill=tk.X, pady=(0, 8))

        def _make_cap_row(parent, label_text, check_default, min_default, max_default):
            row = tk.Frame(parent, bg=self.colors["bg"])
            row.pack(fill=tk.X, pady=(2, 2))
            var = tk.BooleanVar(value=check_default)
            chk = tk.Checkbutton(row, text=label_text, variable=var,
                                 bg=self.colors["bg"], fg=self.colors["fg"],
                                 activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                                 font=("Helvetica", 9))
            chk.pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(row, text="MIN:", bg=self.colors["bg"], fg=self.colors["fg"],
                     font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(0, 2))
            min_var = tk.IntVar(value=min_default)
            min_spin = tk.Spinbox(row, from_=0, to=100, width=4,
                                  textvariable=min_var,
                                  bg=self.colors["entry_bg"], fg="#000000",
                                  font=("Consolas", 9), relief=tk.SOLID, bd=1)
            min_spin.pack(side=tk.LEFT, padx=(0, 6))
            bind_mousewheel_to_spinbox(min_spin)
            tk.Label(row, text="MAX:", bg=self.colors["bg"], fg=self.colors["fg"],
                     font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(0, 2))
            max_var = tk.IntVar(value=max_default)
            max_spin = tk.Spinbox(row, from_=0, to=100, width=4,
                                  textvariable=max_var,
                                  bg=self.colors["entry_bg"], fg="#000000",
                                  font=("Consolas", 9), relief=tk.SOLID, bd=1)
            max_spin.pack(side=tk.LEFT, padx=(0, 2))
            bind_mousewheel_to_spinbox(max_spin)
            return var, min_var, max_var

        self.cap_fill_chk, self.cap_fill_min, self.cap_fill_max = _make_cap_row(
            capf, "Fill", False, 50, 100)
        self.cap_border_chk, self.cap_border_min, self.cap_border_max = _make_cap_row(
            capf, "Border", False, 50, 100)
        self.cap_line_chk, self.cap_line_min, self.cap_line_max = _make_cap_row(
            capf, "Line", True, 75, 100)

        h_row = tk.Frame(capf, bg=self.colors["bg"])
        h_row.pack(fill=tk.X, pady=(2, 2))
        self.note_heading_var = tk.BooleanVar(value=True)
        self.h1_chk = tk.Checkbutton(h_row, text="H1",
                                     variable=self.note_heading_var,
                                     bg=self.colors["bg"], fg=self.colors["fg"],
                                     activebackground=self.colors["bg"],
                                     selectcolor=self.colors["select"],
                                     font=("Helvetica", 9))
        self.h1_chk.pack(side=tk.LEFT, padx=(0, 8))
        self.note_bold_var = tk.BooleanVar(value=False)
        self.bold_chk = tk.Checkbutton(h_row, text="Bold",
                                       variable=self.note_bold_var,
                                       bg=self.colors["bg"], fg=self.colors["fg"],
                                       activebackground=self.colors["bg"],
                                       selectcolor=self.colors["select"],
                                       font=("Helvetica", 9))
        self.bold_chk.pack(side=tk.LEFT, padx=(0, 4))
        self.field_highlight_var = tk.BooleanVar(value=False)
        self.field_highlight_chk = tk.Checkbutton(
            h_row, text="Field Colors", variable=self.field_highlight_var,
            command=lambda: self._colorize_input_text(),
            bg=self.colors["bg"], fg=self.colors["fg"],
            activebackground=self.colors["bg"],
            selectcolor=self.colors["select"],
            font=("Helvetica", 9))
        self.field_highlight_chk.pack(side=tk.LEFT, padx=(0, 4))

        # Equations Design Section
        eqf = tk.LabelFrame(right_content, text=" Equations Design Section ",
                             bg=self.colors["bg"], fg=self.colors["fg"],
                             font=("Helvetica", 9, "bold"), padx=8, pady=8)
        eqf.pack(fill=tk.X, pady=(0, 8))

        eq_override_row = tk.Frame(eqf, bg=self.colors["bg"])
        eq_override_row.pack(fill=tk.X, pady=(0, 6))
        self.eq_override_var = tk.BooleanVar(value=False)
        self.eq_override_chk = tk.Checkbutton(
            eq_override_row, text="Override All Equations",
            variable=self.eq_override_var,
            bg=self.colors["bg"], fg=self.colors["fg"],
            activebackground=self.colors["bg"], selectcolor=self.colors["select"],
            font=("Helvetica", 9, "bold"))
        self.eq_override_chk.pack(side=tk.LEFT)
        tk.Label(eq_override_row, text="  ← toggles all individual overrides below",
                 bg=self.colors["bg"], fg="#888888", font=("Helvetica", 8)).pack(side=tk.LEFT)

        override_frame = tk.Frame(eqf, bg=self.colors["bg"])
        override_frame.pack(fill=tk.X, pady=(2, 4))

        self.eq_color_override = tk.BooleanVar(value=True)
        self.eq_bg_override = tk.BooleanVar(value=True)
        self.eq_w_override = tk.BooleanVar(value=False)
        self.eq_h_override = tk.BooleanVar(value=False)
        self.eq_font_override = tk.BooleanVar(value=False)
        self.eq_fmt_override = tk.BooleanVar(value=True)

        self._eq_syncing = False

        def _sync_master(*args):
            if self._eq_syncing:
                return
            self._eq_syncing = True
            try:
                master = self.eq_override_var.get()
                self.eq_color_override.set(master)
                self.eq_bg_override.set(master)
                self.eq_w_override.set(master)
                self.eq_h_override.set(master)
                self.eq_font_override.set(master)
                self.eq_fmt_override.set(master)
            finally:
                self._eq_syncing = False

        def _sync_individual(*args):
            if self._eq_syncing:
                return
            self._eq_syncing = True
            try:
                all_true = (self.eq_color_override.get() and self.eq_bg_override.get() and
                            self.eq_w_override.get() and self.eq_h_override.get() and
                            self.eq_font_override.get() and self.eq_fmt_override.get())
                self.eq_override_var.set(all_true)
            finally:
                self._eq_syncing = False

        self.eq_override_var.trace_add("write", _sync_master)
        self.eq_color_override.trace_add("write", _sync_individual)
        self.eq_bg_override.trace_add("write", _sync_individual)
        self.eq_w_override.trace_add("write", _sync_individual)
        self.eq_h_override.trace_add("write", _sync_individual)
        self.eq_font_override.trace_add("write", _sync_individual)
        self.eq_fmt_override.trace_add("write", _sync_individual)

        cb_frame = tk.Frame(override_frame, bg=self.colors["bg"])
        cb_frame.pack(fill=tk.X)

        tk.Checkbutton(cb_frame, text="Color", variable=self.eq_color_override,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 8)).pack(side=tk.LEFT, padx=3)
        tk.Checkbutton(cb_frame, text="BG", variable=self.eq_bg_override,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 8)).pack(side=tk.LEFT, padx=3)
        tk.Checkbutton(cb_frame, text="Width", variable=self.eq_w_override,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 8)).pack(side=tk.LEFT, padx=3)
        tk.Checkbutton(cb_frame, text="Height", variable=self.eq_h_override,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 8)).pack(side=tk.LEFT, padx=3)
        tk.Checkbutton(cb_frame, text="Font", variable=self.eq_font_override,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 8)).pack(side=tk.LEFT, padx=3)
        tk.Checkbutton(cb_frame, text="Format", variable=self.eq_fmt_override,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 8)).pack(side=tk.LEFT, padx=3)

        eq_color_row = tk.Frame(eqf, bg=self.colors["bg"])
        eq_color_row.pack(fill=tk.X, pady=(2, 2))
        tk.Label(eq_color_row, text="Text:", bg=self.colors["bg"], fg=self.colors["fg"],
                 font=("Helvetica", 9), width=6, anchor="w").pack(side=tk.LEFT)
        self.eq_color_var = tk.StringVar(value="white")
        tk.Entry(eq_color_row, textvariable=self.eq_color_var, width=8,
                 bg=self.colors["entry_bg"], fg="#000000",
                 relief=tk.SOLID, bd=1, font=("Consolas", 9)).pack(side=tk.LEFT, padx=(0, 2))
        self.eq_color_prev = tk.Label(eq_color_row, text="", bg="white", relief=tk.RIDGE, width=2)
        self.eq_color_prev.pack(side=tk.LEFT, padx=(0, 8))
        self.eq_color_prev.bind("<Button-1>", lambda e: self._pick_eq_color())
        self.eq_color_var.trace_add("write", lambda *args: self._update_eq_color_swatch())

        tk.Label(eq_color_row, text="BG:", bg=self.colors["bg"], fg=self.colors["fg"],
                 font=("Helvetica", 9), width=4, anchor="w").pack(side=tk.LEFT)
        self.eq_bg_var = tk.StringVar(value="black")
        tk.Entry(eq_color_row, textvariable=self.eq_bg_var, width=8,
                 bg=self.colors["entry_bg"], fg="#000000",
                 relief=tk.SOLID, bd=1, font=("Consolas", 9)).pack(side=tk.LEFT, padx=(0, 2))
        self.eq_bg_prev = tk.Label(eq_color_row, text="", bg="black", relief=tk.RIDGE, width=2)
        self.eq_bg_prev.pack(side=tk.LEFT, padx=(0, 2))
        self.eq_bg_prev.bind("<Button-1>", lambda e: self._pick_eq_bg())
        self.eq_bg_var.trace_add("write", lambda *args: self._update_eq_bg_swatch())

        eq_size_row = tk.Frame(eqf, bg=self.colors["bg"])
        eq_size_row.pack(fill=tk.X, pady=(2, 2))

        tk.Label(eq_size_row, text="W:", bg=self.colors["bg"], fg=self.colors["fg"],
                 font=("Helvetica", 9)).pack(side=tk.LEFT)
        self.eq_w_var = tk.IntVar(value=DEFAULT_EQ_W)
        eq_w_spin = tk.Spinbox(eq_size_row, from_=50, to=800, width=5,
                               textvariable=self.eq_w_var,
                               bg=self.colors["entry_bg"], fg="#000000",
                               font=("Consolas", 9), relief=tk.SOLID, bd=1)
        eq_w_spin.pack(side=tk.LEFT, padx=(2, 8))
        bind_mousewheel_to_spinbox(eq_w_spin)

        tk.Label(eq_size_row, text="H:", bg=self.colors["bg"], fg=self.colors["fg"],
                 font=("Helvetica", 9)).pack(side=tk.LEFT)
        self.eq_h_var = tk.IntVar(value=DEFAULT_EQ_H)
        eq_h_spin = tk.Spinbox(eq_size_row, from_=30, to=300, width=5,
                               textvariable=self.eq_h_var,
                               bg=self.colors["entry_bg"], fg="#000000",
                               font=("Consolas", 9), relief=tk.SOLID, bd=1)
        eq_h_spin.pack(side=tk.LEFT, padx=(2, 8))
        bind_mousewheel_to_spinbox(eq_h_spin)

        tk.Label(eq_size_row, text="Font:", bg=self.colors["bg"], fg=self.colors["fg"],
                 font=("Helvetica", 9)).pack(side=tk.LEFT)
        self.eq_font_var = tk.IntVar(value=DEFAULT_EQ_FONT)
        eq_font_spin = tk.Spinbox(eq_size_row, from_=1, to=999, width=5,
                                  textvariable=self.eq_font_var,
                                  bg=self.colors["entry_bg"], fg="#000000",
                                  font=("Consolas", 9), relief=tk.SOLID, bd=1)
        eq_font_spin.pack(side=tk.LEFT, padx=(2, 8))
        bind_mousewheel_to_spinbox(eq_font_spin)

        tk.Label(eq_size_row, text="Fmt:", bg=self.colors["bg"], fg=self.colors["fg"],
                 font=("Helvetica", 9)).pack(side=tk.LEFT)
        self.eq_fmt_var = tk.StringVar(value="webp")
        self.eq_fmt_combo = tk.OptionMenu(eq_size_row, self.eq_fmt_var, *IMAGE_FORMATS)
        self._style_app_dropdown(self.eq_fmt_combo, self.eq_fmt_var, IMAGE_FORMATS)
        self.eq_fmt_combo.pack(side=tk.LEFT, padx=(2, 0))

        # Level Colors
        cf = tk.LabelFrame(right_content, text=" Levels Design Section ",
                           bg=self.colors["bg"], fg=self.colors["fg"],
                           font=("Helvetica", 9, "bold"), padx=8, pady=8)
        cf.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.randomize_all_var = tk.BooleanVar(value=False)
        self.randomize_pct_var = tk.BooleanVar(value=False)

        legend = tk.Frame(cf, bg=self.colors["bg"])
        legend.pack(fill=tk.X, pady=(0, 4))
        tk.Label(legend,
            text="☑ = Overwrite All  ·  ☐ = Apply If Blank",
            font=("Helvetica", 8), bg=self.colors["bg"], fg="#888888").pack(side=tk.LEFT)

        rand_frame = tk.Frame(legend, bg=self.colors["bg"])
        rand_frame.pack(side=tk.RIGHT, padx=2)
        tk.Checkbutton(rand_frame, text="All", variable=self.randomize_all_var,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(0, 2))
        tk.Checkbutton(rand_frame, text="%", variable=self.randomize_pct_var,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(0, 2))
        tk.Button(rand_frame, text="🎲 Randomize", command=self._randomize_colors,
                  bg="#6c5ce7", fg="#ffffff", activebackground="#a29bfe",
                  font=("Helvetica", 8, "bold"), relief=tk.FLAT, padx=8, pady=2,
                  cursor="hand2").pack(side=tk.LEFT)

        strip_btn = tk.Button(legend, text="🧹 Strip All", command=self._strip_all_styling,
                  bg="#e74c3c", fg="#ffffff", activebackground="#c0392b",
                  font=("Helvetica", 8, "bold"), relief=tk.FLAT, padx=8, pady=2,
                  cursor="hand2")
        strip_btn.pack(side=tk.RIGHT, padx=2)

        remove_row = tk.Frame(cf, bg=self.colors["bg"])
        remove_row.pack(fill=tk.X, pady=(2, 4))
        tk.Label(remove_row, text="Remove from all levels:",
                 font=("Helvetica", 8), bg=self.colors["bg"], fg="#888888").pack(side=tk.LEFT)

        self._make_remove_btn(remove_row, "Fill", self._remove_fill)
        self._make_remove_btn(remove_row, "Text", self._remove_text)
        self._make_remove_btn(remove_row, "Line", self._remove_line)
        self._make_remove_btn(remove_row, "Border", self._remove_border)
        self._make_remove_btn(remove_row, "Labels", self._remove_labels)
        self._make_remove_btn(remove_row, "Notes", self._remove_notes)

        scale_legend = tk.Frame(cf, bg=self.colors["bg"])
        scale_legend.pack(fill=tk.X, pady=(0, 2))
        tk.Label(scale_legend,
            text="W: 0=None  1=1pt  2=2pt  3=3pt  4=4pt  5=5pt",
            font=("Helvetica", 8), bg=self.colors["bg"], fg="#888888").pack(side=tk.LEFT)

        scroll_frame = tk.Frame(cf, bg=self.colors["bg"], height=320)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        scroll_frame.pack_propagate(False)

        self.colors_canvas = tk.Canvas(scroll_frame, highlightthickness=0, bg=self.colors["bg"])
        self.colors_sb = tk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=self.colors_canvas.yview,
                                       bg=self.colors["accent"], troughcolor=self.colors["bg"],
                                       activebackground=self.colors["select"])
        self.colors_canvas.configure(yscrollcommand=self.colors_sb.set)

        self.colors_host = tk.Frame(self.colors_canvas, bg=self.colors["bg"])
        self.colors_window = self.colors_canvas.create_window((0, 0), window=self.colors_host, anchor="nw")

        self.colors_host.bind("<Configure>", self._on_colors_host_configure)
        self.colors_canvas.bind("<Configure>", self._on_colors_canvas_configure)

        self.colors_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.colors_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._bind_colors_canvas_mousewheel()

        self.color_rows: List[ColorRow] = []
        self._init_color_rows(10)

        af = tk.Frame(right_content, bg=self.colors["bg"])
        af.pack(fill=tk.X, pady=(0, 8))
        tk.Button(af, text="↺ Reset", command=self._reset_colors,
                  bg=self.colors["btn_bg"], fg="#000000", activebackground=self.colors["accent"],
                  relief=tk.FLAT, cursor="hand2", font=("Helvetica", 9)).pack(side=tk.LEFT, padx=2)
        tk.Button(af, text="+ Level", command=self._add_level,
                  bg=self.colors["btn_bg"], fg="#000000", activebackground=self.colors["accent"],
                  relief=tk.FLAT, cursor="hand2", font=("Helvetica", 9)).pack(side=tk.LEFT, padx=2)

        # Strip Properties
        spf = tk.LabelFrame(right_content, text=" Strip Properties ",
                            bg=self.colors["bg"], fg=self.colors["fg"],
                            font=("Helvetica", 9, "bold"), padx=8, pady=8)
        spf.pack(fill=tk.X, pady=(0, 8))

        strip_row1 = tk.Frame(spf, bg=self.colors["bg"])
        strip_row1.pack(fill=tk.X)
        strip_row2 = tk.Frame(spf, bg=self.colors["bg"])
        strip_row2.pack(fill=tk.X, pady=(2, 0))

        self.strip_border_var = tk.BooleanVar(value=False)
        self.strip_fill_var = tk.BooleanVar(value=False)
        self.strip_text_var = tk.BooleanVar(value=False)
        self.strip_labels_var = tk.BooleanVar(value=False)
        self.strip_notes_var = tk.BooleanVar(value=False)
        self.strip_equation_var = tk.BooleanVar(value=False)

        tk.Checkbutton(strip_row1, text="Border", variable=self.strip_border_var,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(0, 8))
        tk.Checkbutton(strip_row1, text="Fill", variable=self.strip_fill_var,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(0, 8))
        tk.Checkbutton(strip_row1, text="Text", variable=self.strip_text_var,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(0, 8))
        tk.Checkbutton(strip_row1, text="Labels", variable=self.strip_labels_var,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(0, 8))

        tk.Checkbutton(strip_row2, text="Notes", variable=self.strip_notes_var,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(0, 8))
        tk.Checkbutton(strip_row2, text="Equations", variable=self.strip_equation_var,
                       bg=self.colors["bg"], fg=self.colors["fg"],
                       activebackground=self.colors["bg"], selectcolor=self.colors["select"],
                       font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(spf, text="✕  Strip All Checked", command=self._strip_properties,
                  bg="#ff3b30", fg="#ffffff", activebackground="#ff6b6b",
                  font=("Helvetica", 9, "bold"), relief=tk.FLAT, padx=10, pady=4,
                  cursor="hand2").pack(fill=tk.X, pady=(6, 0))

        # Update eq adjust button state initially and on changes
        self._update_eq_adjust_button()
        self.input_text.text.bind("<KeyRelease>", lambda e: self._update_eq_adjust_button())

    # ── Eq Adjuster toggle (fixed) ──
    def _toggle_eq_adjuster(self):
        # This button is disabled (unclickable) while the panel is open --
        # see the state=tk.DISABLED set right after EqAdjusterPanel is
        # created below. Closing only happens via the Normal/Manual toggle
        # button or the panel's own Close button, both of which re-enable
        # this button through close_callback -> _update_eq_adjust_button().
        if self.eq_adjust_frame is not None:
            return
        if not self._has_equations():
            return
        raw = self.input_text.get("1.0", tk.END)
        try:
            parser = HierarchyParser(raw)
            entries = parser.parse()

            # Build cumulative paths for each entry (same logic as build_tree)
            last_at_level = {}
            for entry in entries:
                level = entry["level"]
                index = entry["index"]
                if level == 1:
                    entry["path"] = [(1, index)]
                    last_at_level[1] = entry
                else:
                    parent_level = level - 1
                    if parent_level in last_at_level:
                        parent_path = list(last_at_level[parent_level]["path"])
                        entry["path"] = parent_path + [(level, index)]
                    else:
                        entry["path"] = [(level, index)]
                    last_at_level[level] = entry

            nodes_with_eq = []
            for entry in entries:
                img_data = entry.get("image_data")
                if img_data and img_data.get("equation"):
                    node = {
                        "path": list(entry["path"]),
                        "heading": entry["title"],
                        "equation": img_data["equation"],
                        "eq_w": int(img_data.get("eq_w", DEFAULT_EQ_W)),
                        "eq_h": int(img_data.get("eq_h", DEFAULT_EQ_H)),
                        "eq_font": int(img_data.get("eq_font", DEFAULT_EQ_FONT)),
                        "_entry_key": tuple(tuple(p) for p in entry["path"]),
                    }
                    nodes_with_eq.append(node)
            if not nodes_with_eq:
                return

            self._hide_editor_content()

            def close_callback(updated_nodes):
                # Build lookup: full path tuple → updated node
                up_map = {}
                for up in updated_nodes:
                    up_map[up["_entry_key"]] = up

                # Rebuild the WHOLE hierarchy from the already-parsed `entries`
                # (each of which carries its own cumulative lvlN[I] "path"),
                # instead of naively re-splitting the raw text on "\n".
                #
                # IMPORTANT: any entry whose note/label field contains an
                # embedded newline (perfectly legal -- e.g. a multi-paragraph
                # note) spans several physical lines of raw text. The old
                # line-by-line rebuild processed one physical line at a time,
                # so it could never find that entry's closing "}" (which sat
                # several lines below), mis-detected the title, and dropped
                # the note. Worse, the mangled output line ended up with
                # unbalanced braces, so the NEXT time this text was parsed by
                # HierarchyParser._split_entries() (which tracks brace depth
                # to know where one entry ends and the next begins), brace
                # depth never returned to 0 and every remaining entry in the
                # file got fused into one giant blob -- i.e. the whole map
                # collapsing into a single node after an Eq Adjuster save.
                # Rebuilding straight from the structured `entries` list
                # sidesteps all of that: braces are always emitted balanced.
                new_blocks = []
                for entry in entries:
                    prefix = "".join(f"lvl{lvl}[{idx}]" for lvl, idx in entry["path"])
                    title = entry["title"]
                    entry_key = tuple(tuple(p) for p in entry["path"])
                    img_data = entry.get("image_data") or {}

                    parts = []
                    note = entry.get("note")
                    if note:
                        escaped_note = note.replace('\\', '\\\\').replace('"', '\\"')
                        parts.append(f'note:"{escaped_note}"')
                    labels = entry.get("labels")
                    if labels:
                        parts.append('label:"' + ",".join(labels) + '"')
                    colors = entry.get("colors") or {}
                    for key in ("fill", "text", "line", "border"):
                        if colors.get(key):
                            parts.append(f'{key}:"{colors[key]}"')

                    if entry_key in up_map:
                        updated = up_map[entry_key]
                        equation = updated["equation"]
                        eq_w = updated["eq_w"]
                        eq_h = updated["eq_h"]
                        eq_font = updated["eq_font"]
                    else:
                        equation = img_data.get("equation")
                        eq_w = img_data.get("eq_w")
                        eq_h = img_data.get("eq_h")
                        eq_font = img_data.get("eq_font")

                    if equation:
                        parts.append(f'equation:"{equation}"')
                        if eq_w is not None:
                            parts.append(f'eq_w:{eq_w}')
                        if eq_h is not None:
                            parts.append(f'eq_h:{eq_h}')
                        if eq_font is not None:
                            parts.append(f'eq_font:{eq_font}')
                        if img_data.get("eq_color"):
                            parts.append(f'eq_color:"{img_data["eq_color"]}"')
                        if img_data.get("eq_bg"):
                            parts.append(f'eq_bg:"{img_data["eq_bg"]}"')
                        if img_data.get("img_fmt"):
                            parts.append(f'img_fmt:"{img_data["img_fmt"]}"')

                    block = prefix + title
                    if parts:
                        block += "{" + ",".join(parts) + "}"
                    new_blocks.append(block)

                new_text = "\n\n".join(new_blocks)
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", new_text)
                self.status_var.set("Eq adjustments applied")
                self._update_eq_adjust_button()
                self.eq_adjust_frame = None
                self._show_normal_editor()
                if self.manual_mode_var.get() and self.manual_editor:
                    self.manual_editor.reload_from_text()

            self.eq_adjust_frame = EqAdjusterPanel(self.editor_container, self, nodes_with_eq, close_callback)
            self.eq_adjust_frame.pack(fill=tk.BOTH, expand=True)
            # Disabled while open: the panel is closed via the Normal/Manual
            # toggle button or the panel's own Close button, not by
            # re-clicking this one. close_callback (above) calls
            # _update_eq_adjust_button() to re-enable it once closed.
            self.eq_adjust_btn.config(state=tk.DISABLED, bg="#555555", fg="#888888")
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Eq Adjuster Error", str(e))
            self.status_var.set(f"Error: {e}")
    def _hide_editor_content(self):
        # Main search bar only belongs to Normal mode -- hide it whenever the
        # Eq Adjuster panel takes over (it has its own list/search UI).
        self.search_frame.pack_forget()
        if self.manual_mode_var.get() and self.manual_editor:
            self.manual_editor.frame.pack_forget()
        else:
            self.input_text.pack_forget()

    def _show_normal_editor(self):
        # Ensure eq adjuster is hidden before showing normal editor
        if self.eq_adjust_frame is not None:
            self.eq_adjust_frame.pack_forget()
        if self.manual_mode_var.get() and self.manual_editor:
            self.manual_editor.frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.search_frame.pack(fill=tk.X, pady=(0, 2), before=self.manual_btn.master)
            self.input_text.pack(fill=tk.BOTH, expand=True)

    # ── Search methods ──
    def _search_find_all(self):
        # BUGFIX (M3-82): this used to call self._search_clear() FIRST, which
        # deletes the text typed into search_entry -- so search_text was read
        # AFTER the box was already wiped, and the search always ran on "".
        # Now we read the text first, and only clear old highlights/matches
        # (not the entry box itself).
        search_text = self.search_entry.get()
        self._clear_search_highlights()
        if not search_text:
            self.search_status.config(text="Enter search text")
            return
        text_widget = self.input_text.text
        start = "1.0"
        count = 0
        while True:
            pos = text_widget.search(search_text, start, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(search_text)}c"
            text_widget.tag_add("search_highlight", pos, end)
            self._search_matches.append((pos, end))
            count += 1
            start = end
        self._search_current = -1
        if count > 0:
            self.search_status.config(text=f"Found {count} match(es)")
            self._search_next()
        else:
            self.search_status.config(text="No matches found")

    def _search_next(self):
        if not self._search_matches:
            return
        self._search_current = (self._search_current + 1) % len(self._search_matches)
        self._goto_match(self._search_current)

    def _search_prev(self):
        if not self._search_matches:
            return
        self._search_current = (self._search_current - 1) % len(self._search_matches)
        self._goto_match(self._search_current)

    def _goto_match(self, idx):
        start, end = self._search_matches[idx]
        text_widget = self.input_text.text
        text_widget.see(start)
        text_widget.tag_remove("sel", "1.0", tk.END)
        text_widget.tag_add("sel", start, end)
        self.search_status.config(text=f"Match {idx+1}/{len(self._search_matches)}")

    def _clear_search_highlights(self):
        self.input_text.text.tag_remove("search_highlight", "1.0", tk.END)
        self._search_matches = []
        self._search_current = -1
        self.search_status.config(text="")

    def _search_clear(self):
        # Used by the "Clear" button: clears highlights AND empties the box.
        self._clear_search_highlights()
        self.search_entry.delete(0, tk.END)

    def _style_app_dropdown(self, optionmenu, var, options):
        menu = optionmenu["menu"]
        btn_bg = "#00b4d8"
        active_bg = "#00d2ff"
        optionmenu.config(bg=btn_bg, fg="#000000", activebackground=active_bg,
                          relief=tk.FLAT, font=("Helvetica", 9))
        menu.config(bg=self.colors["entry_bg"], fg="#000000",
                    activebackground=active_bg, activeforeground="#000000")
        def _update_highlight(*args):
            current = var.get()
            for i, opt in enumerate(options):
                if opt == current:
                    menu.entryconfig(i, background=btn_bg, foreground="#ffffff")
                else:
                    menu.entryconfig(i, background=self.colors["entry_bg"], foreground="#000000")
        var.trace_add("write", _update_highlight)
        menu.configure(postcommand=lambda: _update_highlight())
        _update_highlight()

    def _on_cat_change(self, *args):
        cat = self.cat_var.get()
        cat_info = STRUCTURE_DEFS.get(cat, {})
        subs = list(cat_info.get("subs", {}).keys())
        if subs:
            self.sub_var.set(subs[0])
        self._update_sub_combo()
        self._on_sub_change()

    def _on_sub_change(self, *args):
        self._update_status()

    def _update_sub_combo(self):
        cat = self.cat_var.get()
        cat_info = STRUCTURE_DEFS.get(cat, {})
        subs = list(cat_info.get("subs", {}).keys())
        menu = self.sub_combo["menu"]
        menu.delete(0, tk.END)
        for s in subs:
            menu.add_command(label=s, command=lambda v=s: self.sub_var.set(v) or self._on_sub_change())
        if self.sub_var.get() not in subs and subs:
            self.sub_var.set(subs[0])
        self._style_app_dropdown(self.sub_combo, self.sub_var, subs)

    def _update_status(self):
        cat = self.cat_var.get()
        sub = self.sub_var.get()
        self.status_var.set(f"Layout: {cat} — {sub}")

    def _toggle_manual_mode(self):
        # Close eq adjuster if open
        if self.eq_adjust_frame is not None:
            self.eq_adjust_frame._close()
            self.eq_adjust_frame = None
        if not self.manual_mode_var.get():
            self.manual_mode_var.set(True)
            self.manual_btn.config(text="✎ Normal", bg="#e74c3c", font=("Helvetica", 13, "bold"), relief=tk.RAISED, bd=3)
            self.manual_status.config(
                text="Manual Mode — Enter/Tab=deeper (at root) | Enter=sibling | Tab=child (at lvl2+) | Shift=field | Backspace=delete",
                fg="#00b894"
            )
            self.search_frame.pack_forget()
            self.input_text.pack_forget()
            if self.manual_editor is None:
                self.manual_editor = ManualModeEditor(self.editor_container, self, self.colors)
            self.manual_editor.show()
            self.status_var.set("Manual Mode ON — Start typing heading for lvl1[1]")
        else:
            self.manual_mode_var.set(False)
            self.manual_btn.config(text="📝 Manual", bg="#6c5ce7", font=("Helvetica", 13, "bold"), relief=tk.RAISED, bd=3)
            self.manual_status.config(
                text="Normal Mode — type or paste hierarchy text freely",
                fg="#888888"
            )
            if self.manual_editor:
                self.manual_editor.hide()
            self.search_frame.pack(fill=tk.X, pady=(0, 2), before=self.manual_btn.master)
            self.input_text.pack(fill=tk.BOTH, expand=True)
            self.status_var.set("Normal Mode — paste or type hierarchy text")

    def _get_layout(self) -> str:
        cat = self.cat_var.get()
        sub = self.sub_var.get()
        cat_info = STRUCTURE_DEFS.get(cat, {})
        sub_info = cat_info.get("subs", {}).get(sub, {})
        return sub_info.get("struct", "org.xmind.ui.map.unbalanced")

    def _pick_eq_color(self):
        c = colorchooser.askcolor(color=self.eq_color_var.get(), title="Equation Text Color")[1]
        if c:
            self.eq_color_var.set(c)
            self.eq_color_prev.config(bg=c)

    def _update_eq_color_swatch(self):
        v = self.eq_color_var.get()
        if v.lower() == "none":
            self.eq_color_prev.config(bg="#888888")
        else:
            self.eq_color_prev.config(bg=v)

    def _pick_eq_bg(self):
        c = colorchooser.askcolor(color=self.eq_bg_var.get(), title="Equation Background")[1]
        if c:
            self.eq_bg_var.set(c)
            self.eq_bg_prev.config(bg=c)

    def _update_eq_bg_swatch(self):
        v = self.eq_bg_var.get()
        if v.lower() == "none":
            self.eq_bg_prev.config(bg=self.colors["bg"])
        else:
            self.eq_bg_prev.config(bg=v)

    def _pick_map_bg(self):
        c = colorchooser.askcolor(color=self.map_bg_var.get(), title="Canvas Background")[1]
        if c:
            self.map_bg_var.set(c.upper())
            self.map_bg_prev.config(bg=c)

    def _update_map_bg(self):
        v = self.map_bg_var.get()
        if re.match(r'^#[0-9a-fA-F]{6}$', v):
            self.map_bg_prev.config(bg=v)

    def _init_color_rows(self, count: int):
        for row in self.color_rows:
            row.card.destroy()
        self.color_rows.clear()
        for i in range(1, count + 1):
            d = DEFAULT_LEVEL_PALETTE[(i - 1) % len(DEFAULT_LEVEL_PALETTE)]
            check_var = tk.BooleanVar(value=False)
            row = ColorRow(self.colors_host, i, d, check_var, self.colors)
            self.color_rows.append(row)
        self.colors_host.update_idletasks()
        self.colors_canvas.update_idletasks()
        self._on_colors_host_configure()
        self._on_colors_canvas_configure()

    def _detect_levels(self):
        raw = self.input_text.get("1.0", tk.END)
        if not raw.strip():
            messagebox.showwarning("Empty", "Paste some data first.")
            return
        try:
            parser = HierarchyParser(raw)
            max_level = parser.get_max_level()
            target = max(3, max_level)
            self._init_color_rows(target)
            self.status_var.set(f"Detected {max_level} levels. Showing {target} color rows.")
            self._update_level_counts()
        except Exception as e:
            messagebox.showerror("Detection Failed", str(e))
            self.status_var.set(f"Error: {e}")

    def _paste(self):
        try:
            t = self.root.clipboard_get()
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", t)
            self.status_var.set("Pasted")
            self._update_level_counts()
            self._update_eq_adjust_button()
        except tk.TclError:
            messagebox.showwarning("Clipboard", "Clipboard is empty.")

    def _clear(self):
        self.input_text.delete("1.0", tk.END)
        self.status_var.set("Cleared")
        self._update_level_counts()
        self._update_eq_adjust_button()

    def _load(self):
        p = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if p:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    self.input_text.delete("1.0", tk.END)
                    self.input_text.insert("1.0", f.read())
                self.status_var.set(f"Loaded: {os.path.basename(p)}")
                self._update_level_counts()
                self._update_eq_adjust_button()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _copy_raw(self):
        t = self.input_text.get("1.0", tk.END).strip()
        if not t:
            self.status_var.set("Nothing to copy — editor is empty")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(t)
        lines = len(t.splitlines())
        self.status_var.set(f"Copied {lines} lines to clipboard")

    def _make_remove_btn(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd,
                         bg="#e74c3c", fg="#ffffff", activebackground="#c0392b",
                         font=("Helvetica", 8, "bold"), relief=tk.FLAT, padx=6, pady=1,
                         cursor="hand2")

    def _remove_fill(self):
        for row in self.color_rows:
            row.fill_var.set("")
            row.fill_opacity_var.set(100)
        self.status_var.set("Fill color removed from all levels")

    def _remove_text(self):
        for row in self.color_rows:
            row.font_var.set("")
        self.status_var.set("Text color removed from all levels")

    def _remove_line(self):
        for row in self.color_rows:
            row.line_var.set("")
            row.line_opacity_var.set(100)
        self.status_var.set("Line color removed from all levels")

    def _remove_border(self):
        for row in self.color_rows:
            row.border_var.set("")
            row.border_width_var.set(0)
            row.border_opacity_var.set(100)
        self.status_var.set("Border removed from all levels")

    def _remove_labels(self):
        raw = self.input_text.get("1.0", tk.END)
        cleaned = re.sub(r'label:\s*"[^"]*"', '', raw)
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", cleaned)
        self.status_var.set("Labels removed from all entries")

    def _remove_notes(self):
        raw = self.input_text.get("1.0", tk.END)
        cleaned = re.sub(r'note:\s*"[^"]*"', '', raw)
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", cleaned)
        self.status_var.set("Notes removed from all entries")

    def _randomize_colors(self):
        randomize_all = self.randomize_all_var.get()
        randomize_pct = self.randomize_pct_var.get()
        for row in self.color_rows:
            fill = f"#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}"
            border = f"#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}"
            line = f"#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}"
            brightness = (int(fill[1:3], 16) * 299 + int(fill[3:5], 16) * 587 + int(fill[5:7], 16) * 114) / 1000
            text = "#ffffff" if brightness < 128 else "#000000"
            if random.random() < 0.1:
                text = "#000000" if text == "#ffffff" else "#ffffff"
            row.fill_var.set(fill)
            row.border_var.set(border)
            row.font_var.set(text)
            row.line_var.set(line)
            if randomize_pct:
                if self.cap_fill_chk.get():
                    fmin = self.cap_fill_min.get()
                    fmax = self.cap_fill_max.get()
                    row.fill_opacity_var.set(random.randint(fmin, fmax))
                else:
                    row.fill_opacity_var.set(random.randint(20, 100))
                if self.cap_line_chk.get():
                    lmin = self.cap_line_min.get()
                    lmax = self.cap_line_max.get()
                    row.line_opacity_var.set(random.randint(lmin, lmax))
                else:
                    row.line_opacity_var.set(random.randint(20, 100))
                if self.cap_border_chk.get():
                    bmin = self.cap_border_min.get()
                    bmax = self.cap_border_max.get()
                    row.border_opacity_var.set(random.randint(bmin, bmax))
                else:
                    row.border_opacity_var.set(random.randint(20, 100))
            if randomize_all:
                row.font_size_var.set(random.randint(10, 24))
                row.line_width_var.set(random.randint(1, 5))
                row.border_width_var.set(random.randint(0, 5))
                row.branch_shape_var.set(random.choice(BRANCH_SHAPE_LABELS))
                row.node_shape_var.set(random.choice(NODE_SHAPE_LABELS))
        parts = []
        if randomize_all: parts.append("all styles")
        if randomize_pct: parts.append("opacity")
        suffix = f" + {', '.join(parts)}" if parts else ""
        self.status_var.set("Colors randomized" + suffix)

    def _reset_colors(self):
        for i, row in enumerate(self.color_rows):
            d = DEFAULT_LEVEL_PALETTE[i % len(DEFAULT_LEVEL_PALETTE)]
            row.fill_var.set(d["fill"])
            row.fill_opacity_var.set(d.get("fill_opacity", 100))
            row.font_var.set(d["text"])
            row.line_var.set(d["line"])
            row.line_opacity_var.set(d.get("line_opacity", 100))
            row.border_var.set(d.get("border", d["fill"]))
            row.border_opacity_var.set(d.get("border_opacity", 100))
            fs = d.get("font_size", 14)
            if isinstance(fs, str): fs = int(fs) if fs.isdigit() else 14
            row.font_size_var.set(fs)
            lw = d.get("line_width", 1)
            if isinstance(lw, str): lw = int(lw) if lw.isdigit() else 1
            row.line_width_var.set(lw)
            bw = d.get("border_width", 2)
            if isinstance(bw, str): bw = int(bw) if bw.isdigit() else 2
            row.border_width_var.set(bw)
            row.branch_shape_var.set(d.get("branch_shape", "Rounded"))
            row.node_shape_var.set(d.get("node_shape", "Rounded Rect"))
            row.check_var.set(False)
        self.map_bg_var.set(DEFAULT_MAP_BG)
        self.map_bg_prev.config(bg=DEFAULT_MAP_BG)
        self.cat_var.set("Logic Chart")
        self._on_cat_change()
        self.randomize_all_var.set(False)
        self.randomize_pct_var.set(False)
        self.note_heading_var.set(False)
        self.note_bold_var.set(False)
        self.eq_override_var.set(False)
        self.eq_color_override.set(False)
        self.eq_bg_override.set(False)
        self.eq_w_override.set(False)
        self.eq_h_override.set(False)
        self.eq_font_override.set(False)
        self.eq_fmt_override.set(False)
        self.eq_color_var.set("white")
        self.eq_bg_var.set("black")
        self.eq_w_var.set(DEFAULT_EQ_W)
        self.eq_h_var.set(DEFAULT_EQ_H)
        self.eq_font_var.set(DEFAULT_EQ_FONT)
        self.eq_fmt_var.set(DEFAULT_IMAGE_FMT)
        self._update_eq_color_swatch()
        self._update_eq_bg_swatch()
        self.status_var.set("Colors reset")
        self._update_eq_adjust_button()

    def _on_colors_host_configure(self, event=None):
        self.colors_canvas.configure(scrollregion=self.colors_canvas.bbox("all"))
        self.colors_canvas.update_idletasks()

    def _on_colors_canvas_configure(self, event=None):
        canvas_width = event.width if event else self.colors_canvas.winfo_width()
        if canvas_width > 1:
            self.colors_canvas.itemconfig(self.colors_window, width=canvas_width - 4)

    def _bind_colors_canvas_mousewheel(self):
        def _on_mousewheel(event):
            if isinstance(event.widget, tk.Spinbox):
                return
            if event.delta > 0:
                self.colors_canvas.yview_scroll(-3, "units")
            elif event.delta < 0:
                self.colors_canvas.yview_scroll(3, "units")
            return "break"

        def _on_linux_scroll_up(event):
            if isinstance(event.widget, tk.Spinbox):
                return
            self.colors_canvas.yview_scroll(-3, "units")
            return "break"

        def _on_linux_scroll_down(event):
            if isinstance(event.widget, tk.Spinbox):
                return
            self.colors_canvas.yview_scroll(3, "units")
            return "break"

        self.colors_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.colors_canvas.bind("<Button-4>", _on_linux_scroll_up)
        self.colors_canvas.bind("<Button-5>", _on_linux_scroll_down)
        self.colors_host.bind("<MouseWheel>", _on_mousewheel)
        self.colors_host.bind("<Button-4>", _on_linux_scroll_up)
        self.colors_host.bind("<Button-5>", _on_linux_scroll_down)

    def _strip_all_styling(self):
        for row in self.color_rows:
            row.border_var.set("")
            row.border_prev.config(bg=self.colors["bg"])
            row.border_width_var.set(0)
            row.border_opacity_var.set(100)
            row.fill_var.set("")
            row.fill_prev.config(bg=self.colors["bg"])
            row.fill_opacity_var.set(100)
            row.font_var.set("")
            row.font_prev.config(bg=self.colors["bg"])
            row.line_var.set("")
            row.line_prev.config(bg=self.colors["bg"])
            row.line_opacity_var.set(100)
        self.status_var.set("Stripped: border, fill, text, line color from all levels")

    def _add_level(self):
        n = len(self.color_rows) + 1
        d = DEFAULT_LEVEL_PALETTE[(n - 1) % len(DEFAULT_LEVEL_PALETTE)]
        check_var = tk.BooleanVar(value=False)
        row = ColorRow(self.colors_host, n, d, check_var, self.colors)
        self.color_rows.append(row)
        self.colors_host.update_idletasks()
        self.colors_canvas.update_idletasks()
        self._on_colors_host_configure()
        self._on_colors_canvas_configure()
        self.colors_canvas.yview_moveto(1.0)
        self.status_var.set(f"Added Level {n}")

    def _get_config(self):
        level_colors = [row.get() for row in self.color_rows]
        color_mode = [row.get_mode() for row in self.color_rows]
        layout = self._get_layout()
        map_bg = self.map_bg_var.get()
        note_heading = self.note_heading_var.get()
        note_bold = self.note_bold_var.get()
        eq_fmt = self.eq_fmt_var.get()
        eq_override_flags = {
            'color': self.eq_color_override.get(),
            'bg': self.eq_bg_override.get(),
            'w': self.eq_w_override.get(),
            'h': self.eq_h_override.get(),
            'font': self.eq_font_override.get(),
            'fmt': self.eq_fmt_override.get(),
        }
        eq_design = {
            "eq_color": self.eq_color_var.get(),
            "eq_bg": self.eq_bg_var.get(),
            "eq_w": self.eq_w_var.get(),
            "eq_h": self.eq_h_var.get(),
            "eq_font": self.eq_font_var.get(),
            "eq_fmt": self.eq_fmt_var.get(),
        }
        return level_colors, color_mode, layout, map_bg, note_heading, note_bold, eq_fmt, eq_override_flags, eq_design

    def _strip_properties(self):
        strip_border = self.strip_border_var.get()
        strip_fill = self.strip_fill_var.get()
        strip_text = self.strip_text_var.get()
        strip_labels = self.strip_labels_var.get()
        strip_notes = self.strip_notes_var.get()
        strip_equation = self.strip_equation_var.get()

        if not any([strip_border, strip_fill, strip_text, strip_labels, strip_notes, strip_equation]):
            self.status_var.set("Nothing checked to strip")
            return

        for row in self.color_rows:
            if strip_border:
                row.border_var.set("")
                row.border_prev.config(bg=self.colors["bg"])
                row.border_opacity_var.set(100)
            if strip_fill:
                row.fill_var.set("")
                row.fill_prev.config(bg=self.colors["bg"])
                row.fill_opacity_var.set(100)
            if strip_text:
                row.font_var.set("")
                row.font_prev.config(bg=self.colors["bg"])

        if strip_labels or strip_notes or strip_equation:
            raw = self.input_text.get("1.0", tk.END)
            if strip_labels:
                raw = re.sub(r'label:\s*"[^"]*"', '', raw)
            if strip_notes:
                raw = re.sub(r'note:\s*"[^"]*"', '', raw)
            if strip_equation:
                raw = re.sub(r'equation:\s*"[^"]*"', '', raw)
                raw = re.sub(r'eq_w:\s*\d+', '', raw)
                raw = re.sub(r'eq_h:\s*\d+', '', raw)
                raw = re.sub(r'eq_font:\s*\d+', '', raw)
                raw = re.sub(r'eq_color:\s*"[^"]*"', '', raw)
                raw = re.sub(r'eq_bg:\s*"[^"]*"', '', raw)
                raw = re.sub(r'img_fmt:\s*"?[^",}]*"?', '', raw)
            for _ in range(3):
                raw = re.sub(r'\{\s*,+\s*\}', '', raw)
                raw = re.sub(r',\s*\}', '}', raw)
                raw = re.sub(r'\{\s*,', '{', raw)
                raw = re.sub(r',\s*,', ',', raw)
                raw = re.sub(r'\{\s+', '{', raw)
                raw = re.sub(r'\s+\}', '}', raw)
            raw = re.sub(r'\{\s*\}', '', raw)
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", raw)

        parts = []
        if strip_border: parts.append("border")
        if strip_fill: parts.append("fill")
        if strip_text: parts.append("text")
        if strip_labels: parts.append("labels")
        if strip_notes: parts.append("notes")
        if strip_equation: parts.append("equations")
        self.status_var.set(f"Stripped: {', '.join(parts)}")
        self._update_eq_adjust_button()

    def _apply_heading_tags(self, raw_text):
        use_h1 = self.note_heading_var.get()
        use_bold = self.note_bold_var.get()
        if not use_h1 and not use_bold:
            return raw_text
        try:
            parser = HierarchyParser(raw_text)
            entries = parser.parse()
        except Exception:
            return raw_text
        if not entries:
            return raw_text
        lines = []
        for entry in entries:
            level = entry["level"]
            idx = entry["index"]
            title = entry["title"]
            note = entry.get("note")
            labels = entry.get("labels")
            colors = entry.get("colors")
            line = f"lvl{level}[{idx}]{title}"
            brace_parts = []
            if note is not None:
                wrapped_note = note
                if use_bold:
                    wrapped_note = f"<strong>{wrapped_note}</strong>"
                if use_h1:
                    wrapped_note = f"<h1>{wrapped_note}</h1>"
                brace_parts.append(f'note:"{wrapped_note}"')
            if labels:
                brace_parts.append(f'label:"{",".join(labels)}"')
            if colors:
                for key, val in colors.items():
                    brace_parts.append(f'{key}:"{val}"')
            img_data = entry.get("image_data")
            if img_data:
                if img_data.get("equation"):
                    brace_parts.append(f'equation:"{img_data["equation"]}"')
                    if img_data.get("eq_w") and img_data["eq_w"] != 260:
                        brace_parts.append(f'eq_w:{img_data["eq_w"]}')
                    if img_data.get("eq_h") and img_data["eq_h"] != 70:
                        brace_parts.append(f'eq_h:{img_data["eq_h"]}')
                    if img_data.get("eq_font") and img_data["eq_font"] != 18:
                        brace_parts.append(f'eq_font:{img_data["eq_font"]}')
                if img_data.get("img_fmt") and img_data["img_fmt"] != DEFAULT_IMAGE_FMT:
                    brace_parts.append(f'img_fmt:"{img_data["img_fmt"]}"')
            if brace_parts:
                line += "{" + ",".join(brace_parts) + "}"
            lines.append(line)
        return chr(10).join(lines)

    def _export(self):
        # Close eq adjuster if open
        if self.eq_adjust_frame is not None:
            self.eq_adjust_frame._close()
            self.eq_adjust_frame = None
        if self.manual_mode_var.get() and self.manual_editor and self.manual_editor.active:
            self.manual_editor._save_current_field()
            self.manual_editor.hide()
            self.manual_mode_var.set(False)
            self.manual_btn.config(text="📝 Manual", bg="#6c5ce7", font=("Helvetica", 13, "bold"), relief=tk.RAISED, bd=3)
            self.manual_status.config(
                text="Normal Mode — type or paste hierarchy text freely",
                fg="#888888"
            )
            self.search_frame.pack(fill=tk.X, pady=(0, 2), before=self.manual_btn.master)
            self.input_text.pack(fill=tk.BOTH, expand=True)
            self.status_var.set("Synced Manual Mode data and switched to Normal Mode for export")

        raw = self.input_text.get("1.0", tk.END)
        if not raw.strip():
            messagebox.showwarning("Empty", "Paste some data first.")
            return
        raw = self._apply_heading_tags(raw)
        initial_name = None
        try:
            parser = HierarchyParser(raw)
            root_node = parser.build_tree()
            if root_node and root_node.get("title"):
                initial_name = root_node["title"] + ".xmind"
        except Exception:
            pass
        kwargs = {"defaultextension": ".xmind",
                    "filetypes": [("XMind", "*.xmind"), ("All", "*.*")]}
        if initial_name:
            kwargs["initialfile"] = initial_name
        sp = filedialog.asksaveasfilename(**kwargs)
        if not sp:
            return
        level_colors, color_mode, layout, map_bg, note_heading, note_bold, eq_fmt, eq_override_flags, eq_design = self._get_config()
        try:
            result = convert_to_xmind(raw, sp, layout=layout, level_colors=level_colors,
                                     color_mode=color_mode, map_bg=map_bg, note_heading=note_heading,
                                     default_img_fmt=eq_fmt, eq_override_flags=eq_override_flags, eq_design=eq_design)
            self.status_var.set(f"Exported: {os.path.basename(result)}")
            if self.open_after_export_var.get():
                try:
                    if os.name == "nt":
                        os.startfile(result)
                    elif os.name == "posix":
                        subprocess.Popen(["xdg-open", result], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.Popen(["open", result], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception as e:
                    messagebox.showerror("Open Failed", f"Could not open exported file: {e}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
            self.status_var.set(f"Error: {e}")

    def _copy_to_clipboard(self):
        raw = self.input_text.get("1.0", tk.END)
        if not raw.strip():
            messagebox.showwarning("Empty", "Paste some data first.")
            return
        try:
            parser = HierarchyParser(raw)
            root_node = parser.build_tree()
            if root_node is None:
                raise ValueError("No valid entries found.")
            outline_text = build_tab_outline(root_node)
            self.root.clipboard_clear()
            self.root.clipboard_append(outline_text)
            line_count = len(outline_text.splitlines())
            self.status_var.set(f"Copied {line_count} topics to clipboard")
        except Exception as e:
            messagebox.showerror("Copy Failed", str(e))
            self.status_var.set(f"Error: {e}")

    def _preview(self):
        # Close eq adjuster if open
        if self.eq_adjust_frame is not None:
            self.eq_adjust_frame._close()
            self.eq_adjust_frame = None
        if self.manual_mode_var.get() and self.manual_editor and self.manual_editor.active:
            self.manual_editor._save_current_field()
            self.manual_editor.hide()
            self.manual_mode_var.set(False)
            self.manual_btn.config(text="📝 Manual", bg="#6c5ce7", font=("Helvetica", 13, "bold"), relief=tk.RAISED, bd=3)
            self.manual_status.config(
                text="Normal Mode — type or paste hierarchy text freely",
                fg="#888888"
            )
            self.search_frame.pack(fill=tk.X, pady=(0, 2), before=self.manual_btn.master)
            self.input_text.pack(fill=tk.BOTH, expand=True)
            self.status_var.set("Synced Manual Mode data and switched to Normal Mode for preview")

        raw = self.input_text.get("1.0", tk.END)
        if not raw.strip():
            messagebox.showwarning("Empty", "Paste some data first.")
            return
        raw = self._apply_heading_tags(raw)
        level_colors, color_mode, layout, map_bg, note_heading, note_bold, eq_fmt, eq_override_flags, eq_design = self._get_config()
        try:
            xmind_bytes = build_xmind_bytes(raw, layout=layout, level_colors=level_colors,
                                           color_mode=color_mode, map_bg=map_bg, note_heading=note_heading,
                                           default_img_fmt=eq_fmt, eq_override_flags=eq_override_flags, eq_design=eq_design)
        except Exception as e:
            messagebox.showerror("Preview Failed", str(e))
            self.status_var.set(f"Error: {e}")
            return
        path = os.path.join(tempfile.gettempdir(), f"mindmap_preview_{uuid.uuid4().hex}.xmind")
        with open(path, "wb") as f:
            f.write(xmind_bytes)
        # Register with the atexit-driven cleanup safety net (see
        # _cleanup_all_temps) so this file still gets removed on exit
        # even if the delayed-delete thread below never gets to run --
        # e.g. the app is closed before its `delay` elapses.
        _register_temp(path)
        try:
            if os.name == "nt":
                os.startfile(path)
            elif os.name == "posix":
                subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            messagebox.showerror("Open Failed", f"Could not open preview: {e}")
            try:
                os.remove(path)
            except OSError:
                pass
            return
        self.status_var.set(f"Preview opened: {os.path.basename(path)}")

        delay = getattr(self, '_delay_seconds', 30)

        def _cleanup():
            time.sleep(delay)
            # Retry a few times with backoff -- if the external viewer
            # this preview was opened in still has the file open/locked
            # right when the timer first fires, a single attempt used to
            # silently give up (log to stderr, which nobody sees in a
            # GUI app) and leave the file behind for good.
            for attempt, wait in enumerate((0, 2, 5, 10)):
                if wait:
                    time.sleep(wait)
                try:
                    if not os.path.exists(path):
                        return
                    os.remove(path)
                    self.root.after(0, lambda: self.status_var.set(
                        f"Preview deleted after {self._format_delay(delay)}"))
                    return
                except Exception as e:
                    if attempt == 3:
                        print(f"[Cleanup] Could not delete preview after retries: {e}", file=sys.stderr)

        t = threading.Thread(target=_cleanup, daemon=True)
        t.start()

    def _randomize_map_bg(self):
        bg = f"#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}"
        self.map_bg_var.set(bg.upper())
        self.map_bg_prev.config(bg=bg)
        self.status_var.set("Canvas background randomized")

    def _add_node(self):
        if not hasattr(self, '_hierarchy_depth'):
            self._hierarchy_depth = 0
        self._hierarchy_depth += 1
        level = self._hierarchy_depth
        path = ""
        for i in range(1, level + 1):
            path += f"lvl{i}[1]"
        line = f"{path}Heading {level}"
        if self._hierarchy_depth == 1:
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", line)
        else:
            self.input_text.insert(tk.END, chr(10) + line)
        self.status_var.set(f"Level {level}")
        self._update_eq_adjust_button()

    def _remove_node(self):
        if not hasattr(self, '_hierarchy_depth') or self._hierarchy_depth <= 0:
            self.input_text.delete("1.0", tk.END)
            self.status_var.set("Nothing to remove")
            return
        text = self.input_text.get("1.0", tk.END)
        lines = text.splitlines()
        if len(lines) > 0:
            lines.pop()
            self._hierarchy_depth -= 1
        self.input_text.delete("1.0", tk.END)
        if lines:
            self.input_text.insert("1.0", chr(10).join(lines))
        if self._hierarchy_depth > 0:
            self.status_var.set(f"Level {self._hierarchy_depth}")
        else:
            self.status_var.set("Hierarchy cleared")
        self._update_eq_adjust_button()

    _HL_ADDR_RE = re.compile(r'^(?:lvl\d+\[\d+\])+')
    _HL_FIELD_RE = re.compile(
        r'\b(note|equation|equage|eq|label)\s*:\s*"((?:\\.|[^"\\])*)"', re.IGNORECASE)

    def _on_input_text_modified(self, event=None):
        # <<Modified>> fires on ANY change to the widget's content --
        # typed, pasted, or written programmatically (e.g. Manual mode
        # syncing its generated hierarchy text back into this box) --
        # so this one binding covers every way the text can change
        # instead of needing a call added at each individual call site
        # that inserts into input_text. The flag must be reset after
        # each fire or Tkinter won't raise the event again.
        if self.input_text.text.edit_modified():
            self._colorize_input_text()
            self.input_text.text.edit_modified(False)

    def _colorize_input_text(self):
        """Highlight each hierarchy line's structure in Normal mode: the
        leading address ("lvl1[1]lvl2[3]..."), the node name that follows
        it, and the note/equation/label field values inside the {...}
        properties block, each with its own background tag (configured
        where input_text is built). Only does anything when the "Field
        Colors" checkbox (Color Capacity Section, unchecked by default)
        is on -- otherwise any existing highlight tags are cleared."""
        text_widget = self.input_text.text
        for tag in ("hl_address", "hl_nodename", "hl_note", "hl_equation", "hl_label"):
            text_widget.tag_remove(tag, "1.0", tk.END)
        if not getattr(self, 'field_highlight_var', None) or not self.field_highlight_var.get():
            return
        content = text_widget.get("1.0", "end-1c")
        field_tag = {"note": "hl_note", "equation": "hl_equation",
                     "equage": "hl_equation", "eq": "hl_equation", "label": "hl_label"}
        for line_no, line in enumerate(content.split("\n"), start=1):
            m = self._HL_ADDR_RE.match(line)
            if not m:
                continue
            addr_end = m.end()
            text_widget.tag_add("hl_address", f"{line_no}.0", f"{line_no}.{addr_end}")

            brace_idx = line.find('{', addr_end)
            name_end = brace_idx if brace_idx != -1 else len(line)
            name_text = line[addr_end:name_end]
            name_start = addr_end + (len(name_text) - len(name_text.lstrip()))
            name_stop = addr_end + len(name_text.rstrip())
            if name_stop > name_start:
                text_widget.tag_add("hl_nodename", f"{line_no}.{name_start}", f"{line_no}.{name_stop}")

            if brace_idx == -1:
                continue
            for fm in self._HL_FIELD_RE.finditer(line, brace_idx):
                tagname = field_tag.get(fm.group(1).lower())
                if tagname:
                    text_widget.tag_add(tagname, f"{line_no}.{fm.start(2)}", f"{line_no}.{fm.end(2)}")
        text_widget.tag_raise("search_highlight")

    def _update_level_counts(self):
        for lbl in self.level_count_labels.values():
            lbl.destroy()
        self.level_count_labels.clear()
        raw = self.input_text.get("1.0", tk.END).strip()
        if not raw:
            self._set_total_nodes(0)
            self._reflow_level_labels()
            return
        try:
            parser = HierarchyParser(raw)
            entries = copy.deepcopy(parser.parse())
        except Exception:
            self._set_total_nodes(0)
            self._reflow_level_labels()
            return
        self._set_total_nodes(len(entries))
        if not entries:
            self._reflow_level_labels()
            return
        level_counts = {}
        for entry in entries:
            lvl = entry["level"]
            if lvl >= 2:
                level_counts[lvl] = level_counts.get(lvl, 0) + 1
        if not level_counts:
            self._reflow_level_labels()
            return
        for lvl in sorted(level_counts.keys()):
            count = level_counts[lvl]
            lbl = tk.Label(
                self.level_counts_frame,
                text=f"lvl{lvl}={count}",
                bg=self.colors["bg"],
                fg="#888888",
                font=("Consolas", 9)
            )
            self.level_count_labels[lvl] = lbl
        self._reflow_level_labels()

    def _set_total_nodes(self, count: int):
        var = getattr(self, 'total_nodes_var', None)
        if var is not None:
            var.set(f"Total Nodes: {count}")

    def _reflow_level_labels(self, event=None):
        """Wrap the level-count labels onto as many rows as needed instead
        of packing them all in a single side=LEFT row, which used to run
        off the right edge and get clipped once there were enough levels
        (e.g. 18) that they no longer fit on one line. Re-measures and
        re-wraps on every resize of the panel, so it stays correct as the
        window is resized too.

        level_counts_frame is packed with fill=tk.X, so it always spans
        the exact width of bf_container's cavity -- meaning x=0 inside it
        IS bf_container's true left edge, same as the Copy button below.

        Height is adaptive rather than fixed: it reserves a single line
        (LEVEL_COUNTS_ONE_ROW_H) for the normal case -- a handful of
        levels, which is nearly all real maps -- and only grows to fit
        additional wrapped rows when a map actually has enough levels to
        need them (e.g. the 50-level stress-test case). It's only ever
        set to a value derived from the *current* label count, and only
        written when that value actually changes, so retyping the same
        content doesn't re-trigger a resize/jump of bf_container beneath
        it -- only a genuine change in how many rows are needed does."""
        labels = list(self.level_count_labels.values())
        frame = self.level_counts_frame
        row_h, pad_x = 18, 12
        one_row_h = row_h + 4
        if not labels:
            if int(frame["height"]) != one_row_h:
                frame.config(height=one_row_h)
            return
        frame.update_idletasks()
        avail_w = frame.winfo_width()
        if avail_w <= 1:
            bf = getattr(self, 'bf_buttons_frame', None)
            if bf is not None:
                bf.update_idletasks()
            avail_w = (bf.winfo_width() if bf is not None else 0) or \
                      (bf.winfo_reqwidth() if bf is not None else 0) or 480
        x, y, row = 0, 0, 0
        for lbl in labels:
            lbl.place_forget()
            w = lbl.winfo_reqwidth()
            if x > 0 and x + w > avail_w:
                x = 0
                row += 1
                y = row * row_h
            lbl.place(x=x, y=y)
            x += w + pad_x
        target_h = max(one_row_h, (row + 1) * row_h + 4)
        if int(frame["height"]) != target_h:
            frame.config(height=target_h)

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        self.colors = self.dark_colors if self._is_dark else self.light_colors
        self._apply_theme()

    def _apply_theme(self):
        c = self.colors
        self.root.configure(bg=c["bg"])
        self._update_widget_theme(self.root, c)
        self.map_bg_prev.config(bg=self.map_bg_var.get())
        if hasattr(self, 'right_canvas') and self.right_canvas:
            self.right_canvas.config(bg=c["bg"])
        if hasattr(self, 'right_sb') and self.right_sb:
            self.right_sb.config(bg=c["accent"], troughcolor=c["bg"], activebackground=c["select"])
        if self.manual_editor and self.manual_editor.active:
            self.manual_editor.frame.config(bg=c["bg"])
            for widget in self.manual_editor.frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.config(bg=c["bg"])
                    for child in widget.winfo_children():
                        wtype = child.winfo_class()
                        if wtype == "Label":
                            child.config(bg=c["bg"], fg=c["fg"])
                        elif wtype == "Entry":
                            child.config(bg=c["entry_bg"], fg=c["input_fg"], insertbackground=c["input_fg"])
                        elif wtype == "Button":
                            child.config(bg=c["btn_bg"], fg="#000000")
                        elif wtype == "Text":
                            child.config(bg=c["input_bg"], fg=c["input_fg"])
                        elif wtype == "LabelFrame":
                            child.config(bg=c["bg"], fg=c["fg"])
        self.colors_canvas.config(bg=c["bg"])
        self.colors_sb.config(bg=c["accent"], troughcolor=c["bg"], activebackground=c["select"])
        for row in self.color_rows:
            row.fill_prev.config(bg=row.fill_var.get())
            row.font_prev.config(bg=row.font_var.get())
            row.line_prev.config(bg=row.line_var.get())
            row.border_prev.config(bg=row.border_var.get())
            row._style_optionmenu(row.branch_shape_combo, row.branch_shape_var, BRANCH_SHAPE_LABELS)
            row._style_optionmenu(row.node_shape_combo, row.node_shape_var, NODE_SHAPE_LABELS)
        self._style_app_dropdown(self.cat_combo, self.cat_var, list(STRUCTURE_DEFS.keys()))
        self._style_app_dropdown(self.sub_combo, self.sub_var, list(STRUCTURE_DEFS.get(self.cat_var.get(), {}).get("subs", {}).keys()))
        self._style_app_dropdown(self.eq_fmt_combo, self.eq_fmt_var, IMAGE_FORMATS)
        if self.eq_adjust_frame is not None:
            pass  # panel is open -- leave the button disabled, don't override
        elif self._has_equations():
            self.eq_adjust_btn.config(bg="#00b894", fg="#ffffff", state=tk.NORMAL)
        else:
            self.eq_adjust_btn.config(bg="#555555", fg="#888888", state=tk.DISABLED)

    def _update_widget_theme(self, widget, c):
        wtype = widget.winfo_class()
        if wtype in ("Frame", "Tk", "Toplevel"):
            widget.configure(bg=c["bg"])
        elif wtype == "Label":
            try:
                if str(widget.cget("width")) == "2" and str(widget.cget("relief")) == "ridge":
                    pass
                else:
                    widget.configure(bg=c["bg"], fg=c["fg"])
            except:
                widget.configure(bg=c["bg"], fg=c["fg"])
        elif wtype == "Button":
            try:
                current = widget.cget("bg")
                if current in ("#6c5ce7", "#00b894", "#0984e3", "#00b4d8"):
                    pass
                else:
                    widget.configure(bg=c["btn_bg"], fg="#000000",
                                     activebackground=c["accent"], activeforeground="#000000")
            except:
                pass
        elif wtype == "Entry":
            widget.configure(bg=c["entry_bg"], fg="#000000", insertbackground="#000000")
        elif wtype == "Spinbox":
            widget.configure(bg=c["entry_bg"], fg="#000000", insertbackground="#000000")
        elif wtype == "Checkbutton":
            widget.configure(bg=c["bg"], activebackground=c["bg"], selectcolor=c["select"])
        elif wtype == "LabelFrame":
            widget.configure(bg=c["bg"], fg=c["fg"])
        elif wtype == "Canvas":
            widget.configure(bg=c["bg"])
            if hasattr(self, 'right_canvas') and widget is self.right_canvas:
                if hasattr(self, 'right_sb') and self.right_sb:
                    self.right_sb.config(bg=c["accent"], troughcolor=c["bg"], activebackground=c["select"])
        elif wtype == "Scrollbar":
            widget.configure(bg=c["accent"])
        elif wtype == "Menu":
            widget.configure(bg=c["entry_bg"], fg="#000000", activebackground=c["select"], activeforeground="#ffffff")
        elif wtype == "ScrolledText":
            widget.configure(bg=c["input_bg"], fg=c["input_fg"], insertbackground=c["input_fg"])
        elif wtype == "PanedWindow":
            widget.configure(bg=c["bg"])
        for child in widget.winfo_children():
            self._update_widget_theme(child, c)

    def _has_equations(self) -> bool:
        raw = self.input_text.get("1.0", tk.END)
        if not raw.strip():
            return False
        try:
            parser = HierarchyParser(raw)
            entries = copy.deepcopy(parser.parse())
            for entry in entries:
                if entry.get("image_data") and entry["image_data"].get("equation"):
                    return True
            return False
        except:
            return False

    def _update_eq_adjust_button(self):
        if self._has_equations():
            self.eq_adjust_btn.config(state=tk.NORMAL, bg="#00b894", fg="#ffffff")
        else:
            self.eq_adjust_btn.config(state=tk.DISABLED, bg="#555555", fg="#888888")

def main():
    _cleanup_stale_previews()
    root = tk.Tk()
    app = MindMapExporterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
