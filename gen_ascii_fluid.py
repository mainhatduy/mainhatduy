import math
import os

OUTPUT_DIR = "/home/myduy/Workspace/personal/mainhatduy"
OUTPUT_SVG = os.path.join(OUTPUT_DIR, "ascii_fluid.svg")

# Grid configuration for 896x252 space (32:9 aspect ratio)
COLS = 132
ROWS = 21
FONT_SIZE = 11
LINE_HEIGHT = 11.2
START_X = 12
START_Y = 16

NUM_FRAMES = 90
LOOP_DURATION = 3000.0  # 3s loop
FRAME_DURATION = 3000.0 / 90.0  # ~33.33ms per frame (30 FPS)

# Background text (Feynman's introduction text)
FEYNMAN_TEXT = (
    "Simulating Physics with Computers Richard P. Feynman Department of Physics, "
    "California Institute of Technology, Pasadena, California 91107 Received May 7, 1981 "
    "1. INTRODUCTION On the program it says this is a keynote speech--and I don't know "
    "what a keynote speech is. I do not intend in any way to suggest what should "
    "be in this meeting as a keynote of the subjects or anything like that. I have "
    "my own things to say and to talk about and there's no implication that "
    "anybody needs to talk about the same thing or anything like it. So what I "
    "want to talk about is what Mike Dertouzos suggested that nobody would "
    "talk about. I want to talk about the problem of simulating physics with "
    "computers and I mean that in a specific way which I am going to explain. "
    "The reason for doing this is something that I learned about from Ed "
    "Fredkin, and my entire interest in the subject has been inspired by him. It "
    "has to do with learning something about the possibilities of computers, and "
    "also something about possibilities in physics. If we suppose that we know all "
    "the physical laws perfectly, of course we don't have to pay any attention to "
    "computers. It's interesting anyway to entertain oneself with the idea that "
    "we've got something to learn about physical laws; and if I take a relaxed "
    "view here (after all I'm here and not at home) I'll admit that we don't "
    "understand everything. The first question is, What kind of computer are we going to use to "
    "simulate physics? Computer theory has been developed to a point where it "
    "realizes that it doesn't make any difference; when you get to a universal "
    "computer, it doesn't matter how it's manufactured, how it's actually made. "
    "Therefore my question is, Can physics be simulated by a universal computer? "
    "I would like to have the elements of this computer locally interconnected, and "
    "therefore sort of think about cellular automata as an example (but I don't want "
    "to force it). But I do want something involved with the locality of interaction. "
    "I would not like to think of a very enormous computer with arbitrary interconnections "
    "throughout the entire thing. "
)

# Build the background text grid
GRID = []
word_index = 0
words = FEYNMAN_TEXT.split()
for r in range(ROWS):
    line = ""
    while len(line) < COLS:
        if len(line) > 0:
            line += " "
        line += words[word_index % len(words)]
        word_index += 1
    GRID.append(line[:COLS])

# --- Name overlay configuration ---
# Name is rendered as a separate layer on top of the wave
NAME = "MAI NHAT DUY"
NAME_FONT_SIZE = 36  # Double the size (previously 18)

CHARS = ".,·-─~+:;=*π┐┌┘╔╝║╚!?1742&35$690#@8$▀▄■░▒▓"


def hash_func_3d(x, y, z):
    n = math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453
    return n - math.floor(n)


def get_wave_intensity(px, py, now):
    age = now
    life = 1.0 - (age / LOOP_DURATION)

    # BandWidth decays over time (shrinks and narrows)
    band_half = (268.0 / 2.0) * math.pow(max(0.0, life), 2.5)
    if band_half < 0.5:
        return -1.0

    front = band_half
    wake = band_half * 2.2
    radius = (age / 1000.0) * 670.0  # speed is 670 px/s

    # Wobble calculation (organic wave front ripple)
    wobble = (
        math.sin(py * 0.05 + age * 0.004) * 0.45
        + math.sin(py * 0.08 - age * 0.006) * 0.30
        + math.sin(py * 0.13 + age * 0.002) * 0.18
    ) * 4.0

    x_crest = -200.0 + radius + wobble
    gap = x_crest - px

    if gap < -front or gap > wake:
        return -1.0

    t_val = 1.0 + gap / front if gap < 0.0 else 1.0 - gap / wake
    envelope = t_val * t_val * (3.0 - 2.0 * t_val)  # smoothstep

    return envelope * life


def pick_char(col, row, intensity, now, wave_id):
    target = intensity * (len(CHARS) - 1)
    seed = int(now / 76.0) + wave_id
    jitter = (hash_func_3d(col, row, seed) - 0.5) * len(CHARS) * 0.25
    char_idx = int(round(target + jitter))
    char_idx = max(0, min(len(CHARS) - 1, char_idx))
    return CHARS[char_idx]


