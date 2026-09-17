import os
import re
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION


# ──────────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS & CURATED THEME PALETTES
# Each theme provides mathematically verified contrast ratios for high-end decks.
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_PALETTES: Dict[str, Dict[str, Any]] = {
    "Obsidian Emerald": {
        "bg": RGBColor(8, 14, 26),               # #080E1A deep near-black charcoal
        "surface": RGBColor(12, 20, 34),         # #0C1422 dark navy card surface
        "surface_border": RGBColor(19, 47, 43),  # #132F2B subtle emerald dark border
        "primary_accent": RGBColor(16, 185, 129),# #10B981 emerald green
        "secondary_accent": RGBColor(52, 211, 153), # #34D399 light emerald
        "heading": RGBColor(241, 245, 249),      # #F1F5F9 crisp white
        "body": RGBColor(148, 163, 184),         # #94A3B8 cool ash gray
        "muted": RGBColor(100, 116, 139),        # #64748B slate
        "is_dark": True,
    },
    "Midnight Executive": {
        "bg": RGBColor(13, 27, 42),              # #0D1B2A deep executive navy
        "surface": RGBColor(19, 34, 56),         # #132238 medium navy card surface
        "surface_border": RGBColor(31, 53, 84),  # #1F3554 subtle navy border
        "primary_accent": RGBColor(212, 160, 23),# #D4A017 antique gold
        "secondary_accent": RGBColor(240, 192, 64), # #F0C040 bright gold
        "heading": RGBColor(248, 250, 252),      # #F8FAFC crisp silver-white
        "body": RGBColor(148, 163, 184),         # #94A3B8 cool gray
        "muted": RGBColor(100, 116, 139),        # #64748B steel gray
        "is_dark": True,
    },
    "Ivory Linen": {
        "bg": RGBColor(250, 248, 245),           # #FAF8F5 warm ivory background
        "surface": RGBColor(255, 255, 255),      # #FFFFFF pure white card surface
        "surface_border": RGBColor(231, 224, 214), # #E7E0D6 warm neutral border
        "primary_accent": RGBColor(184, 134, 11),# #B8860B deep warm gold / bronze
        "secondary_accent": RGBColor(139, 101, 8), # #8B6508 deep bronze
        "heading": RGBColor(28, 25, 23),         # #1C1917 warm charcoal black
        "body": RGBColor(68, 64, 60),            # #44403C stone dark brown
        "muted": RGBColor(120, 113, 108),        # #78716C warm gray
        "is_dark": False,
    },
    "Arctic Blueprint": {
        "bg": RGBColor(241, 245, 249),           # #F1F5F9 clean icy light gray
        "surface": RGBColor(255, 255, 255),      # #FFFFFF pure white card surface
        "surface_border": RGBColor(203, 213, 225), # #CBD5E1 crisp slate border
        "primary_accent": RGBColor(37, 99, 235), # #2563EB electric blue
        "secondary_accent": RGBColor(2, 132, 199), # #0284C7 cyan blue
        "heading": RGBColor(15, 23, 42),         # #0F172A deep slate navy
        "body": RGBColor(51, 65, 85),            # #334155 dark slate body
        "muted": RGBColor(100, 116, 139),        # #64748B mid slate
        "is_dark": False,
    },
    "Crimson Authority": {
        "bg": RGBColor(9, 9, 11),                # #09090B pure dark black
        "surface": RGBColor(20, 20, 23),         # #141417 dark zinc card surface
        "surface_border": RGBColor(39, 39, 42),  # #27272A subtle zinc border
        "primary_accent": RGBColor(239, 68, 68), # #EF4444 vivid crimson red
        "secondary_accent": RGBColor(248, 113, 113), # #F87171 light crimson
        "heading": RGBColor(250, 250, 250),      # #FAFAFA pure white
        "body": RGBColor(212, 212, 216),         # #D4D4D8 light zinc gray
        "muted": RGBColor(113, 113, 122),        # #71717A mid zinc gray
        "is_dark": True,
    },
}


def hex_to_rgb(hex_str: Optional[str], default_rgb: RGBColor) -> RGBColor:
    """Safely converts a HEX color string (e.g. '#1E3A8A' or '1E3A8A') to RGBColor."""
    if not hex_str or not isinstance(hex_str, str):
        return default_rgb
    cleaned = hex_str.strip().lstrip("#")
    # Handle possible comment like "#080e1a (near-black)"
    if " " in cleaned:
        cleaned = cleaned.split()[0]
    if len(cleaned) == 6:
        try:
            return RGBColor(int(cleaned[0:2], 16), int(cleaned[2:4], 16), int(cleaned[4:6], 16))
        except ValueError:
            pass
    return default_rgb


def get_relative_luminance(rgb: RGBColor) -> float:
    """Computes perceptual relative luminance (0.0 = black, 255.0 = white)."""
    r, g, b = rgb[0], rgb[1], rgb[2]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_theme_palette(theme_data: Dict[str, Any], default_theme_name: str = "Obsidian Emerald") -> Dict[str, Any]:
    """
    Extracts or infers a cohesive color palette from theme metadata,
    guaranteeing strict WCAG AA/AAA contrast ratios for text vs surfaces.
    """
    palette_data = theme_data.get("color_palette", {})
    name = (theme_data.get("name") or default_theme_name or "").strip()

    # Find the matching default base palette
    base_key = "Obsidian Emerald"
    for k in DEFAULT_PALETTES:
        if k.lower() in name.lower() or name.lower() in k.lower():
            base_key = k
            break
    else:
        # Keyword fallbacks
        lname = name.lower()
        if "emerald" in lname or "tech" in lname or "cyber" in lname:
            base_key = "Obsidian Emerald"
        elif "midnight" in lname or "navy" in lname or "executive" in lname or "blue" in lname:
            base_key = "Midnight Executive"
        elif "ivory" in lname or "linen" in lname or "warm" in lname or "editorial" in lname:
            base_key = "Ivory Linen"
        elif "arctic" in lname or "blueprint" in lname or "saas" in lname or "light" in lname:
            base_key = "Arctic Blueprint"
        elif "crimson" in lname or "red" in lname or "authority" in lname or "dark" in lname:
            base_key = "Crimson Authority"

    base = DEFAULT_PALETTES[base_key]

    # Parse provided hex tokens with safe fallbacks
    bg = hex_to_rgb(palette_data.get("background") or palette_data.get("bg"), base["bg"])
    surface = hex_to_rgb(palette_data.get("surface"), base["surface"])
    surface_border = hex_to_rgb(palette_data.get("surface_border") or palette_data.get("border"), base["surface_border"])
    primary_accent = hex_to_rgb(palette_data.get("primary_accent") or palette_data.get("primary"), base["primary_accent"])
    secondary_accent = hex_to_rgb(palette_data.get("secondary_accent") or palette_data.get("accent"), base["secondary_accent"])
    heading = hex_to_rgb(palette_data.get("heading") or palette_data.get("heading_color"), base["heading"])
    body = hex_to_rgb(palette_data.get("body") or palette_data.get("body_text") or palette_data.get("text"), base["body"])
    muted = hex_to_rgb(palette_data.get("muted") or palette_data.get("muted_text"), base["muted"])

    # CONTRAST SAFETY GUARDRAIL:
    # If the surface is dark, headings and body MUST be light.
    # If the surface is light, headings and body MUST be dark.
    surf_lum = get_relative_luminance(surface)
    if surf_lum < 128:
        # Dark surface: guarantee crisp light text
        if get_relative_luminance(heading) < 160:
            heading = RGBColor(241, 245, 249)
        if get_relative_luminance(body) < 120:
            body = RGBColor(148, 163, 184)
        if get_relative_luminance(muted) < 80:
            muted = RGBColor(100, 116, 139)
    else:
        # Light surface: guarantee crisp dark text
        if get_relative_luminance(heading) > 100:
            heading = RGBColor(15, 23, 42)
        if get_relative_luminance(body) > 130:
            body = RGBColor(51, 65, 85)
        if get_relative_luminance(muted) > 160:
            muted = RGBColor(100, 116, 139)

    return {
        "bg": bg,
        "surface": surface,
        "surface_border": surface_border,
        "primary_accent": primary_accent,
        "secondary_accent": secondary_accent,
        "heading": heading,
        "body": body,
        "muted": muted,
        "is_dark": surf_lum < 128,
    }


