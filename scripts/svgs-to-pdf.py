import os
from pathlib import Path
from svglib.svglib import svg2rlg # type: ignore
from reportlab.graphics import renderPDF # type: ignore
from reportlab.pdfgen import canvas # type: ignore
from reportlab.lib.pagesizes import A2, portrait # type: ignore

# --- Paths ---
script_dir = Path(__file__).parent
project_root = script_dir.parent

svg_folder = project_root / "data" / "svg"
pdf_output = project_root / "data" / "combined" / "combined_a2_1page_black.pdf"

# --- Settings ---
cols, rows = 9, 12  # 9 columns × 12 rows = 108
page_w, page_h = portrait(A2)

# Margins
outer_margin = 100  # around edge of page
inner_margin = 15   # between cells

# Calculate usable space and cell size
usable_w = page_w - 2 * outer_margin - (cols - 1) * inner_margin
usable_h = page_h - 2 * outer_margin - (rows - 1) * inner_margin
cell_w = usable_w / cols
cell_h = usable_h / rows

# Sort helper: handles yyyymmdd and yyyymmdd.1 etc
def extract_sort_key(filename):
    base = Path(filename).stem
    parts = base.split(".")
    date_part = parts[0]
    suffix = int(parts[1]) if len(parts) > 1 else 0
    return (date_part, suffix)

# Load and sort SVGs
svgs = sorted(
    [f for f in svg_folder.glob("*.svg")],
    key=lambda x: extract_sort_key(x.name),
    reverse=True
)[:cols * rows]

# Create canvas
c = canvas.Canvas(str(pdf_output), pagesize=portrait(A2))

# Fill black background
c.setFillColorRGB(0, 0, 0)
c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

# Draw SVGs in grid
for idx, svg_path in enumerate(svgs):
    col = idx % cols
    row = idx // cols

    x = outer_margin + col * (cell_w + inner_margin)
    y = page_h - outer_margin - (row + 1) * cell_h - row * inner_margin

    drawing = svg2rlg(str(svg_path))
    if drawing.width == 0 or drawing.height == 0:
        continue

    # Scale proportionally to fit cell
    scale_x = cell_w / drawing.width
    scale_y = cell_h / drawing.height
    scale = min(scale_x, scale_y)
    drawing.scale(scale, scale)

    renderPDF.draw(drawing, c, x, y)

# Save PDF
c.save()
print(f"One-page A2 PDF with 108 SVGs saved to: {pdf_output}")
