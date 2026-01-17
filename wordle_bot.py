import pyautogui
import time
import math
import keyboard
from collections import Counter

# config
TILES_X = [797, 865, 933, 1000, 1068]  # corner of tiles, watever aka row[1-> 6][0]
TILE_Y_START = 393                  # first row Y aka row[0][0]
ROW_GAP = 70                        # distance between rows aka row[-][1]

guess_histogram = {i: 0 for i in range(1, 7)}
stop_ai = False
game_count = 0
fail_count = 0

# local vars
class wordleState:
    def __init__(self, all_words):
        self.all_words = all_words
        self.reset()

    def reset(self):
        self.greens = [None] * 5
        self.yellows = [set() for _ in range(5)]
        self.grays = set()
        self.guessed_words = set()
        self.possible = self.all_words.copy()
        self.last_feedback = None
        self.min_count = Counter()
        self.max_count = {}

def update_constraints(guess, fb, state):
    guess_count = Counter()

    for i in range(5):
        if fb[i] in ("g", "y"):
            guess_count[guess[i]] += 1

    for i in range(5):
        c = guess[i]

        if fb[i] == "g":
            state.greens[i] = c

        elif fb[i] == "y":
            state.yellows[i].add(c)

        elif fb[i] == "b":
            if c in guess_count:
                # letter exists but limited
                state.max_count[c] = min(
                    state.max_count.get(c, float("inf")),
                    guess_count[c]
                )
            else:
                # letter does not exist
                state.max_count[c] = 0

    for c in guess_count:
        state.min_count[c] = max(
            state.min_count.get(c, 0),
            guess_count[c]
        )

# color checking
def classify_color(pixel):
    r, g, b = pixel
    # gray
    if abs(r - g) < 15 and abs(r - b) < 15:
        return "b"
    # green
    if g > r and g > b:
        return "g"
    # yellow
    return "y"

def read_feedback(row):
    y = TILE_Y_START + row * ROW_GAP
    screenshot = pyautogui.screenshot()
    fb = ""
    for x in TILES_X:
        fb += classify_color(screenshot.getpixel((x, y)))
    return fb

def is_green(pixel):
    r, g, b = pixel
    return g > 120 and g > r + 20 and g > b + 20

# wordle logic
def get_feedback(guess, answer):
    fb = ["b"] * 5
    used = [False] * 5
    # green
    for i in range(5):
        if guess[i] == answer[i]:
            fb[i] = "g"
            used[i] = True
    # yellow
    for i in range(5):
        if fb[i] == "g":
            continue
        for j in range(5):
            if not used[j] and guess[i] == answer[j]:
                fb[i] = "y"
                used[j] = True
                break

    return "".join(fb)

def valid(word, state):
    # position conscrane
    # crtraints
    for i in range(5):
        if state.greens[i] and word[i] != state.greens[i]:
            return False
        for c in state.yellows[i]:
            if word[i] == c:
                return False

    cnt = Counter(word)

    # minimum counts
    for c in state.min_count:
        if cnt[c] < state.min_count[c]:
            return False

    # maximum counts
    for c in state.max_count:
        if cnt[c] > state.max_count[c]:
            return False

    return True


# logic for hard words etc _acer (r l m p n s)
def is_probe_safe(word, state):
    for c in word:
        if c in state.max_count and state.max_count[c] == 0:
            return False

    for i in range(5):
        for c in state.yellows[i]:
            if word[i] == c:
                return False

    return True

def choose_probe_word(state):
    candidates = [
        w for w in state.all_words
        if w not in state.guessed_words and is_probe_safe(w, state)
    ]

    unknown_positions = [
        i for i in range(5)
        if state.greens[i] is None
    ]

    letter_freq = Counter()
    for w in state.possible:
        for i in unknown_positions:
            letter_freq[w[i]] += 1

    def score(w):
        return sum(letter_freq[c] for c in set(w) if c in letter_freq)

    return max(candidates, key=score)