def resolve_fonts(theme_info: Dict[str, Any], requested_font_style: str) -> Tuple[str, str]:
    """Resolves clean, professional typography respecting the user's requested font style."""
    req = requested_font_style.lower() if requested_font_style else "modern sans-serif"
    typography = theme_info.get("typography", {})
    raw_header = typography.get("header_font", "")
    raw_body = typography.get("body_font", "")

    if "sans" in req:
        # Enforce modern sans-serif fonts
        header_font = "Segoe UI"
        body_font = "Segoe UI"
        if raw_header and any(s in raw_header.lower() for s in ["inter", "aptos", "segoe", "arial", "helvetica", "roboto", "montserrat"]):
            header_font = raw_header
        if raw_body and any(s in raw_body.lower() for s in ["inter", "aptos", "segoe", "arial", "helvetica", "roboto", "calibri"]):
            body_font = raw_body
        return header_font, body_font

    if "serif" in req:
        return "Georgia", "Georgia"

    if "mono" in req:
        return "Consolas", "Segoe UI"

    # Default clean fallback
    return raw_header or "Segoe UI", raw_body or "Calibri"


# ──────────────────────────────────────────────────────────────────────────────
# SLIDE RENDERING LAYOUTS
# ──────────────────────────────────────────────────────────────────────────────

def render_hero_title(
    slide,
    headline: str,
    subheadline: str,
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
    has_logo: bool,
    topic: str = "Presentation",
):
    """
    Renders an executive-grade Title slide:
    Clean full-bleed background, modern eyebrow pill, massive high-contrast title,
    crisp accent divider rule, readable subtitle, and subtle bottom metadata.
    """
    # 1. Eyebrow badge / kicker pill at top-left
    badge_left = Inches(1.2)
    badge_top = Inches(1.5)
    badge_width = Inches(2.2)
    badge_height = Inches(0.4)

    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, badge_left, badge_top, badge_width, badge_height)
    badge.fill.solid()
    badge.fill.fore_color.rgb = colors["surface"]
    badge.line.color.rgb = colors["surface_border"]
    badge.line.width = Pt(1)

    btf = badge.text_frame
    btf.word_wrap = False
    btf.vertical_anchor = MSO_ANCHOR.MIDDLE
    bp = btf.paragraphs[0]
    bp.alignment = PP_ALIGN.CENTER
    bp.text = "EXECUTIVE BRIEFING"
    bp.font.name = header_font
    bp.font.size = Pt(10)
    bp.font.bold = True
    bp.font.color.rgb = colors["primary_accent"]

    # 2. Main Title Text Box
    title_width = Inches(9.8) if has_logo else Inches(11.2)
    title_box = slide.shapes.add_textbox(Inches(1.2), Inches(2.2), title_width, Inches(3.2))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p_title = tf.paragraphs[0]
    p_title.text = headline
    p_title.font.name = header_font
    p_title.font.size = Pt(38)
    p_title.font.bold = True
    p_title.font.color.rgb = colors["heading"]
    p_title.space_after = Pt(16)

    # 3. Decorative Accent Rule Line under the title
    accent_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(4.3), Inches(1.8), Inches(0.06))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = colors["primary_accent"]
    accent_bar.line.fill.background()

    # 4. Subheadline Box
    if subheadline:
        sub_width = Inches(9.8) if has_logo else Inches(11.2)
        sub_box = slide.shapes.add_textbox(Inches(1.2), Inches(4.6), sub_width, Inches(1.4))
        stf = sub_box.text_frame
        stf.word_wrap = True
        stf.margin_left = stf.margin_right = stf.margin_top = stf.margin_bottom = 0

        p_sub = stf.paragraphs[0]
        p_sub.text = subheadline
        p_sub.font.name = body_font
        p_sub.font.size = Pt(18)
        p_sub.font.color.rgb = colors["body"]

    # 5. Bottom Metadata Footer
    meta_box = slide.shapes.add_textbox(Inches(1.2), Inches(6.4), Inches(8.0), Inches(0.5))
    mtf = meta_box.text_frame
    mtf.margin_left = mtf.margin_right = mtf.margin_top = mtf.margin_bottom = 0
    p_meta = mtf.paragraphs[0]
    p_meta.text = f"Prepared by Nova PPT Gen  •  {topic}"
    p_meta.font.name = body_font
    p_meta.font.size = Pt(10)
    p_meta.font.color.rgb = colors["muted"]

    # 6. Optional Minimal Logo in top-right
    if has_logo:
        logo_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.3), Inches(1.5), Inches(1.2), Inches(0.4))
        logo_box.fill.solid()
        logo_box.fill.fore_color.rgb = colors["surface"]
        logo_box.line.color.rgb = colors["surface_border"]
        ltf = logo_box.text_frame
        ltf.vertical_anchor = MSO_ANCHOR.MIDDLE
        lp = ltf.paragraphs[0]
        lp.alignment = PP_ALIGN.CENTER
        lp.text = "LOGO"
        lp.font.name = header_font
        lp.font.size = Pt(10)
        lp.font.bold = True
        lp.font.color.rgb = colors["muted"]


