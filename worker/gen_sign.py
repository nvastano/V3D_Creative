#!/usr/bin/env python3
"""
Generate a custom funny-sign .3mf (BambuStudio format).

The sign design (from the FIXED example file) is TWO portrait panels
printed side by side and then snapped together:
  - RIGHT PANEL  (sign_x = 0 … +74.75 mm) → front face
  - LEFT PANEL   (sign_x = -74.75 … 0 mm) → back face (mirrored)

Each panel face is portrait: ≈40 mm wide (sign_y) × ≈74.75 mm tall (sign_x).
Text runs HORIZONTALLY across the 40 mm width, stacked down the 75 mm height.

Text vertex mapping from glyph 2-D space to sign 3-D space:
  glyph_x  →  sign_Y  (horizontal across the panel face)
  glyph_y  →  sign_X  (vertical down/up the panel face)
  depth    →  sign_Z  (perpendicular to face, extrudes away from face)
"""

import sys
sys.path.insert(0, '/usr/local/lib/python3.11/dist-packages')

import os, math, uuid, zipfile, argparse
import numpy as np
import freetype
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import triangulate, unary_union
from shapely.validation import make_valid
from shapely.affinity import translate, scale as shp_scale

# ── Config ────────────────────────────────────────────────────────────────────
FONT_PATH   = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
TEMPLATE_3MF = '/root/.claude/uploads/78464379-f874-4a11-8b94-049de62ec7ca/de8973d9-Funny_work_signs_Template.3mf'

# Sign geometry (from the template mesh)
SIGN_X_HALF  = 74.748   # sign_x goes ±74.748 mm
SIGN_Y_HALF  = 19.994   # sign_y goes ±19.994 mm
SIGN_FRONT_Z = 1.5      # z of the front face (text protrudes UP from here)
TEXT_THICK   = 0.8      # mm – emboss depth

# Each portrait panel: right half (x=0…+74.748), left half (x=-74.748…0)
PANEL_HALF_X = SIGN_X_HALF          # 74.748 mm panel height
PANEL_HALF_Y = SIGN_Y_HALF          # 19.994 mm → ±19.994 gives 40 mm width

# Usable text area on each panel (with margins)
TEXT_MAX_W   = 33.0    # mm – max text width  (in sign_y direction)
TEXT_MAX_H   = 58.0    # mm – max stacked text height (in sign_x direction)
LINE_GAP     = 2.0     # mm – gap between lines
BEZIER_STEPS = 10      # curve sampling steps


# ── 1. Freetype outline extraction ────────────────────────────────────────────

class _OC:
    def __init__(self):
        self.contours = []
        self._cur = []
        self._pos = np.zeros(2)

    @staticmethod
    def _v(pt):
        # Freetype gives 26.6 fixed-point; divide by 64
        return np.array([pt.x / 64.0, pt.y / 64.0], dtype=float)

    def _app(self, pt):
        self._cur.append(pt)
        self._pos = self._cur[-1].copy()

    def move_to(self, pt, _=None):
        if self._cur:
            self.contours.append(self._cur)
        self._cur = [self._v(pt)]
        self._pos = self._cur[-1].copy()

    def line_to(self, pt, _=None):
        self._app(self._v(pt))

    def conic_to(self, ctrl, end, _=None):
        p0, p1, p2 = self._pos, self._v(ctrl), self._v(end)
        for i in range(1, BEZIER_STEPS + 1):
            t = i / BEZIER_STEPS
            self._app((1-t)**2*p0 + 2*(1-t)*t*p1 + t**2*p2)

    def cubic_to(self, c1, c2, end, _=None):
        p0 = self._pos
        p1, p2, p3 = self._v(c1), self._v(c2), self._v(end)
        for i in range(1, BEZIER_STEPS + 1):
            t = i / BEZIER_STEPS
            self._app((1-t)**3*p0 + 3*(1-t)**2*t*p1
                      + 3*(1-t)*t**2*p2 + t**3*p3)

    def flush(self):
        if self._cur:
            self.contours.append(self._cur)
            self._cur = []


