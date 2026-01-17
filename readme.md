# Wordle Solver AI Agent

A Python **Wordle solver bot** that plays the game automatically using screen reading (`pyautogui`) and algorithmic guessing strategies.

Built as a **learning project** focused on algorithms, constraints, and heuristics rather than perfect optimal play.

---

## ✨ Features

- Plays Wordle automatically via screen interaction
- Reads tile feedback using pixel color detection
- Tracks green / yellow / gray constraints
- Handles **repeated letters** correctly
- Uses **entropy (information gain)** to choose guesses
- Falls back to **probe words** for ambiguous situations (e.g. `_RACE`, `_RAVE`)
- Tracks statistics across many games
- Safe stop with `ESC`

---

## Solver Strategy

### 1. Entropy Guessing (Early Game)

Chooses words that maximize **expected information gain**, quickly shrinking the search space.
    `H(X) = -∑ p_i log(p_i)`

### 2. Probe Words (Ambiguous States)

When remaining candidates exceed remaining turns, the solver plays a **probe word** that:

- Respects known constraints
- Covers as many unknown letters as possible

This avoids wasting turns guessing near-identical answers.

### 3. Direct Guessing (Endgame)

When few candidates remain, the solver directly guesses valid answers.

---

## Repeated Letter Handling

Uses **minimum and maximum letter counts** to correctly interpret Wordle feedback and avoid invalid eliminations.

---

## Example Performance

After 1500+ games (varies by word list):

- Most games solved in **3–5 guesses**
- Significantly higher accurate compared to pure entropy solvers (85% vs ~96%)

Example:

```
Games played: 1528
1 guesses: 2
2 guesses: 13
3 guesses: 275
4 guesses: 652
5 guesses: 417
6 guesses: 101
Failed games: 68
```

---

## Requirements

- Python 3.9+
- `pyautogui`
- `keyboard`
- Wordle running in a browser

⚠️ Screen resolution and OS (Wayland) may require adjustments.
Test was made on "https://wordleunlimited.org", windows, running 1920x1200.

---

## Motivation

This project was built to **learn**:

- Algorithmic problem solving
- Constraint propagation
- Entropy-based heuristics
- Debugging real-world systems

Not intended as a perfect solver.

---

## Future Ideas

- Faster entropy computation
- Offline simulation mode
- Cleaner solver / UI separation
- Better ambiguity detection

---

Made with iterating, debugging, and extending ideas with guidance. The final architecture, experiments, and improvements are mostly mine.