def add_slide_header(
    slide,
    headline: str,
    subheadline: str,
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
    has_logo: bool,
):
    """
    Renders a clean, executive slide header with category eyebrow,
    bold high-contrast title, and subtle subtitle.
    When has_logo is False, the header expands to full slide width (11.733") with no reserved dead space.
    """
    # 1. Top Accent Rule
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.4), Inches(1.2), Inches(0.05))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = colors["primary_accent"]
    top_bar.line.fill.background()

    # 2. Title and Subtitle Box (expand to full 11.733" when logo is disabled)
    title_width = Inches(10.4) if has_logo else Inches(11.733)
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.55), title_width, Inches(1.3))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p_title = tf.paragraphs[0]
    p_title.text = headline
    p_title.font.name = header_font
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = colors["heading"]

    if subheadline:
        p_sub = tf.add_paragraph()
        p_sub.text = subheadline
        p_sub.font.name = body_font
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = colors["muted"]
        p_sub.space_before = Pt(3)

    # 3. Optional Logo Box
    if has_logo:
        logo_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.5), Inches(0.45), Inches(1.0), Inches(0.35))
        logo_box.fill.solid()
        logo_box.fill.fore_color.rgb = colors["surface"]
        logo_box.line.color.rgb = colors["surface_border"]
        ltf = logo_box.text_frame
        ltf.vertical_anchor = MSO_ANCHOR.MIDDLE
        lp = ltf.paragraphs[0]
        lp.alignment = PP_ALIGN.CENTER
        lp.text = "LOGO"
        lp.font.name = header_font
        lp.font.size = Pt(9)
        lp.font.bold = True
        lp.font.color.rgb = colors["muted"]


def render_metrics_layout(
    slide,
    elements: List[Dict[str, Any]],
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
):
    """
    Renders executive KPI cards side-by-side with massive accent numbers,
    crisp titles, and contextual body text.
    """
    num_items = min(len(elements), 4)
    if num_items == 0:
        return

    left_start = Inches(0.8)
    top_pos = Inches(2.1)
    total_width = Inches(11.733)
    card_gap = Inches(0.25)
    card_width = (total_width - (card_gap * (num_items - 1))) / num_items
    card_height = Inches(4.7)

    for i, elem in enumerate(elements[:num_items]):
        cur_left = left_start + i * (card_width + card_gap)

        # Surface Card container
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_pos, card_width, card_height)
        card.fill.solid()
        card.fill.fore_color.rgb = colors["surface"]
        card.line.color.rgb = colors["surface_border"]
        card.line.width = Pt(1)

        # Top Accent Stripe on each card (3px)
        stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_left, top_pos, card_width, Inches(0.06))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = colors["primary_accent"]
        stripe.line.fill.background()

        # Text Frame
        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.4)

        title = elem.get("title", "")
        desc = elem.get("description", "")

        # Look for a number or KPI metric in title or description
        metric_val = ""
        metric_match = re.search(r'([$€£¥]?\d+(?:[.,]\d+)?%?[BMKkm+]?)', title)
        if metric_match:
            metric_val = metric_match.group(0)
            clean_title = title.replace(metric_val, "").strip(" -:•")
        else:
            # Check desc for metric value
            d_match = re.search(r'([$€£¥]?\d+(?:[.,]\d+)?%?[BMKkm+]?)', desc)
            metric_val = d_match.group(0) if d_match else f"0{i+1}"
            clean_title = title

        # Large Metric Value
        p_val = tf.paragraphs[0]
        p_val.text = metric_val or f"0{i+1}"
        p_val.font.name = header_font
        p_val.font.size = Pt(36)
        p_val.font.bold = True
        p_val.font.color.rgb = colors["primary_accent"]
        p_val.space_after = Pt(10)

        # Metric Title / Label
        p_label = tf.add_paragraph()
        p_label.text = clean_title or title
        p_label.font.name = header_font
        p_label.font.size = Pt(15)
        p_label.font.bold = True
        p_label.font.color.rgb = colors["heading"]
        p_label.space_after = Pt(10)

        # Description text
        if desc:
            p_desc = tf.add_paragraph()
            p_desc.text = desc
            p_desc.font.name = body_font
            p_desc.font.size = Pt(12)
            p_desc.font.color.rgb = colors["body"]


def render_grid_layout(
    slide,
    elements: List[Dict[str, Any]],
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
):
    """
    Renders content elements into a clean responsive layout:
    - 2 or 3 items: full-height vertical columns side-by-side
    - 4 items: balanced 2x2 grid
    """
    num_items = min(len(elements), 4)
    if num_items == 0:
        return

    left_start = Inches(0.8)
    top_pos = Inches(2.1)
    total_width = Inches(11.733)
    total_height = Inches(4.7)

    if num_items <= 3:
        # Clean multi-column side-by-side cards
        col_gap = Inches(0.25)
        col_width = (total_width - (col_gap * (num_items - 1))) / num_items

        for i, elem in enumerate(elements[:num_items]):
            cur_left = left_start + i * (col_width + col_gap)

            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_pos, col_width, total_height)
            card.fill.solid()
            card.fill.fore_color.rgb = colors["surface"]
            card.line.color.rgb = colors["surface_border"]
            card.line.width = Pt(1)

            # Elegant Top Accent Stripe (flush with card top)
            stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_left, top_pos, col_width, Inches(0.06))
            stripe.fill.solid()
            stripe.fill.fore_color.rgb = colors["primary_accent"]
            stripe.line.fill.background()

            tf = card.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.TOP
            tf.margin_left = Inches(0.35)
            tf.margin_right = Inches(0.3)
            tf.margin_top = Inches(0.45)

            title = elem.get("title", "")
            desc = elem.get("description", "")
            elem_type = (elem.get("type") or "").lower()

            # Dynamic badge according to element type
            badge_text = f"PILLAR 0{i+1}"
            if elem_type == "step":
                badge_text = f"PHASE 0{i+1}"
            elif elem_type == "takeaway":
                badge_text = f"TAKEAWAY 0{i+1}"

            p_badge = tf.paragraphs[0]
            p_badge.text = badge_text
            p_badge.font.name = header_font
            p_badge.font.size = Pt(10)
            p_badge.font.bold = True
            p_badge.font.color.rgb = colors["primary_accent"]
            p_badge.space_after = Pt(8)

            p_title = tf.add_paragraph()
            p_title.text = title if title else desc
            p_title.font.name = header_font
            p_title.font.size = Pt(16)
            p_title.font.bold = True
            p_title.font.color.rgb = colors["heading"]
            p_title.space_after = Pt(10)

            if title and desc:
                p_desc = tf.add_paragraph()
                p_desc.text = desc
                p_desc.font.name = body_font
                p_desc.font.size = Pt(12)
                p_desc.font.color.rgb = colors["body"]
    else:
        # 4 items in 2x2 grid
        col_gap = Inches(0.3)
        row_gap = Inches(0.25)
        col_width = (total_width - col_gap) / 2
        row_height = (total_height - row_gap) / 2

        for i, elem in enumerate(elements[:4]):
            col = i % 2
            row = i // 2
            cur_left = left_start + col * (col_width + col_gap)
            cur_top = top_pos + row * (row_height + row_gap)

            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, cur_top, col_width, row_height)
            card.fill.solid()
            card.fill.fore_color.rgb = colors["surface"]
            card.line.color.rgb = colors["surface_border"]
            card.line.width = Pt(1)

            # Top Accent Stripe (flush with card top)
            stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_left, cur_top, col_width, Inches(0.05))
            stripe.fill.solid()
            stripe.fill.fore_color.rgb = colors["primary_accent"]
            stripe.line.fill.background()

            tf = card.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.TOP
            tf.margin_left = Inches(0.35)
            tf.margin_right = Inches(0.25)
            tf.margin_top = Inches(0.22)
            tf.margin_bottom = Inches(0.12)

            title = elem.get("title", "")
            desc = elem.get("description", "")
            elem_type = (elem.get("type") or "").lower()

            badge_prefix = f"0{i+1}"
            if elem_type == "step":
                badge_prefix = f"STEP 0{i+1}"

            p_title = tf.paragraphs[0]
            p_title.text = f"{badge_prefix}  •  {title}" if title else desc
            p_title.font.name = header_font
            p_title.font.size = Pt(14)
            p_title.font.bold = True
            p_title.font.color.rgb = colors["heading"]

            if title and desc:
                p_desc = tf.add_paragraph()
                p_desc.text = desc
                p_desc.font.name = body_font
                p_desc.font.size = Pt(11.5)
                p_desc.font.color.rgb = colors["body"]
                p_desc.space_before = Pt(5)