def _signed_area(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        a += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
    return a / 2.0


def build_glyph_polygon(contours_raw, scale):
    """
    Convert raw freetype contour points into a Shapely Polygon.
    TrueType convention: outer contour = CW (area<0), hole = CCW (area>0).
    """
    contours = []
    for raw in contours_raw:
        pts = [(p[0] * scale, p[1] * scale) for p in raw]
        if len(pts) >= 3:
            contours.append(pts)
    if not contours:
        return None

    outer, holes = [], []
    for c in contours:
        (holes if _signed_area(c) > 0 else outer).append(c)

    # Fallback: if all same sign, treat largest as outer
    if not outer and holes:
        areas = [abs(_signed_area(c)) for c in holes]
        idx = areas.index(max(areas))
        outer = [holes.pop(idx)]
    if not outer:
        return None

    polys = []
    for oc in outer:
        outer_shp = Polygon(oc)
        if not outer_shp.is_valid:
            outer_shp = make_valid(outer_shp)
        my_holes = [h for h in holes
                    if outer_shp.contains(Polygon(h).representative_point())]
        try:
            p = Polygon(oc, my_holes)
            polys.append(make_valid(p) if not p.is_valid else p)
        except Exception:
            polys.append(outer_shp)

    combined = unary_union(polys) if len(polys) > 1 else polys[0]
    return make_valid(combined) if not combined.is_valid else combined


def line_to_polygons(text_line, font_path, target_width_mm):
    """
    Render one line of text and scale it so total advance ≤ target_width_mm.
    Returns (list of (poly, x_offset_mm), actual_width_mm, actual_height_mm).
    Glyph space: x = text direction (→), y = ascender direction (↑).
    """
    face = freetype.Face(font_path)
    face.set_char_size(1000 * 64)

    ascender_pts = face.size.ascender / 64.0

    # Measure total advance at reference size (target_height=20mm)
    REF_H = 20.0
    ref_scale = REF_H / ascender_pts

    cursor = 0.0
    glyph_data = []
    for ch in text_line:
        idx = face.get_char_index(ord(ch))
        face.load_glyph(idx, freetype.FT_LOAD_DEFAULT | freetype.FT_LOAD_NO_BITMAP)
        adv = face.glyph.advance.x / 64.0 * ref_scale
        oc = _OC()
        face.glyph.outline.decompose(oc, move_to=oc.move_to, line_to=oc.line_to,
                                     conic_to=oc.conic_to, cubic_to=oc.cubic_to)
        oc.flush()
        glyph_data.append((idx, oc.contours, cursor, adv))
        cursor += adv

    total_w_ref = cursor
    if total_w_ref <= 0:
        return [], 0.0, 0.0

    # Scale to fit target_width_mm (width-constrained scaling)
    width_scale = target_width_mm / total_w_ref
    # Also constrain by a max height (TEXT_MAX_W per line height)
    height_scale = (TEXT_MAX_W * 0.80) / (REF_H)  # don't let font be taller than ~80% of usable
    final_scale_ratio = min(width_scale, height_scale)  # relative to REF_H

    target_h = REF_H * final_scale_ratio
    scale = target_h / ascender_pts  # mm per freetype-pixel

    # Re-generate polygons at final scale
    results = []
    cursor_mm = 0.0
    for idx, contours, cursor_ref, adv_ref in glyph_data:
        adv_mm = adv_ref * final_scale_ratio
        if contours:
            poly = build_glyph_polygon(contours, scale)
            if poly is not None and not poly.is_empty:
                results.append((poly, cursor_mm))
        cursor_mm += adv_mm

    total_w_mm = cursor_mm

    # Measure actual glyph height
    all_y = []
    for poly, _ in results:
        plist = list(poly.geoms) if isinstance(poly, MultiPolygon) else [poly]
        for p in plist:
            all_y.extend([p.bounds[1], p.bounds[3]])
    glyph_h = (max(all_y) - min(all_y)) if all_y else target_h

    return results, total_w_mm, glyph_h


# ── 2. Build text mesh for one panel ─────────────────────────────────────────

def _poly_tris(poly):
    """Delaunay triangulate + filter by centroid inside polygon."""
    all_tris = triangulate(poly)
    return [t for t in all_tris
            if poly.contains(Point(t.centroid.x, t.centroid.y))]


def panel_text_mesh(lines, font_path,
                    panel_center_x, z_face, mirror_y=False):
    """
    Build triangle list for text on one panel.

    lines        : list of strings (text lines)
    panel_center_x : center of panel in sign_x (e.g. +37 for front, -37 for back)
    z_face       : z of the sign face (e.g. 1.5)
    mirror_y     : if True, flip sign_y (for the back panel)

    Coordinate mapping:
      glyph_x → sign_Y  (horizontal on panel face)
      glyph_y → sign_X  (vertical on panel face)
      depth   → sign_Z  (extrudes from z_face)
    """
    z_top = z_face + TEXT_THICK   # text protrudes above face

    # Build each line's polygons (centered on the panel)
    rendered_lines = []
    for line in lines:
        glyphs, w, h = line_to_polygons(line, font_path, TEXT_MAX_W)
        if glyphs:
            rendered_lines.append((glyphs, w, h))

    if not rendered_lines:
        return []

    # Stack lines vertically: compute total block height
    total_block_h = sum(h for _, _, h in rendered_lines)
    total_block_h += LINE_GAP * (len(rendered_lines) - 1)

    # Start from panel_center_x + half block height (top of block)
    current_x = panel_center_x + total_block_h / 2.0

    triangles = []

    for (glyphs, w, h) in rendered_lines:
        # Center each line horizontally (in sign_y = glyph_x direction)
        x_shift = -w / 2.0   # shift so text is centered at sign_y = 0

        # Find glyph vertical center to align baseline-to-midline centering
        all_y_vals = []
        for poly, _ in glyphs:
            pl = list(poly.geoms) if isinstance(poly, MultiPolygon) else [poly]
            for p in pl:
                all_y_vals.extend([p.bounds[1], p.bounds[3]])
        line_y_center = (min(all_y_vals) + max(all_y_vals)) / 2.0 if all_y_vals else 0.0

        # In sign_X (panel height), position this line so its center is at current_x
        y_shift = -line_y_center   # glyph_y → sign_X: shift to center around 0
        # Then offset so the LINE CENTER is at current_x (in sign_X space)
        sign_x_offset = current_x   # glyph_y + y_shift + sign_x_offset → sign_X

        for (poly, gx_off) in glyphs:
            # Shift the polygon in glyph space
            shifted = translate(poly, xoff=x_shift + gx_off, yoff=y_shift)
            if mirror_y:
                # Mirror glyph_x (which → sign_y) for the back panel
                shifted = shp_scale(shifted, xfact=-1, yfact=1, origin=(0, 0))

            plist = list(shifted.geoms) if isinstance(shifted, MultiPolygon) else [shifted]
            for p in plist:
                tris = _poly_tris(p)
                for tri in tris:
                    coords = list(tri.exterior.coords)[:3]

                    # Glyph (cx, cy) → sign (sign_x, sign_y)
                    # glyph_x=cx → sign_Y;  glyph_y=cy → sign_X offset by sign_x_offset
                    def sv(cx, cy, z):
                        sx = sign_x_offset + cy    # glyph_y → sign_X
                        sy = cx                    # glyph_x → sign_Y
                        return np.array([sx, sy, z])

                    # Top face (outward normal in +z)
                    top = [sv(cx, cy, z_top) for cx, cy in coords]
                    triangles.append(np.array(top))
                    # Bottom face (inward normal)
                    bot = [sv(cx, cy, z_face) for cx, cy in coords]
                    triangles.append(np.array(list(reversed(bot))))

                    # Side walls
                    for i in range(len(coords)):
                        ax, ay = coords[i]
                        bx, by = coords[(i+1) % len(coords)]
                        A = sv(ax, ay, z_face)
                        B = sv(bx, by, z_face)
                        C = sv(bx, by, z_top)
                        D = sv(ax, ay, z_top)
                        triangles.append(np.array([A, B, C]))
                        triangles.append(np.array([A, C, D]))

                # Side walls for interior rings (holes)
                for interior in p.interiors:
                    hcoords = list(interior.coords)
                    for i in range(len(hcoords) - 1):
                        ax, ay = hcoords[i]
                        bx, by = hcoords[i+1]
                        A = sv(ax, ay, z_face)
                        B = sv(bx, by, z_face)
                        C = sv(bx, by, z_top)
                        D = sv(ax, ay, z_top)
                        # Interior ring walls face inward (reversed)
                        triangles.append(np.array([A, C, B]))
                        triangles.append(np.array([A, D, C]))

        # Move down for next line (sign_X decreases going "down" panel)
        current_x -= h + LINE_GAP

    return triangles


# ── 3. Load sign base mesh from template ─────────────────────────────────────

def load_sign_triangles(template_3mf):
    import xml.etree.ElementTree as ET
    with zipfile.ZipFile(template_3mf) as zf:
        with zf.open('3D/Objects/object_11.model') as f:
            tree = ET.parse(f)
    ns = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    root = tree.getroot()
    verts = [(float(v.attrib['x']), float(v.attrib['y']), float(v.attrib['z']))
             for v in root.findall('.//m:vertex', ns)]
    return [np.array([verts[int(t.attrib['v1'])],
                      verts[int(t.attrib['v2'])],
                      verts[int(t.attrib['v3'])]],
                     dtype=float)
            for t in root.findall('.//m:triangle', ns)]


# ── 4. Write 3MF ──────────────────────────────────────────────────────────────

_XMLH = '<?xml version="1.0" encoding="UTF-8"?>\n'


def _obj_xml(obj_id, obj_uuid, tris):
    verts, v_map, faces = [], {}, []
    for tri in tris:
        fids = []
        for v in tri:
            k = tuple(f'{x:.5f}' for x in v)
            if k not in v_map:
                v_map[k] = len(verts)
                verts.append(v)
            fids.append(v_map[k])
        faces.append(fids)

    lines = [
        f'  <object id="{obj_id}" p:UUID="{obj_uuid}" type="model">',
        '   <mesh>',
        '    <vertices>',
        *[f'     <vertex x="{v[0]:.5f}" y="{v[1]:.5f}" z="{v[2]:.5f}"/>' for v in verts],
        '    </vertices>',
        '    <triangles>',
        *[f'     <triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}"/>' for f in faces],
        '    </triangles>',
        '   </mesh>',
        '  </object>',
    ]
    return '\n'.join(lines)


def make_object_model(sign_tris, front_tris, back_tris):
    ns   = 'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"'
    p_ns = 'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06"'
    bns  = 'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021"'
    hdr  = f'<model unit="millimeter" xml:lang="en-US" {ns} {p_ns} {bns} requiredextensions="p">'
    parts = [
        _XMLH + hdr,
        ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
        ' <resources>',
        _obj_xml(1, str(uuid.uuid4()), sign_tris),
        _obj_xml(2, str(uuid.uuid4()), front_tris),
        _obj_xml(3, str(uuid.uuid4()), back_tris),
        ' </resources>',
        '</model>',
    ]
    return '\n'.join(parts)


def make_3dmodel(obj_file, asm_id=10):
    ns   = 'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"'
    p_ns = 'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06"'
    bns  = 'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021"'
    asm_uuid   = str(uuid.uuid4())
    build_uuid = str(uuid.uuid4())
    item_uuid  = str(uuid.uuid4())
    c_uuids    = [str(uuid.uuid4()) for _ in range(3)]
    ident = '1 0 0 0 1 0 0 0 1 0 0 0'
    # Place sign centred on a 256×256 mm plate; tz=2.5 puts sign bottom at z=0
    place = '1 0 0 0 1 0 0 0 1 128.0 128.0 2.5'
    return (
        f'{_XMLH}'
        f'<model unit="millimeter" xml:lang="en-US" {ns} {bns} {p_ns} requiredextensions="p">\n'
        f' <metadata name="Application">BambuStudio-02.04.00.70</metadata>\n'
        f' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        f' <metadata name="Title">Funny work sign – custom</metadata>\n'
        f' <resources>\n'
        f'  <object id="{asm_id}" p:UUID="{asm_uuid}" type="model">\n'
        f'   <components>\n'
        f'    <component p:path="/3D/Objects/{obj_file}" objectid="1" p:UUID="{c_uuids[0]}" transform="{ident}"/>\n'
        f'    <component p:path="/3D/Objects/{obj_file}" objectid="2" p:UUID="{c_uuids[1]}" transform="{ident}"/>\n'
        f'    <component p:path="/3D/Objects/{obj_file}" objectid="3" p:UUID="{c_uuids[2]}" transform="{ident}"/>\n'
        f'   </components>\n'
        f'  </object>\n'
        f' </resources>\n'
        f' <build p:UUID="{build_uuid}">\n'
        f'  <item objectid="{asm_id}" p:UUID="{item_uuid}" transform="{place}" printable="1"/>\n'
        f' </build>\n'
        f'</model>'
    )


def make_settings(asm_id, text_display):
    ident = '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'
    safe  = text_display.replace('"', '&quot;')
    return (
        f'{_XMLH}'
        f'<config>\n'
        f'  <object id="{asm_id}">\n'
        f'    <metadata key="name" value="Funny Sign"/>\n'
        f'    <metadata key="extruder" value="1"/>\n'
        f'    <part id="1" subtype="normal_part">\n'
        f'      <metadata key="name" value="Sign"/>\n'
        f'      <metadata key="matrix" value="{ident}"/>\n'
        f'      <metadata key="extruder" value="1"/>\n'
        f'    </part>\n'
        f'    <part id="2" subtype="normal_part">\n'
        f'      <metadata key="name" value="text_front"/>\n'
        f'      <metadata key="matrix" value="{ident}"/>\n'
        f'      <metadata key="extruder" value="2"/>\n'
        f'      <text_info text="{safe}" font_name="DejaVu Sans Bold" font_size="10"'
        f' thickness="0.8" bold="1" italic="0" surface_text="1"/>\n'
        f'    </part>\n'
        f'    <part id="3" subtype="normal_part">\n'
        f'      <metadata key="name" value="text_back"/>\n'
        f'      <metadata key="matrix" value="{ident}"/>\n'
        f'      <metadata key="extruder" value="2"/>\n'
        f'      <text_info text="{safe}" font_name="DejaVu Sans Bold" font_size="10"'
        f' thickness="0.8" bold="1" italic="0" surface_text="1"/>\n'
        f'    </part>\n'
        f'  </object>\n'
        f'</config>'
    )


CT_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
    '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
    '  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
    '  <Default Extension="config" ContentType="text/xml"/>\n'
    '</Types>'
)