# check if word from filee is invalid
def row_changed(row):
    y = TILE_Y_START + row * ROW_GAP
    screenshot = pyautogui.screenshot()

    for x in TILES_X:
        r, g, b = screenshot.getpixel((x, y))
        if r + g + b > 70:
            return True  # something appeared
    return False

# entropy to find best word
def entropy(guess, possible):
    patterns = Counter()

    for answer in possible:
        fb = get_feedback(guess, answer)
        patterns[fb] += 1

    total = len(possible)
    H = 0.0
    for count in patterns.values():
        p = count / total
        H -= p * math.log2(p)
    return H

def choose_word(state, turns_left):
    if len(state.possible) > turns_left:
        return choose_probe_word(state)

    pool = state.possible if len(state.possible) < 40 else state.all_words

    entropy_cache = {}

    best_word = None
    best_score = -1
    for w in pool:
        if w in state.guessed_words:
            continue

        if should_stop():
            return None
        
        if len(state.possible) > 100 and len(set(w)) < 5:
            continue

        if w not in entropy_cache:
            entropy_cache[w] = entropy(w, state.possible)
        score = entropy_cache[w]

        if score > best_score:
            best_score = score
            best_word = w

    return best_word

# keyboard actions
def type_word(word):
    pyautogui.write(word, interval=0.1)
    pyautogui.press("enter")
    time.sleep(2.3)

def clear_word():
    for _ in range(5):
        pyautogui.press("backspace")

def stop():
    global stop_ai
    stop_ai = True
    print("Stopping requested")

def should_stop():
    return stop_ai

keyboard.add_hotkey("esc", stop)

# mai
with open("D:\\home\\izu\\Izu\\Projects\\wordle_bot\\words.txt") as f:
    ALL_WORDS = [w.strip().lower() for w in f if len(w.strip()) == 5]

state = wordleState(ALL_WORDS)
state.possible = ALL_WORDS.copy()

print("Wordle AI starting in 3...")
pyautogui.moveTo(764, 825)
pyautogui.leftClick()
time.sleep(3)

FIRST_GUESS = "crane"

def play_one_game():
    global stop_ai, state
    state.reset()

    if should_stop():
        print("Stopped before starting game")
        return

    turn = 0
    while turn < 6:
        if should_stop():
            print("Stopped during game")
            return

        if turn == 0:
            guess = FIRST_GUESS
        elif state.last_feedback == "bbbbb" and turn == 1:
            guess = "toils"
        else:
            print("Choosing word...")
            guess = choose_word(state, 6 - turn)
            print("Chosen:", guess)

            if guess is None:
                return
        state.guessed_words.add(guess)

        print(f"\nTurn {turn + 1}")
        print("Guess:", guess)
        type_word(guess)
        time.sleep(0.1)

        # invalid word detection
        if not row_changed(turn):

            print("Invalid word:", guess)

            if guess in state.possible:
                state.possible.remove(guess)

            clear_word()
            print("Remaining possible:", len(state.possible))
            continue

        fb = read_feedback(turn)
        state.last_feedback = fb
        print("Feedback:", fb)

        if fb == "ggggg":
            print("\nSolved.!")
            return turn + 1

        update_constraints(guess, fb, state)
        state.possible = [w for w in state.possible if valid(w, state)]

        print("Remaining candidates:", len(state.possible))

        if not state.possible:
            print("No valid words left")
            for turn in range(6):
                type_word(FIRST_GUESS)
            return None
        turn += 1

while True:
    if should_stop():
        print("Stopped main loop")
        break

    result = play_one_game()

    if result is not None:
        game_count += 1
        guess_histogram[result] += 1
    else:
        game_count += 1
        fail_count += 1
    time.sleep(2)

    while True:
        if stop_ai:
            print("\n Game stats")
            print("Games played:", game_count)
            print("Guesses distribution:")

            for i in range(1, 7):
                print(f"{i} guesses: {guess_histogram[i]}")

            print("Failed games:", fail_count)
            break

        if is_green(pyautogui.pixel(764, 825)):
            pyautogui.moveTo(764, 825)
            time.sleep(0.1)
            pyautogui.leftClick()
            break

    time.sleep(1)