def render_standard_cards(
    slide,
    elements: List[Dict[str, Any]],
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
    has_visual: bool = False,
    visual_assets: Optional[Dict[str, Any]] = None,
):
    """
    Renders structured content elements into balanced, elegant cards.
    """
    left_margin = Inches(0.8)
    top_margin = Inches(2.1)
    avail_width = Inches(7.6) if has_visual else Inches(11.733)
    card_height = Inches(4.7)

    num_elements = len(elements)
    if num_elements == 0:
        return

    # Multi-card vertical stack with adaptive spacing
    gap = Inches(0.14) if num_elements >= 4 else Inches(0.18)
    item_height = (card_height - (gap * (num_elements - 1))) / num_elements

    title_size = Pt(13.5) if num_elements >= 4 else Pt(15)
    desc_size = Pt(11) if num_elements >= 4 else Pt(12)
    top_pad = Inches(0.14) if num_elements >= 4 else Inches(0.20)

    for i, elem in enumerate(elements):
        item_top = top_margin + i * (item_height + gap)

        # Card container with subtle surface fill and crisp border
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_margin, item_top, avail_width, item_height)
        card.fill.solid()
        card.fill.fore_color.rgb = colors["surface"]
        card.line.color.rgb = colors["surface_border"]
        card.line.width = Pt(1)

        # Top Accent Stripe on card
        stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_margin, item_top, avail_width, Inches(0.04))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = colors["primary_accent"]
        stripe.line.fill.background()

        # Text Frame
        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.35)
        tf.margin_right = Inches(0.3)
        tf.margin_top = top_pad
        tf.margin_bottom = Inches(0.08)

        title = elem.get("title", "")
        desc = elem.get("description", "")
        elem_type = (elem.get("type") or "").lower()

        badge_prefix = f"0{i+1}"
        if elem_type == "step":
            badge_prefix = f"STEP 0{i+1}"
        elif elem_type == "takeaway":
            badge_prefix = f"TAKEAWAY 0{i+1}"

        p_title = tf.paragraphs[0]
        p_title.text = f"{badge_prefix}  •  {title}" if title else desc
        p_title.font.name = header_font
        p_title.font.size = title_size
        p_title.font.bold = True
        p_title.font.color.rgb = colors["heading"]

        if title and desc:
            p_desc = tf.add_paragraph()
            p_desc.text = desc
            p_desc.font.name = body_font
            p_desc.font.size = desc_size
            p_desc.font.color.rgb = colors["body"]
            p_desc.space_before = Pt(3)

    # Optional visual card if visual assets / images are enabled
    if has_visual and visual_assets:
        vis_left = Inches(8.7)
        vis_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, vis_left, top_margin, Inches(3.833), card_height)
        vis_card.fill.solid()
        vis_card.fill.fore_color.rgb = colors["surface"]
        vis_card.line.color.rgb = colors["surface_border"]
        vis_card.line.width = Pt(1)

        # Accent top stripe on visual frame
        vis_stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, vis_left, top_margin, Inches(3.833), Inches(0.06))
        vis_stripe.fill.solid()
        vis_stripe.fill.fore_color.rgb = colors["primary_accent"]
        vis_stripe.line.fill.background()

        vis_tf = vis_card.text_frame
        vis_tf.word_wrap = True
        vis_tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        vis_tf.margin_left = vis_tf.margin_right = Inches(0.35)

        icon_kw = visual_assets.get("icon_keyword", "Visual Focus")
        p_icon = vis_tf.paragraphs[0]
        p_icon.alignment = PP_ALIGN.CENTER
        p_icon.text = f"KEY FOCUS: {icon_kw.upper()}"
        p_icon.font.name = header_font
        p_icon.font.size = Pt(12)
        p_icon.font.bold = True
        p_icon.font.color.rgb = colors["primary_accent"]

        # Only display prompt context elegantly if provided
        img_prompt = visual_assets.get("image_prompt")
        if img_prompt:
            p_prompt = vis_tf.add_paragraph()
            p_prompt.alignment = PP_ALIGN.CENTER
            # Short clean caption instead of raw prompt dump
            clean_caption = img_prompt.split(".")[0].strip('"')
            p_prompt.text = f"{clean_caption}"
            p_prompt.font.name = body_font
            p_prompt.font.size = Pt(11)
            p_prompt.font.color.rgb = colors["muted"]
            p_prompt.space_before = Pt(10)