RELS_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
    '  <Relationship Target="/3D/3dmodel.model" Id="rel-1"\n'
    '    Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
    '</Relationships>'
)


def d3_rels(obj_file):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        f'  <Relationship Target="/3D/Objects/{obj_file}" Id="rel-1"\n'
        '    Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
        '</Relationships>'
    )


# ── 5. Main ───────────────────────────────────────────────────────────────────

def generate_sign_3mf(text_lines, output_path, template_path=TEMPLATE_3MF):
    """
    text_lines : list of strings, one per line on the sign
                 e.g. ["Shoutout to", "Cody!"]
    """
    print(f"[1/5] Loading sign base …")
    sign_tris = load_sign_triangles(template_path)
    print(f"      {len(sign_tris)} triangles")

    # Front panel: right half, normal orientation
    front_center_x = PANEL_HALF_X / 2.0   # +37.37 mm
    print(f"[2/5] Generating front-panel text …")
    front_tris = panel_text_mesh(text_lines, FONT_PATH,
                                 panel_center_x=front_center_x,
                                 z_face=SIGN_FRONT_Z,
                                 mirror_y=False)
    print(f"      {len(front_tris)} triangles")

    # Back panel: left half, mirrored in sign_y
    back_center_x = -PANEL_HALF_X / 2.0   # -37.37 mm
    print(f"[3/5] Generating back-panel text …")
    back_tris  = panel_text_mesh(text_lines, FONT_PATH,
                                 panel_center_x=back_center_x,
                                 z_face=SIGN_FRONT_Z,
                                 mirror_y=True)
    print(f"      {len(back_tris)} triangles")

    if not front_tris:
        raise RuntimeError("No text triangles generated.")

    print(f"[4/5] Building .3mf XML …")
    OBJ_FILE = 'sign_custom.model'
    ASM_ID   = 10

    print(f"[5/5] Writing {output_path} …")
    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml',           CT_XML)
        zf.writestr('_rels/.rels',                   RELS_XML)
        zf.writestr('3D/3dmodel.model',              make_3dmodel(OBJ_FILE, ASM_ID))
        zf.writestr(f'3D/Objects/{OBJ_FILE}',        make_object_model(sign_tris, front_tris, back_tris))
        zf.writestr('3D/_rels/3dmodel.model.rels',   d3_rels(OBJ_FILE))
        zf.writestr('Metadata/model_settings.config',
                    make_settings(ASM_ID, ' / '.join(text_lines)))
    print("Done →", output_path)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('lines', nargs='+', help='One or more text lines for the sign')
    ap.add_argument('-o', '--output', default='custom_sign.3mf')
    args = ap.parse_args()
    generate_sign_3mf(args.lines, args.output)