# Generate frames
frames = []
for f_idx in range(NUM_FRAMES):
    now = f_idx * FRAME_DURATION
    grid_chars = []
    grid_colors = []
    grid_bold = []

    for r in range(ROWS):
        row_chars = []
        row_colors = []
        row_bold = []
        py = START_Y + r * LINE_HEIGHT

        for c in range(COLS):
            px = START_X + c * (FONT_SIZE * 0.6)
            orig_char = GRID[r][c]

            # Feynman name highlight remains green
            is_feynman_name = r == 0 and 34 <= c <= 51

            if is_feynman_name:
                char = orig_char
                color = "rgb(74,222,128)"  # Feynman name: Green
                bold = True
            else:
                intensity = get_wave_intensity(px, py, now)
                threshold = hash_func_3d(c, r, 0)
                bold = False

                if intensity > 0.08 and threshold <= intensity * 1.25:
                    char = pick_char(c, r, intensity, now, 0)
                    # White wave with brightness variation
                    clamped = min(1.0, intensity)
                    brightness = int(180 + 75 * clamped)
                    color = f"rgb({brightness},{brightness},{brightness})"
                else:
                    char = orig_char
                    color = "rgb(75,75,75)"  # Background text: Gray

            row_chars.append(char)
            row_colors.append(color)
            row_bold.append(bold)

        grid_chars.append(row_chars)
        grid_colors.append(row_colors)
        grid_bold.append(row_bold)

    frames.append((grid_chars, grid_colors, grid_bold))

# Write SVG file
spritesheet_height = NUM_FRAMES * 252
svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 896 252" width="896" height="252">
  <defs>
    <!-- Rounded corners clipping -->
    <clipPath id="card-clip">
      <rect width="896" height="252" rx="16" />
    </clipPath>
  </defs>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@900&amp;display=swap');

    .ascii-text {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: {FONT_SIZE}px;
      font-weight: 700;
      white-space: pre;
      letter-spacing: 0.5px;
    }}
    .overlay-name {{
      font-family: 'Cinzel', serif;
      font-size: {NAME_FONT_SIZE}px;
      font-weight: 900;
      fill: rgb(255, 255, 255);
      dominant-baseline: middle;
      letter-spacing: 6px;
    }}
    .spritesheet {{
      animation: play 3.0s steps({NUM_FRAMES}) infinite;
    }}
    @keyframes play {{
      to {{
        transform: translateY(-{spritesheet_height}px);
      }}
    }}
  </style>

  <g clip-path="url(#card-clip)">
    <!-- Animated spritesheet container -->
    <g class="spritesheet">
"""

for f_idx, (grid_chars, grid_colors, grid_bold) in enumerate(frames):
    y_offset = f_idx * 252
    svg_content += f"      <!-- Frame {f_idx} -->\n"
    svg_content += f'      <text class="ascii-text" x="{START_X}" y="{y_offset + START_Y}">\n'

    for r_idx in range(ROWS):
        current_color = grid_colors[r_idx][0]
        current_bold = grid_bold[r_idx][0]
        consecutive_text = ""

        svg_content += f'        <tspan x="{START_X}" dy="{LINE_HEIGHT if r_idx > 0 else 0}px">'

        for c_idx in range(COLS):
            char = grid_chars[r_idx][c_idx]
            color = grid_colors[r_idx][c_idx]
            bold = grid_bold[r_idx][c_idx]
            escaped_char = (
                char.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )

            if color == current_color and bold == current_bold:
                consecutive_text += escaped_char
            else:
                bold_attr = ' font-weight="900"' if current_bold else ""
                svg_content += f'<tspan fill="{current_color}"{bold_attr}>{consecutive_text}</tspan>'
                consecutive_text = escaped_char
                current_color = color
                current_bold = bold

        # Append the last chunk of the row
        bold_attr = ' font-weight="900"' if current_bold else ""
        svg_content += f'<tspan fill="{current_color}"{bold_attr}>{consecutive_text}</tspan></tspan>\n'

    svg_content += "      </text>\n"
    # Layer 2: Name overlay on top of the wave
    svg_content += f'      <text class="overlay-name" x="448" y="{y_offset + 126}" text-anchor="middle">{NAME}</text>\n'

svg_content += """    </g>
  </g>
</svg>
"""

with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"Successfully generated White Wave Banner at {OUTPUT_SVG}")
print(f"  - Name '{NAME}' as overlay layer (font: {NAME_FONT_SIZE}px)")
print(f"  - Wave color: White with brightness variation")
print(f"  - 2-layer: wave underneath, name on top")