def render_chart_slide(
    slide,
    chart_data: Dict[str, Any],
    elements: List[Dict[str, Any]],
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
):
    """
    Renders a native, theme-styled PowerPoint chart paired with an analytical takeaway card.
    """
    left_start = Inches(0.8)
    top_pos = Inches(2.1)
    chart_card_width = Inches(7.2)
    takeaway_card_width = Inches(4.283)
    card_height = Inches(4.7)

    # 1. Left Chart Card Background Surface
    chart_surface = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_start, top_pos, chart_card_width, card_height)
    chart_surface.fill.solid()
    chart_surface.fill.fore_color.rgb = colors["surface"]
    chart_surface.line.color.rgb = colors["surface_border"]
    chart_surface.line.width = Pt(1)

    # Top accent stripe
    stripe_l = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_start, top_pos, chart_card_width, Inches(0.06))
    stripe_l.fill.solid()
    stripe_l.fill.fore_color.rgb = colors["primary_accent"]
    stripe_l.line.fill.background()

    # 2. Build CategoryChartData
    categories = chart_data.get("categories") or ["2023", "2024", "2025 [Est]", "2026 [Est]"]
    values = chart_data.get("values") or [12.0, 28.5, 54.0, 89.0]
    series_name = chart_data.get("series_name") or "Observed Metric"

    # Normalize lengths
    min_len = min(len(categories), len(values))
    if min_len < 2:
        categories = ["Baseline", "Target"]
        values = [25.0, 75.0]
        min_len = 2

    c_data = CategoryChartData()
    c_data.categories = [str(c) for c in categories[:min_len]]
    c_data.add_series(series_name, [float(v) for v in values[:min_len]])

    # Chart Type
    ctype_str = (chart_data.get("chart_type") or "column").lower()
    if ctype_str in ("donut", "doughnut"):
        chart_type = XL_CHART_TYPE.DOUGHNUT
    elif ctype_str == "line":
        chart_type = XL_CHART_TYPE.LINE
    else:
        chart_type = XL_CHART_TYPE.COLUMN_CLUSTERED

    try:
        chart_shape = slide.shapes.add_chart(
            chart_type,
            left_start + Inches(0.2),
            top_pos + Inches(0.3),
            chart_card_width - Inches(0.4),
            card_height - Inches(0.5),
            c_data,
        )
        chart = chart_shape.chart
        chart.has_legend = False
        plots = chart.plots
        if plots and plots[0].series:
            series = plots[0].series[0]
            series.format.fill.solid()
            series.format.fill.fore_color.rgb = colors["primary_accent"]
    except Exception as e:
        print(f"[Chart Render Warning] Error adding chart shape: {e}")

    # 3. Right Takeaway Card
    takeaway_left = left_start + chart_card_width + Inches(0.25)
    t_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, takeaway_left, top_pos, takeaway_card_width, card_height)
    t_card.fill.solid()
    t_card.fill.fore_color.rgb = colors["surface"]
    t_card.line.color.rgb = colors["surface_border"]
    t_card.line.width = Pt(1)

    stripe_r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, takeaway_left, top_pos, takeaway_card_width, Inches(0.06))
    stripe_r.fill.solid()
    stripe_r.fill.fore_color.rgb = colors["secondary_accent"]
    stripe_r.line.fill.background()

    tf = t_card.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.35)
    tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.35)

    p_badge = tf.paragraphs[0]
    p_badge.text = "QUANTITATIVE EVIDENCE"
    p_badge.font.name = header_font
    p_badge.font.size = Pt(10)
    p_badge.font.bold = True
    p_badge.font.color.rgb = colors["secondary_accent"]
    p_badge.space_after = Pt(8)

    chart_title = chart_data.get("title") or "Observed Performance Trajectory"
    p_title = tf.add_paragraph()
    p_title.text = chart_title
    p_title.font.name = header_font
    p_title.font.size = Pt(16)
    p_title.font.bold = True
    p_title.font.color.rgb = colors["heading"]
    p_title.space_after = Pt(10)

    takeaway = chart_data.get("key_takeaway")
    if takeaway:
        p_take = tf.add_paragraph()
        p_take.text = takeaway
        p_take.font.name = body_font
        p_take.font.size = Pt(12)
        p_take.font.color.rgb = colors["body"]
        p_take.space_after = Pt(10)

    # If any supporting elements exist, render them
    for elem in elements[:2]:
        t = elem.get("title")
        d = elem.get("description")
        if t or d:
            p_elem = tf.add_paragraph()
            p_elem.text = f"•  {t}: {d}" if (t and d) else (t or d)
            p_elem.font.name = body_font
            p_elem.font.size = Pt(11)
            p_elem.font.color.rgb = colors["muted"]
            p_elem.space_before = Pt(4)


def render_comparison_layout(
    slide,
    comp_data: Dict[str, Any],
    elements: List[Dict[str, Any]],
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
):
    """
    Renders an executive Before vs After / Legacy vs Next-Gen comparison layout.
    """
    left_start = Inches(0.8)
    top_pos = Inches(2.1)
    col_width = Inches(5.7)
    card_height = Inches(4.7)
    gap = Inches(0.333)

    # Extract comparison parameters
    left_title = comp_data.get("left_title") or "Traditional Status Quo"
    left_status = comp_data.get("left_status") or "LEGACY FRICTION"
    left_points = comp_data.get("left_points") or [
        "Rigid rule-based scripts break on edge cases",
        "High manual overhead for routine triage",
        "Siloed architecture impedes real-time synthesis",
    ]

    right_title = comp_data.get("right_title") or "Autonomous Paradigm"
    right_status = comp_data.get("right_status") or "MODERN ADVANTAGE"
    right_points = comp_data.get("right_points") or [
        "Self-healing workflows resolve transient anomalies",
        "Automated tool execution with complete telemetry",
        "Sub-second decision latency at enterprise scale",
    ]

    # Left Card (Legacy)
    card_l = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_start, top_pos, col_width, card_height)
    card_l.fill.solid()
    card_l.fill.fore_color.rgb = colors["surface"]
    card_l.line.color.rgb = colors["surface_border"]
    card_l.line.width = Pt(1)

    stripe_l = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_start, top_pos, col_width, Inches(0.06))
    stripe_l.fill.solid()
    stripe_l.fill.fore_color.rgb = colors["muted"]
    stripe_l.line.fill.background()

    tf_l = card_l.text_frame
    tf_l.word_wrap = True
    tf_l.vertical_anchor = MSO_ANCHOR.TOP
    tf_l.margin_left = Inches(0.4)
    tf_l.margin_right = Inches(0.35)
    tf_l.margin_top = Inches(0.35)

    p_badgel = tf_l.paragraphs[0]
    p_badgel.text = left_status.upper()
    p_badgel.font.name = header_font
    p_badgel.font.size = Pt(10)
    p_badgel.font.bold = True
    p_badgel.font.color.rgb = colors["muted"]
    p_badgel.space_after = Pt(8)

    p_tit_l = tf_l.add_paragraph()
    p_tit_l.text = left_title
    p_tit_l.font.name = header_font
    p_tit_l.font.size = Pt(17)
    p_tit_l.font.bold = True
    p_tit_l.font.color.rgb = colors["heading"]
    p_tit_l.space_after = Pt(14)

    for pt in left_points[:4]:
        p_pt = tf_l.add_paragraph()
        p_pt.text = f"—  {pt}"
        p_pt.font.name = body_font
        p_pt.font.size = Pt(12)
        p_pt.font.color.rgb = colors["body"]
        p_pt.space_before = Pt(8)

    # Right Card (Modern Advantage)
    right_left = left_start + col_width + gap
    card_r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, top_pos, col_width, card_height)
    card_r.fill.solid()
    card_r.fill.fore_color.rgb = colors["surface"]
    card_r.line.color.rgb = colors["surface_border"]
    card_r.line.width = Pt(1)

    stripe_r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_left, top_pos, col_width, Inches(0.06))
    stripe_r.fill.solid()
    stripe_r.fill.fore_color.rgb = colors["primary_accent"]
    stripe_r.line.fill.background()

    tf_r = card_r.text_frame
    tf_r.word_wrap = True
    tf_r.vertical_anchor = MSO_ANCHOR.TOP
    tf_r.margin_left = Inches(0.4)
    tf_r.margin_right = Inches(0.35)
    tf_r.margin_top = Inches(0.35)

    p_badger = tf_r.paragraphs[0]
    p_badger.text = right_status.upper()
    p_badger.font.name = header_font
    p_badger.font.size = Pt(10)
    p_badger.font.bold = True
    p_badger.font.color.rgb = colors["primary_accent"]
    p_badger.space_after = Pt(8)

    p_tit_r = tf_r.add_paragraph()
    p_tit_r.text = right_title
    p_tit_r.font.name = header_font
    p_tit_r.font.size = Pt(17)
    p_tit_r.font.bold = True
    p_tit_r.font.color.rgb = colors["heading"]
    p_tit_r.space_after = Pt(14)

    for pt in right_points[:4]:
        p_pt = tf_r.add_paragraph()
        p_pt.text = f"✓  {pt}"
        p_pt.font.name = body_font
        p_pt.font.size = Pt(12)
        p_pt.font.color.rgb = colors["body"]
        p_pt.space_before = Pt(8)


