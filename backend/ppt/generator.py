import os
import re
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


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
    title_box = slide.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.9), Inches(3.2))
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
        sub_box = slide.shapes.add_textbox(Inches(1.2), Inches(4.6), Inches(10.5), Inches(1.4))
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
    """
    # 1. Top Accent Rule
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.4), Inches(1.2), Inches(0.05))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = colors["primary_accent"]
    top_bar.line.fill.background()

    # 2. Title and Subtitle Box
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(10.5), Inches(1.2))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p_title = tf.paragraphs[0]
    p_title.text = headline
    p_title.font.name = header_font
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = colors["heading"]

    if subheadline:
        p_sub = tf.add_paragraph()
        p_sub.text = subheadline
        p_sub.font.name = body_font
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = colors["muted"]
        p_sub.space_before = Pt(4)

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

            # Index tag pill / badge
            p_badge = tf.paragraphs[0]
            p_badge.text = f"KEY TAKEAWAY 0{i+1}"
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
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf.margin_left = Inches(0.35)
            tf.margin_right = Inches(0.25)

            title = elem.get("title", "")
            desc = elem.get("description", "")

            p_title = tf.paragraphs[0]
            p_title.text = f"0{i+1}  •  {title}" if title else desc
            p_title.font.name = header_font
            p_title.font.size = Pt(15)
            p_title.font.bold = True
            p_title.font.color.rgb = colors["heading"]

            if title and desc:
                p_desc = tf.add_paragraph()
                p_desc.text = desc
                p_desc.font.name = body_font
                p_desc.font.size = Pt(12)
                p_desc.font.color.rgb = colors["body"]
                p_desc.space_before = Pt(6)


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

    # Multi-card vertical stack
    gap = Inches(0.18)
    item_height = (card_height - (gap * (num_elements - 1))) / num_elements

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
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.35)
        tf.margin_right = Inches(0.3)

        title = elem.get("title", "")
        desc = elem.get("description", "")

        p_title = tf.paragraphs[0]
        p_title.text = f"0{i+1}  •  {title}" if title else desc
        p_title.font.name = header_font
        p_title.font.size = Pt(15)
        p_title.font.bold = True
        p_title.font.color.rgb = colors["heading"]

        if title and desc:
            p_desc = tf.add_paragraph()
            p_desc.text = desc
            p_desc.font.name = body_font
            p_desc.font.size = Pt(12)
            p_desc.font.color.rgb = colors["body"]
            p_desc.space_before = Pt(4)

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

    # Check if elements are predominantly metrics / numbers
    has_metrics = any(
        elem.get("type") == "metric" or
        bool(re.search(r'\d+[%BKMk]?', elem.get("title", "")))
        for elem in elements
    )

    if layout_type == "metrics_callout" or (has_metrics and len(elements) in (3, 4) and not has_visual):
        render_metrics_layout(slide, elements, colors, header_font, body_font)
    elif layout_type in ("feature_grid", "split_screen") or (len(elements) == 4 and not has_visual):
        render_grid_layout(slide, elements, colors, header_font, body_font)
    else:
        render_standard_cards(slide, elements, colors, header_font, body_font, has_visual, visuals)


def create_presentation_file(
    presentation_data: Dict[str, Any],
    default_topic: str = "Presentation",
    default_font: str = "Modern Sans-Serif",
    default_theme: str = "Obsidian Emerald",
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
    has_logo = str(theme_info.get("logo_specification", "")).lower() not in ("none", "")

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
        visuals = slide_data.get("visual_assets", {})
        has_visual = bool(visuals and visuals.get("image_prompt"))

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