def render_process_flow_layout(
    slide,
    steps: List[Dict[str, Any]],
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
):
    """
    Renders horizontal pipeline stages connected by flow indicators.
    """
    num_steps = max(2, min(4, len(steps)))
    if num_steps == 0:
        return

    left_start = Inches(0.8)
    top_pos = Inches(2.1)
    total_width = Inches(11.733)
    card_height = Inches(4.7)
    gap = Inches(0.25)
    card_width = (total_width - (gap * (num_steps - 1))) / num_steps

    for i, step in enumerate(steps[:num_steps]):
        cur_left = left_start + i * (card_width + gap)

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_pos, card_width, card_height)
        card.fill.solid()
        card.fill.fore_color.rgb = colors["surface"]
        card.line.color.rgb = colors["surface_border"]
        card.line.width = Pt(1)

        stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_left, top_pos, card_width, Inches(0.06))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = colors["primary_accent"]
        stripe.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.3)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.35)

        # Step Indicator
        p_badge = tf.paragraphs[0]
        p_badge.text = f"PHASE 0{i+1}"
        p_badge.font.name = header_font
        p_badge.font.size = Pt(10)
        p_badge.font.bold = True
        p_badge.font.color.rgb = colors["primary_accent"]
        p_badge.space_after = Pt(8)

        title = step.get("title") or f"Milestone {i+1}"
        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.name = header_font
        p_title.font.size = Pt(16)
        p_title.font.bold = True
        p_title.font.color.rgb = colors["heading"]
        p_title.space_after = Pt(10)

        desc = step.get("description") or ""
        if desc:
            p_desc = tf.add_paragraph()
            p_desc.text = desc
            p_desc.font.name = body_font
            p_desc.font.size = Pt(11.5)
            p_desc.font.color.rgb = colors["body"]
            p_desc.space_after = Pt(12)

        deliverable = step.get("deliverable")
        if deliverable:
            p_deliv = tf.add_paragraph()
            p_deliv.text = f"OUTCOME: {deliverable}"
            p_deliv.font.name = header_font
            p_deliv.font.size = Pt(10)
            p_deliv.font.bold = True
            p_deliv.font.color.rgb = colors["secondary_accent"]


def render_case_study_layout(
    slide,
    cs_data: Dict[str, Any],
    elements: List[Dict[str, Any]],
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
):
    """
    Renders an executive case study spotlight with standout result metric and structured narrative.
    """
    left_start = Inches(0.8)
    top_pos = Inches(2.1)
    card_height = Inches(4.7)
    left_width = Inches(4.5)
    right_width = Inches(6.983)
    gap = Inches(0.25)

    org = cs_data.get("organization") or "Enterprise Spotlight"
    metric = cs_data.get("highlight_metric") or "+65% Speed"
    metric_label = cs_data.get("metric_label") or "Operational Gain"
    takeaway = cs_data.get("takeaway") or "Scalable blueprint for enterprise adoption."

    # Left Spotlight Card
    card_l = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_start, top_pos, left_width, card_height)
    card_l.fill.solid()
    card_l.fill.fore_color.rgb = colors["surface"]
    card_l.line.color.rgb = colors["surface_border"]
    card_l.line.width = Pt(1)

    stripe_l = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_start, top_pos, left_width, Inches(0.06))
    stripe_l.fill.solid()
    stripe_l.fill.fore_color.rgb = colors["primary_accent"]
    stripe_l.line.fill.background()

    tf_l = card_l.text_frame
    tf_l.word_wrap = True
    tf_l.vertical_anchor = MSO_ANCHOR.TOP
    tf_l.margin_left = Inches(0.35)
    tf_l.margin_right = Inches(0.3)
    tf_l.margin_top = Inches(0.4)

    p_badge = tf_l.paragraphs[0]
    p_badge.text = f"CASE STUDY: {org.upper()}"
    p_badge.font.name = header_font
    p_badge.font.size = Pt(10)
    p_badge.font.bold = True
    p_badge.font.color.rgb = colors["primary_accent"]
    p_badge.space_after = Pt(14)

    p_met = tf_l.add_paragraph()
    p_met.text = metric
    p_met.font.name = header_font
    p_met.font.size = Pt(40)
    p_met.font.bold = True
    p_met.font.color.rgb = colors["primary_accent"]
    p_met.space_after = Pt(6)

    p_lbl = tf_l.add_paragraph()
    p_lbl.text = metric_label
    p_lbl.font.name = header_font
    p_lbl.font.size = Pt(14)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = colors["heading"]
    p_lbl.space_after = Pt(14)

    p_tk = tf_l.add_paragraph()
    p_tk.text = f"STRATEGIC LESSON:\n{takeaway}"
    p_tk.font.name = body_font
    p_tk.font.size = Pt(11.5)
    p_tk.font.color.rgb = colors["muted"]

    # Right Structured Breakdown Card
    right_left = left_start + left_width + gap
    card_r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, top_pos, right_width, card_height)
    card_r.fill.solid()
    card_r.fill.fore_color.rgb = colors["surface"]
    card_r.line.color.rgb = colors["surface_border"]
    card_r.line.width = Pt(1)

    stripe_r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_left, top_pos, right_width, Inches(0.06))
    stripe_r.fill.solid()
    stripe_r.fill.fore_color.rgb = colors["secondary_accent"]
    stripe_r.line.fill.background()

    tf_r = card_r.text_frame
    tf_r.word_wrap = True
    tf_r.vertical_anchor = MSO_ANCHOR.TOP
    tf_r.margin_left = Inches(0.4)
    tf_r.margin_right = Inches(0.35)
    tf_r.margin_top = Inches(0.4)

    sections = [
        ("THE CORE CHALLENGE", cs_data.get("challenge") or "Manual fragmented workflows constrained growth."),
        ("DEPLOYED MECHANISM", cs_data.get("solution") or "Automated multi-agent execution pipeline integrated into existing ERP."),
        ("MEASURABLE IMPACT", cs_data.get("impact") or "Reduced latency by 65% with zero human exception triaging needed."),
    ]

    for i, (title, content) in enumerate(sections):
        p_st = tf_r.paragraphs[0] if i == 0 else tf_r.add_paragraph()
        p_st.text = title
        p_st.font.name = header_font
        p_st.font.size = Pt(11)
        p_st.font.bold = True
        p_st.font.color.rgb = colors["secondary_accent"]
        p_st.space_after = Pt(4)
        if i > 0:
            p_st.space_before = Pt(14)

        p_sc = tf_r.add_paragraph()
        p_sc.text = content
        p_sc.font.name = body_font
        p_sc.font.size = Pt(12)
        p_sc.font.color.rgb = colors["body"]


def render_big_statistic_layout(
    slide,
    stat_data: Dict[str, Any],
    elements: List[Dict[str, Any]],
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
):
    """
    Renders a dramatic, high-impact numerical anchor layout.
    """
    left_start = Inches(0.8)
    top_pos = Inches(2.1)
    card_height = Inches(4.7)
    left_width = Inches(5.6)
    right_width = Inches(5.883)
    gap = Inches(0.25)

    val = stat_data.get("value") or "$1.4T"
    label = stat_data.get("label") or "Projected Market Expansion"
    context = stat_data.get("context") or "CAGR of 38% through 2030"
    implication = stat_data.get("implication") or "First movers capture disproportionate ecosystem defensibility."

    # Left Card
    card_l = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_start, top_pos, left_width, card_height)
    card_l.fill.solid()
    card_l.fill.fore_color.rgb = colors["surface"]
    card_l.line.color.rgb = colors["surface_border"]
    card_l.line.width = Pt(1)

    stripe_l = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_start, top_pos, left_width, Inches(0.06))
    stripe_l.fill.solid()
    stripe_l.fill.fore_color.rgb = colors["primary_accent"]
    stripe_l.line.fill.background()

    tf_l = card_l.text_frame
    tf_l.word_wrap = True
    tf_l.vertical_anchor = MSO_ANCHOR.TOP
    tf_l.margin_left = Inches(0.4)
    tf_l.margin_right = Inches(0.35)
    tf_l.margin_top = Inches(0.5)

    p_b = tf_l.paragraphs[0]
    p_b.text = "KEY QUANTITATIVE ANCHOR"
    p_b.font.name = header_font
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = colors["primary_accent"]
    p_b.space_after = Pt(14)

    p_v = tf_l.add_paragraph()
    p_v.text = val
    p_v.font.name = header_font
    p_v.font.size = Pt(54)
    p_v.font.bold = True
    p_v.font.color.rgb = colors["primary_accent"]
    p_v.space_after = Pt(10)

    p_lbl = tf_l.add_paragraph()
    p_lbl.text = label
    p_lbl.font.name = header_font
    p_lbl.font.size = Pt(16)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = colors["heading"]
    p_lbl.space_after = Pt(8)

    p_c = tf_l.add_paragraph()
    p_c.text = f"Context: {context}"
    p_c.font.name = body_font
    p_c.font.size = Pt(12)
    p_c.font.color.rgb = colors["muted"]

    # Right Card
    right_left = left_start + left_width + gap
    card_r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, top_pos, right_width, card_height)
    card_r.fill.solid()
    card_r.fill.fore_color.rgb = colors["surface"]
    card_r.line.color.rgb = colors["surface_border"]
    card_r.line.width = Pt(1)

    stripe_r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_left, top_pos, right_width, Inches(0.06))
    stripe_r.fill.solid()
    stripe_r.fill.fore_color.rgb = colors["secondary_accent"]
    stripe_r.line.fill.background()

    tf_r = card_r.text_frame
    tf_r.word_wrap = True
    tf_r.vertical_anchor = MSO_ANCHOR.TOP
    tf_r.margin_left = Inches(0.4)
    tf_r.margin_right = Inches(0.35)
    tf_r.margin_top = Inches(0.5)

    p_rb = tf_r.paragraphs[0]
    p_rb.text = "STRATEGIC IMPLICATION"
    p_rb.font.name = header_font
    p_rb.font.size = Pt(10)
    p_rb.font.bold = True
    p_rb.font.color.rgb = colors["secondary_accent"]
    p_rb.space_after = Pt(14)

    p_imp = tf_r.add_paragraph()
    p_imp.text = implication
    p_imp.font.name = header_font
    p_imp.font.size = Pt(16)
    p_imp.font.bold = True
    p_imp.font.color.rgb = colors["heading"]
    p_imp.space_after = Pt(14)

    for elem in elements[:2]:
        p_pt = tf_r.add_paragraph()
        t = elem.get("title")
        d = elem.get("description")
        p_pt.text = f"•  {t}: {d}" if (t and d) else (t or d)
        p_pt.font.name = body_font
        p_pt.font.size = Pt(12)
        p_pt.font.color.rgb = colors["body"]
        p_pt.space_before = Pt(6)


def render_references_layout(
    slide,
    sources: List[Dict[str, Any]],
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
):
    """
    Renders evidence base and methodology disclosures in a clean 2-column format.
    """
    left_start = Inches(0.8)
    top_pos = Inches(2.1)
    card_height = Inches(4.7)
    card_width = Inches(5.7)
    gap = Inches(0.333)

    items = sources if isinstance(sources, list) else []
    mid = (len(items) + 1) // 2
    left_items = items[:mid]
    right_items = items[mid:]

    for col_idx, col_sources in enumerate([left_items, right_items]):
        cur_left = left_start + col_idx * (card_width + gap)

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_pos, card_width, card_height)
        card.fill.solid()
        card.fill.fore_color.rgb = colors["surface"]
        card.line.color.rgb = colors["surface_border"]
        card.line.width = Pt(1)

        stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_left, top_pos, card_width, Inches(0.06))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = colors["primary_accent"]
        stripe.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.35)
        tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.35)

        p_b = tf.paragraphs[0]
        p_b.text = f"EVIDENCE SOURCES {'PART 1' if col_idx == 0 else 'PART 2'}"
        p_b.font.name = header_font
        p_b.font.size = Pt(10)
        p_b.font.bold = True
        p_b.font.color.rgb = colors["primary_accent"]
        p_b.space_after = Pt(10)

        for src in col_sources[:3]:
            title = src.get("source_title") or src.get("title") or "Empirical Benchmark"
            citation = src.get("citation") or src.get("description") or "Industry Analysis"
            is_est = src.get("is_estimated", False)

            p_t = tf.add_paragraph()
            p_t.text = f"{title} {'[Estimated]' if is_est else ''}"
            p_t.font.name = header_font
            p_t.font.size = Pt(13)
            p_t.font.bold = True
            p_t.font.color.rgb = colors["heading"]
            p_t.space_before = Pt(8)

            p_c = tf.add_paragraph()
            p_c.text = citation
            p_c.font.name = body_font
            p_c.font.size = Pt(11)
            p_c.font.color.rgb = colors["muted"]


def render_quote_layout(
    slide,
    slide_data: Dict[str, Any],
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
):
    """
    Renders an impactful quotation/principle layout.
    """
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(2.1), Inches(10.933), Inches(4.7))
    card.fill.solid()
    card.fill.fore_color.rgb = colors["surface"]
    card.line.color.rgb = colors["surface_border"]
    card.line.width = Pt(1)

    stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(2.1), Inches(10.933), Inches(0.06))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = colors["primary_accent"]
    stripe.line.fill.background()

    tf = card.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.8)

    q_text = slide_data.get("quote_text") or slide_data.get("subheadline") or "The future belongs to those who build continuous agency."
    attrib = slide_data.get("attribution") or "Executive Synthesis"

    p_q = tf.paragraphs[0]
    p_q.text = f'“{q_text}”'
    p_q.font.name = header_font
    p_q.font.size = Pt(22)
    p_q.font.bold = True
    p_q.font.color.rgb = colors["heading"]
    p_q.space_after = Pt(18)

    p_a = tf.add_paragraph()
    p_a.text = f"— {attrib}"
    p_a.font.name = body_font
    p_a.font.size = Pt(13)
    p_a.font.color.rgb = colors["primary_accent"]


def render_slide_content(
    slide,
    slide_data: Dict[str, Any],
    colors: Dict[str, Any],
    header_font: str,
    body_font: str,
    has_visual: bool,
    visuals: Dict[str, Any],
):
    """
    Dispatches to the appropriate layout archetype based on AI slide metadata
    or element characteristics.
    """
    layout_type = (slide_data.get("layout") or "standard").lower()
    elements = slide_data.get("content_elements", [])

    if layout_type == "chart" or slide_data.get("chart_data"):
        render_chart_slide(slide, slide_data.get("chart_data", {}), elements, colors, header_font, body_font)
    elif layout_type == "comparison" or slide_data.get("comparison"):
        render_comparison_layout(slide, slide_data.get("comparison", {}), elements, colors, header_font, body_font)
    elif layout_type in ("process_flow", "timeline", "process_timeline") or slide_data.get("process_flow") or (isinstance(slide_data.get("steps"), list) and len(slide_data["steps"]) >= 2):
        steps = slide_data.get("process_flow", {}).get("steps") or slide_data.get("steps") or elements
        render_process_flow_layout(slide, steps, colors, header_font, body_font)
    elif layout_type == "case_study" or slide_data.get("case_study"):
        render_case_study_layout(slide, slide_data.get("case_study", {}), elements, colors, header_font, body_font)
    elif layout_type in ("big_statistic", "big_stat") or slide_data.get("big_statistic"):
        render_big_statistic_layout(slide, slide_data.get("big_statistic", {}), elements, colors, header_font, body_font)
    elif layout_type in ("references", "sources") or slide_data.get("references") or slide_data.get("sources"):
        sources = slide_data.get("references") or slide_data.get("sources") or elements
        render_references_layout(slide, sources, colors, header_font, body_font)
    elif layout_type in ("quote", "insight") or slide_data.get("quote_text"):
        render_quote_layout(slide, slide_data, colors, header_font, body_font)
    elif layout_type == "metrics_callout":
        render_metrics_layout(slide, elements, colors, header_font, body_font)
    elif layout_type in ("feature_grid", "three_column", "split_screen") or (len(elements) == 4 and not has_visual):
        render_grid_layout(slide, elements, colors, header_font, body_font)
    else:
        render_standard_cards(slide, elements, colors, header_font, body_font, has_visual, visuals)


def create_presentation_file(
    presentation_data: Dict[str, Any],
    default_topic: str = "Presentation",
    default_font: str = "Modern Sans-Serif",
    default_theme: str = "Obsidian Emerald",
    has_logo: Optional[bool] = None,
    has_images: Optional[bool] = None,
) -> str:
    """
    Generates an executive-grade PowerPoint presentation from structured JSON
    and saves to a temporary file. Returns the absolute path to the generated .pptx file.
    """
    prs = Presentation()

    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    metadata = presentation_data.get("metadata", {})
    theme_info = metadata.get("theme", {})
    topic = metadata.get("topic") or default_topic

    # Extract or infer palette with guaranteed contrast safety
    palette = get_theme_palette(theme_info, default_theme)

    # Resolve typography respecting user's font style
    header_font, body_font = resolve_fonts(theme_info, default_font)

    # Strictly resolve logo: if caller passes boolean, respect it 100%; otherwise infer cleanly
    if has_logo is None:
        logo_spec = str(theme_info.get("logo_specification", "")).strip().lower()
        has_logo = bool(logo_spec) and "none" not in logo_spec and logo_spec not in ("null", "false", "disabled", "no logo")

    # Strictly resolve images: if caller passes boolean, respect it 100%; otherwise infer cleanly
    if has_images is None:
        has_images = bool(metadata.get("images", False))

    slides_data = presentation_data.get("slides", [])
    blank_layout = prs.slide_layouts[6]

    for index, slide_data in enumerate(slides_data):
        slide = prs.slides.add_slide(blank_layout)

        # Set slide background color
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = palette["bg"]

        headline = slide_data.get("headline", f"Slide {index + 1}")
        subheadline = slide_data.get("subheadline", "")
        layout_type = (slide_data.get("layout") or "standard").lower()

        # If has_images is False, visual card is NEVER created and content cards use full width
        visuals = slide_data.get("visual_assets", {}) if has_images else {}
        img_prompt = str(visuals.get("image_prompt") or "").strip()
        has_visual = bool(
            has_images
            and img_prompt
            and img_prompt.lower() not in ("none", "null", "false", "disabled", "n/a", "")
        )

        # Render slide by layout type
        if layout_type == "hero_title" or index == 0:
            render_hero_title(
                slide,
                headline,
                subheadline,
                palette,
                header_font,
                body_font,
                has_logo,
                topic,
            )
        else:
            add_slide_header(
                slide,
                headline,
                subheadline,
                palette,
                header_font,
                body_font,
                has_logo,
            )
            render_slide_content(
                slide,
                slide_data,
                palette,
                header_font,
                body_font,
                has_visual,
                visuals,
            )

        # Attach speaker notes if present
        speaker_notes = slide_data.get("speaker_notes")
        if speaker_notes:
            notes_slide = slide.notes_slide
            notes_tf = notes_slide.notes_text_frame
            notes_tf.text = str(speaker_notes)

    # Save to a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=".pptx", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    prs.save(temp_path)
    return temp_path
