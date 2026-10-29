#!/usr/bin/env python3
"""
generate_efg_deck.py
Generates the pristine, fully-calibrated 8-slide Grand Finale Pitch Deck for:
EMERGE FOR GOOD INNOVATION CHALLENGE - TOP 50 FINALE
Pondicherry University (October 28, 2026)

Team Code: EFG-090
Team Name: IDLEBIN
Institution: Easwari Engineering College, Chennai
"""

import os
import zipfile
import shutil
import xml.etree.ElementTree as ET

TEMPLATE_PATH = "/Users/shreeprasandhk/shree_projects/idlebin/Pitch template Emerge for good OCT 28TH.pptx"
OUTPUT_PATH = "/Users/shreeprasandhk/shree_projects/idlebin/Pitch_IdleBin_EFG_Final.pptx"
BUILD_DIR = "/tmp/pptx_build_efg"

# Slide canvas dimensions in EMU: 16:9 Widescreen (20.0" x 11.25")
WIDTH_EMU = 18288000
HEIGHT_EMU = 10287000

def make_shape_xml(shape_id, name, x, y, cx, cy, fill_hex=None, line_hex=None, line_w=12700, paragraphs=None, anchor="t", tIns=72000, lIns=216000, bIns=72000, rIns=216000):
    """
    Constructs an OpenXML <p:sp> element with precise coordinates, background fill, border,
    and text formatted in Times New Roman with justified/centered/left alignment and paragraph spacing.
    """
    name_escaped = name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    
    fill_xml = ""
    if fill_hex:
        fill_xml = f'<a:solidFill><a:srgbClr val="{fill_hex}"/></a:solidFill>'
    else:
        fill_xml = '<a:noFill/>'
        
    line_xml = ""
    if line_hex:
        line_xml = f'<a:ln w="{line_w}"><a:solidFill><a:srgbClr val="{line_hex}"/></a:solidFill></a:ln>'
    else:
        line_xml = '<a:ln><a:noFill/></a:ln>'

    p_xmls = []
    if paragraphs:
        for p in paragraphs:
            align = p.get('align', 'l') # 'l', 'just', 'ctr', 'r'
            ln_spc = p.get('ln_spc', None) # hundredths of a point
            spc_aft = p.get('spc_aft', None)
            spc_bef = p.get('spc_bef', None)
            runs = p.get('runs', [])
            
            pPr_children = []
            if ln_spc:
                pPr_children.append(f'<a:lnSpc><a:spcPts val="{ln_spc}"/></a:lnSpc>')
            if spc_bef:
                pPr_children.append(f'<a:spcBef><a:spcPts val="{spc_bef}"/></a:spcBef>')
            if spc_aft:
                pPr_children.append(f'<a:spcAft><a:spcPts val="{spc_aft}"/></a:spcAft>')
            
            r_xmls = []
            for r in runs:
                text = r.get('text', '')
                sz = r.get('sz', 1800) # hundredths of pt (18pt = 1800)
                b = 'true' if r.get('b', False) else 'false'
                i = 'true' if r.get('i', False) else 'false'
                color = r.get('color', '1A1A1A')
                
                # Escape XML characters
                text_escaped = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                
                r_xml = f'''<a:r>
                    <a:rPr lang="en-US" sz="{sz}" b="{b}" i="{i}">
                        <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
                        <a:latin typeface="Times New Roman"/>
                        <a:ea typeface="Times New Roman"/>
                        <a:cs typeface="Times New Roman"/>
                        <a:sym typeface="Times New Roman"/>
                    </a:rPr>
                    <a:t>{text_escaped}</a:t>
                </a:r>'''
                r_xmls.append(r_xml)
            
            pPr_str = f'<a:pPr algn="{align}">{"".join(pPr_children)}</a:pPr>' if (pPr_children or align != 'l') else '<a:pPr algn="l"/>'
            p_elem = f'''<a:p>
                {pPr_str}
                {''.join(r_xmls)}
            </a:p>'''
            p_xmls.append(p_elem)
    else:
        p_xmls.append('<a:p><a:pPr algn="l"/></a:p>')

    sp_xml = f'''<p:sp>
        <p:nvSpPr>
            <p:cNvPr name="{name_escaped}" id="{shape_id}"/>
            <p:cNvSpPr txBox="true"/>
            <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
            <a:xfrm rot="0">
                <a:off x="{x}" y="{y}"/>
                <a:ext cx="{cx}" cy="{cy}"/>
            </a:xfrm>
            <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
            {fill_xml}
            {line_xml}
        </p:spPr>
        <p:txBody>
            <a:bodyPr anchor="{anchor}" rtlCol="false" tIns="{tIns}" lIns="{lIns}" bIns="{bIns}" rIns="{rIns}">
                <a:spAutoFit/>
            </a:bodyPr>
            <a:lstStyle/>
            {''.join(p_xmls)}
        </p:txBody>
    </p:sp>'''
    return sp_xml

def make_header_shapes(slide_title, rubric_subtitle, slide_num, total_slides=8):
    """Generates the unified top header and bottom footer for content slides."""
    shapes = []
    
    # 1. Slide Title (Times New Roman, 32pt, Bold, Charcoal #1A202C)
    shapes.append(make_shape_xml(
        shape_id=201, name="Slide Title",
        x=1028700, y=450000, cx=13500000, cy=850000,
        fill_hex=None, line_hex=None,
        paragraphs=[{
            'align': 'l', 'ln_spc': 3600,
            'runs': [{'text': slide_title, 'sz': 3200, 'b': True, 'color': '1A202C'}]
        }]
    ))
    
    # 2. Rubric Badge (Times New Roman, 15pt, Bold, Deep Slate/Teal #2B6CB0)
    shapes.append(make_shape_xml(
        shape_id=202, name="Rubric Badge",
        x=1028700, y=1250000, cx=13500000, cy=550000,
        fill_hex=None, line_hex=None,
        paragraphs=[{
            'align': 'l', 'ln_spc': 2000,
            'runs': [{'text': rubric_subtitle, 'sz': 1500, 'b': True, 'color': '2B6CB0'}]
        }]
    ))
    
    # 3. Top-Right Event Badge
    shapes.append(make_shape_xml(
        shape_id=203, name="Event Badge",
        x=14700000, y=450000, cx=2559300, cy=1200000,
        fill_hex="EDF2F7", line_hex="CBD5E0", line_w=12700,
        paragraphs=[
            {'align': 'ctr', 'ln_spc': 2000, 'runs': [{'text': 'EMERGE FOR GOOD', 'sz': 1400, 'b': True, 'color': '2D3748'}]},
            {'align': 'ctr', 'ln_spc': 1800, 'runs': [{'text': 'TOP 50 FINALE | OCT 28', 'sz': 1200, 'b': False, 'color': '4A5568'}]},
            {'align': 'ctr', 'ln_spc': 1800, 'runs': [{'text': 'TEAM: EFG-090', 'sz': 1300, 'b': True, 'color': '1B4D3E'}]}
        ]
    ))
    
    # 4. Subtle Separator Line
    shapes.append(f'''<p:sp>
        <p:nvSpPr><p:cNvPr name="Line 204" id="204"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
            <a:xfrm><a:off x="1028700" y="1780000"/><a:ext cx="16230600" cy="0"/></a:xfrm>
            <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
            <a:ln w="12700"><a:solidFill><a:srgbClr val="CBD5E0"/></a:solidFill></a:ln>
        </p:spPr>
    </p:sp>''')
    
    # 5. Footer (Slide Number & Confidential Tag)
    shapes.append(make_shape_xml(
        shape_id=205, name="Footer Info",
        x=1028700, y=9600000, cx=16230600, cy=580000,
        fill_hex=None, line_hex=None,
        paragraphs=[{
            'align': 'l', 'ln_spc': 2000,
            'runs': [
                {'text': 'IDLEBIN | Grand Finale Innovation Challenge, Pondicherry University  |  Swachh Bharat Mission (SBM-U 2.0) Aligned', 'sz': 1300, 'b': False, 'color': '718096'},
                {'text': f'                Slide {slide_num} of {total_slides}', 'sz': 1300, 'b': True, 'color': '4A5568'}
            ]
        }]
    ))
    
    return shapes

def build_slide1():
    """Slide 1: Cover Slide with Official Banner & Team Identification."""
    shapes = []
    
    # Official Emerge for Good Banner (Freeform 9 with image1.jpeg)
    shapes.append('''<p:sp>
        <p:nvSpPr><p:cNvPr name="Freeform 9" id="9"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
            <a:xfrm flipH="false" flipV="false" rot="0">
                <a:off x="5297028" y="250000"/>
                <a:ext cx="7693943" cy="1955605"/>
            </a:xfrm>
            <a:custGeom>
                <a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/>
                <a:rect l="0" t="0" r="0" b="0"/>
                <a:pathLst><a:path w="814" h="207"><a:moveTo><a:pt x="0" y="0"/></a:moveTo><a:lnTo><a:pt x="814" y="0"/></a:lnTo><a:lnTo><a:pt x="814" y="207"/></a:lnTo><a:lnTo><a:pt x="0" y="207"/></a:lnTo><a:close/></a:path></a:pathLst>
            </a:custGeom>
            <a:blipFill rotWithShape="true">
                <a:blip r:embed="rId2"/>
                <a:srcRect l="0" t="0" r="0" b="0"/>
                <a:stretch><a:fillRect/></a:stretch>
            </a:blipFill>
        </p:spPr>
    </p:sp>''')
    
    # Title & Subtitle Card (Top Center below banner)
    shapes.append(make_shape_xml(
        shape_id=10, name="Title Box",
        x=1028700, y=2200000, cx=16230600, cy=1550000,
        fill_hex=None, line_hex=None,
        paragraphs=[
            {'align': 'ctr', 'ln_spc': 4400, 'spc_aft': 600, 'runs': [{'text': 'IDLEBIN', 'sz': 4400, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'ctr', 'ln_spc': 2600, 'spc_aft': 400, 'runs': [{'text': 'Zero-Electricity Foot-Compacting Community Dustbin', 'sz': 2200, 'i': True, 'color': '2D3748'}]},
            {'align': 'ctr', 'ln_spc': 2000, 'runs': [{'text': 'Track: Waste Reduction, Segregation & Circular Economy | Pondicherry University Grand Finale', 'sz': 1500, 'color': '4A5568'}]}
        ]
    ))
    
    # Left Card: Team Credentials
    shapes.append(make_shape_xml(
        shape_id=11, name="Team Credentials Card",
        x=1028700, y=3800000, cx=7900000, cy=5650000,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=288000, bIns=216000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2800, 'spc_aft': 1000, 'runs': [{'text': 'TEAM IDENTIFICATION & CREDENTIALS', 'sz': 2100, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'l', 'ln_spc': 2400, 'spc_aft': 600, 'runs': [
                {'text': 'Team Code: ', 'sz': 1800, 'b': True, 'color': '2D3748'},
                {'text': 'EFG-090  |  ', 'sz': 1800, 'b': True, 'color': '2B6CB0'},
                {'text': 'Team Name: ', 'sz': 1800, 'b': True, 'color': '2D3748'},
                {'text': 'IDLEBIN', 'sz': 1800, 'b': True, 'color': '2B6CB0'}
            ]},
            {'align': 'l', 'ln_spc': 2400, 'spc_aft': 600, 'runs': [
                {'text': 'Institution: ', 'sz': 1800, 'b': True, 'color': '2D3748'},
                {'text': 'Easwari Engineering College, Chennai', 'sz': 1800, 'b': False, 'color': '1A202C'}
            ]},
            {'align': 'l', 'ln_spc': 2200, 'spc_aft': 1000, 'runs': [
                {'text': 'Affiliation: ', 'sz': 1700, 'b': True, 'color': '2D3748'},
                {'text': 'Autonomous | Affiliated to Anna University', 'sz': 1700, 'b': False, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2400, 'spc_aft': 600, 'runs': [{'text': 'Team Members (5 Student Engineers):', 'sz': 1850, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'l', 'ln_spc': 2200, 'spc_aft': 400, 'runs': [
                {'text': '1. Shreeprasandh K ', 'sz': 1700, 'b': True, 'color': '1A202C'},
                {'text': '(Team Leader | Dept. of IT)', 'sz': 1600, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2200, 'spc_aft': 400, 'runs': [
                {'text': '2. Sivaram Venugopal ', 'sz': 1700, 'b': True, 'color': '1A202C'},
                {'text': '(Member | Mechanical Linkages & CAD)', 'sz': 1600, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2200, 'spc_aft': 400, 'runs': [
                {'text': '3. Shrihari Mohanraj ', 'sz': 1700, 'b': True, 'color': '1A202C'},
                {'text': '(Member | Fabrication & Testing)', 'sz': 1600, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2200, 'spc_aft': 400, 'runs': [
                {'text': '4. Dhanudharan K S ', 'sz': 1700, 'b': True, 'color': '1A202C'},
                {'text': '(Member | Surveys & Data Validation)', 'sz': 1600, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2200, 'spc_aft': 1000, 'runs': [
                {'text': '5. Mithun Thangaraj ', 'sz': 1700, 'b': True, 'color': '1A202C'},
                {'text': '(Member | Cost & SBM Compliance)', 'sz': 1600, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2400, 'runs': [
                {'text': 'Lead Contact: ', 'sz': 1750, 'b': True, 'color': '2D3748'},
                {'text': 'shreeprasandh@gmail.com', 'sz': 1750, 'color': '2B6CB0'}
            ]}
        ]
    ))
    
    # Right Card: The Core Elevator Pitch & Vision
    shapes.append(make_shape_xml(
        shape_id=12, name="Elevator Pitch Card",
        x=9350000, y=3800000, cx=7909300, cy=5650000,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=200000, lIns=288000, bIns=200000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2800, 'spc_aft': 900, 'runs': [{'text': 'THE ELEVATOR PITCH', 'sz': 2100, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'just', 'ln_spc': 2600, 'spc_aft': 1000, 'runs': [
                {'text': '"IdleBin is a zero-electricity, foot-operated community dustbin that mechanically crushes plastic bottles and packets flat with 600 Newtons of human foot force, holding 4 times more waste so garbage never overflows onto Indian streets."', 'sz': 1850, 'b': True, 'i': True, 'color': '1A202C'}
            ]},
            {'align': 'l', 'ln_spc': 2400, 'spc_aft': 700, 'runs': [{'text': 'Three Core Foundational Pillars:', 'sz': 1800, 'b': True, 'color': '2D3748'}]},
            {'align': 'just', 'ln_spc': 2350, 'spc_aft': 700, 'runs': [
                {'text': '1. Zero Electricity Dependency: ', 'sz': 1700, 'b': True, 'color': '1B4D3E'},
                {'text': 'Operates 100% mechanically using pure class-1 leverage. No motors, solar panels, or sensors to fail under Indian road dust or monsoons.', 'sz': 1700, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2350, 'spc_aft': 700, 'runs': [
                {'text': '2. 4X Volume Compaction: ', 'sz': 1700, 'b': True, 'color': '1B4D3E'},
                {'text': 'Eliminates trapped air in plastic bottles immediately at the point of disposal, quadrupling bin capacity and stopping street overflow.', 'sz': 1700, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2350, 'spc_aft': 0, 'runs': [
                {'text': '3. Civic Hygiene & Worker Dignity: ', 'sz': 1700, 'b': True, 'color': '1B4D3E'},
                {'text': 'Hands-free pedal removes the disgust factor of touching dirty bins, while dense lift-out bags eliminate manual street shoveling.', 'sz': 1700, 'color': '2D3748'}
            ]}
        ]
    ))
    
    return shapes

def build_slide2():
    """Slide 2: The Core Problem — Why Indian Street Bins Fail (Rubric 1: 10 Marks)."""
    shapes = make_header_shapes(
        slide_title="THE PROBLEM: WHY INDIAN STREET BINS FAIL",
        rubric_subtitle="RUBRIC 1: CAUSAL ROOT ANALYSIS & GROUND PHENOMENOLOGY [10 MARKS]",
        slide_num=2
    )
    
    card_w = 5000000
    card_h = 7500000
    y_top = 1950000
    
    # Column 1: The 80% Empty Air Trap
    shapes.append(make_shape_xml(
        shape_id=21, name="Problem Col 1",
        x=1028700, y=y_top, cx=card_w, cy=card_h,
        fill_hex="FFF5F5", line_hex="FEB2B2", line_w=15000,
        tIns=252000, lIns=288000, bIns=252000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2800, 'spc_aft': 1600, 'runs': [{'text': '1. THE 80% EMPTY AIR TRAP', 'sz': 2200, 'b': True, 'color': '9B2C2C'}]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 1400, 'runs': [
                {'text': 'Street dustbins in Indian commercial areas fill up within ', 'sz': 1950, 'color': '2D3748'},
                {'text': 'just 2 to 3 hours ', 'sz': 1950, 'b': True, 'color': '9B2C2C'},
                {'text': 'after placement. Crucially, this is not because of heavy solid waste.', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 1400, 'runs': [
                {'text': 'Over 80% of volume inside street bins is trapped empty air ', 'sz': 1950, 'b': True, 'color': '1A202C'},
                {'text': 'inside uncrushed PET mineral water bottles, disposable tea cups, and puffed snack sachets.', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 0, 'runs': [
                {'text': 'A standard 60-liter municipal bin appears completely full after ', 'sz': 1950, 'color': '2D3748'},
                {'text': 'only 20 to 25 empty bottles. ', 'sz': 1950, 'b': True, 'color': '9B2C2C'},
                {'text': 'Municipal trucks end up spending fuel hauling empty trapped air across cities.', 'sz': 1950, 'color': '2D3748'}
            ]}
        ]
    ))
    
    # Column 2: The 10-Foot Toss Barrier
    shapes.append(make_shape_xml(
        shape_id=22, name="Problem Col 2",
        x=6643700, y=y_top, cx=card_w, cy=card_h,
        fill_hex="FFF5F5", line_hex="FEB2B2", line_w=15000,
        tIns=252000, lIns=288000, bIns=252000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2800, 'spc_aft': 1600, 'runs': [{'text': '2. THE 10-FOOT TOSS BARRIER', 'sz': 2200, 'b': True, 'color': '9B2C2C'}]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 1400, 'runs': [
                {'text': 'Traditional community bins quickly turn rusted, stained, and foul-smelling. Citizens experience severe ', 'sz': 1950, 'color': '2D3748'},
                {'text': 'civic disgust ', 'sz': 1950, 'b': True, 'color': '9B2C2C'},
                {'text': 'and refuse to touch bin lids with bare hands.', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 1400, 'runs': [
                {'text': 'As a result, people hurl waste bags from 5 to 10 feet away. ', 'sz': 1950, 'b': True, 'color': '1A202C'},
                {'text': 'Bags burst against the road curb, spilling wet kitchen refuse onto sidewalks.', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 0, 'runs': [
                {'text': 'This behavioral bottleneck sparks permanent ', 'sz': 1950, 'color': '2D3748'},
                {'text': '"Garbage Vulnerable Points" (GVPs) ', 'sz': 1950, 'b': True, 'color': '9B2C2C'},
                {'text': 'around existing bins, defeating municipal sanitation efforts.', 'sz': 1950, 'color': '2D3748'}
            ]}
        ]
    ))
    
    # Column 3: Animal Vectors & Choked Naalis
    shapes.append(make_shape_xml(
        shape_id=23, name="Problem Col 3",
        x=12258700, y=y_top, cx=card_w, cy=card_h,
        fill_hex="FFF5F5", line_hex="FEB2B2", line_w=15000,
        tIns=252000, lIns=288000, bIns=252000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2800, 'spc_aft': 1600, 'runs': [{'text': '3. ANIMAL VECTORS & CHOKING', 'sz': 2200, 'b': True, 'color': '9B2C2C'}]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 1400, 'runs': [
                {'text': 'The moment a bin overflows, stray cattle and street dogs rip open plastic bags to reach food scraps, ', 'sz': 1950, 'color': '2D3748'},
                {'text': 'scattering waste across 50 meters ', 'sz': 1950, 'b': True, 'color': '9B2C2C'},
                {'text': 'of public roadways.', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 1400, 'runs': [
                {'text': 'This creates severe disease vectors (flies, cholera, dengue) ', 'sz': 1950, 'b': True, 'color': '1A202C'},
                {'text': 'and severe occupational health hazards for conservancy staff.', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 0, 'runs': [
                {'text': 'During rains, uncompacted plastic is washed into ', 'sz': 1950, 'color': '2D3748'},
                {'text': 'open municipal storm drains (naalis), ', 'sz': 1950, 'b': True, 'color': '9B2C2C'},
                {'text': 'causing chronic drainage chokes and monsoon urban flooding.', 'sz': 1950, 'color': '2D3748'}
            ]}
        ]
    ))
    
    return shapes

def build_slide3():
    """Slide 3: Existing Solutions & Three Competitors (Rubric 2: 10 Marks)."""
    shapes = make_header_shapes(
        slide_title="EXISTING SOLUTIONS & COMPETITIVE BENCHMARK",
        rubric_subtitle="RUBRIC 2: THREE MARKET COMPETITORS, USER DISCOVERY & UNIQUENESS [10 MARKS]",
        slide_num=3
    )
    
    # Top 3 Competitor Cards
    card_w = 5000000
    card_h = 4200000
    y_top = 1950000
    
    # Competitor 1: Open Municipal Dumpsters
    shapes.append(make_shape_xml(
        shape_id=31, name="Comp 1",
        x=1028700, y=y_top, cx=card_w, cy=card_h,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=252000, bIns=216000, rIns=252000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2700, 'spc_aft': 600, 'runs': [{'text': 'COMPETITOR 1: OPEN DUMPSTERS', 'sz': 2050, 'b': True, 'color': '2D3748'}]},
            {'align': 'l', 'ln_spc': 2200, 'spc_aft': 600, 'runs': [{'text': 'Category: Standard Municipal Bins', 'sz': 1650, 'i': True, 'color': '718096'}]},
            {'align': 'l', 'ln_spc': 2400, 'spc_aft': 1000, 'runs': [{'text': 'Cost: Rs. 3,000 – Rs. 4,500', 'sz': 1850, 'b': True, 'color': '2B6CB0'}]},
            {'align': 'just', 'ln_spc': 2500, 'spc_aft': 1000, 'runs': [
                {'text': '• Pros: ', 'sz': 1750, 'b': True, 'color': '2F855A'},
                {'text': 'Low upfront cost, robust steel/plastic body.', 'sz': 1750, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2500, 'spc_aft': 0, 'runs': [
                {'text': '• Cons: ', 'sz': 1750, 'b': True, 'color': 'C53030'},
                {'text': 'Zero volume compaction; overflows in 2 hours; easily ransacked by stray cattle and dogs; creates roadside black spots.', 'sz': 1750, 'color': '2D3748'}
            ]}
        ]
    ))
    
    # Competitor 2: Solar Smart Compactor Bins
    shapes.append(make_shape_xml(
        shape_id=32, name="Comp 2",
        x=6643700, y=y_top, cx=card_w, cy=card_h,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=252000, bIns=216000, rIns=252000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2700, 'spc_aft': 600, 'runs': [{'text': 'COMPETITOR 2: SOLAR SMART BINS', 'sz': 2050, 'b': True, 'color': '2D3748'}]},
            {'align': 'l', 'ln_spc': 2200, 'spc_aft': 600, 'runs': [{'text': 'Category: Bigbelly / Ecube Labs', 'sz': 1650, 'i': True, 'color': '718096'}]},
            {'align': 'l', 'ln_spc': 2400, 'spc_aft': 1000, 'runs': [{'text': 'Cost: Rs. 3,50,000+ per unit', 'sz': 1850, 'b': True, 'color': 'C53030'}]},
            {'align': 'just', 'ln_spc': 2500, 'spc_aft': 1000, 'runs': [
                {'text': '• Pros: ', 'sz': 1750, 'b': True, 'color': '2F855A'},
                {'text': 'Motorized compaction, fill-level telemetry.', 'sz': 1750, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2500, 'spc_aft': 0, 'runs': [
                {'text': '• Cons: ', 'sz': 1750, 'b': True, 'color': 'C53030'},
                {'text': 'Prohibitive cost for Indian municipalities; ultrasonic sensors cake in road grime; motors and lithium batteries fail in summer heat.', 'sz': 1750, 'color': '2D3748'}
            ]}
        ]
    ))
    
    # Competitor 3: Reverse Vending Machines (RVMs)
    shapes.append(make_shape_xml(
        shape_id=33, name="Comp 3",
        x=12258700, y=y_top, cx=card_w, cy=card_h,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=252000, bIns=216000, rIns=252000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2700, 'spc_aft': 600, 'runs': [{'text': 'COMPETITOR 3: REVERSE VENDORS', 'sz': 2050, 'b': True, 'color': '2D3748'}]},
            {'align': 'l', 'ln_spc': 2200, 'spc_aft': 600, 'runs': [{'text': 'Category: Biocrux / Zeleno RVMs', 'sz': 1650, 'i': True, 'color': '718096'}]},
            {'align': 'l', 'ln_spc': 2400, 'spc_aft': 1000, 'runs': [{'text': 'Cost: Rs. 2,00,000 – Rs. 5,00,000', 'sz': 1850, 'b': True, 'color': 'C53030'}]},
            {'align': 'just', 'ln_spc': 2500, 'spc_aft': 1000, 'runs': [
                {'text': '• Pros: ', 'sz': 1750, 'b': True, 'color': '2F855A'},
                {'text': 'Shreds clean PET bottles, rewards users.', 'sz': 1750, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2500, 'spc_aft': 0, 'runs': [
                {'text': '• Cons: ', 'sz': 1750, 'b': True, 'color': 'C53030'},
                {'text': 'Restricted to indoor air-conditioned malls; high continuous grid power requirement; rejects crushed, dented, or unlabeled bottles.', 'sz': 1750, 'color': '2D3748'}
            ]}
        ]
    ))
    
    # Bottom Card: Ground Truth Customer Discovery & IdleBin Uniqueness
    shapes.append(make_shape_xml(
        shape_id=34, name="Discovery & Uniqueness",
        x=1028700, y=6400000, cx=16230600, cy=3050000,
        fill_hex="EDF2F7", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=288000, bIns=216000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2800, 'spc_aft': 1200, 'runs': [{'text': 'GROUND TRUTH CUSTOMER DISCOVERY & IDLEBIN UNIQUENESS', 'sz': 2200, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'just', 'ln_spc': 2600, 'spc_aft': 1200, 'runs': [
                {'text': '• Field Interviews Conducted: ', 'sz': 1850, 'b': True, 'color': '2D3748'},
                {'text': 'We interviewed local municipal sanitation workers (Safai Karamcharis), tea stall vendors, and residents in Chennai and Puducherry. Workers confirmed that shoveling scattered street garbage consumes 70% of their daily time; lifting compacted, clean bags saves hours and prevents glass punctures.', 'sz': 1850, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2600, 'spc_aft': 0, 'runs': [
                {'text': '• Why IdleBin is Completely Unique: ', 'sz': 1850, 'b': True, 'color': '1B4D3E'},
                {'text': 'IdleBin is the only 100% mechanical, zero-power compacting bin engineered specifically for Indian street conditions. At Rs. 680 build cost, it achieves 4x plastic volume reduction using human footstep energy alone, with zero electronics, zero maintenance complexity, and total animal resistance.', 'sz': 1850, 'color': '2D3748'}
            ]}
        ]
    ))
    
    return shapes

def build_slide4():
    """Slide 4: Our Solution — Mechanical Innovation (Rubric 3: 10 Marks)."""
    shapes = make_header_shapes(
        slide_title="OUR SOLUTION: IDLEBIN MECHANICAL INNOVATION",
        rubric_subtitle="RUBRIC 3: ZERO-ELECTRICITY FOOT-COMPACTION ARCHITECTURE [10 MARKS]",
        slide_num=4
    )
    
    # Left Card: 5-Step Mechanical Flow
    shapes.append(make_shape_xml(
        shape_id=41, name="Mechanical Flow Card",
        x=1028700, y=1950000, cx=8600000, cy=7500000,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=288000, bIns=216000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 3000, 'spc_aft': 1600, 'runs': [{'text': 'THE 5-STEP MECHANICAL COMPACTION CYCLE', 'sz': 2200, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 1100, 'runs': [
                {'text': '1. Touchless Foot Pedal: ', 'sz': 1900, 'b': True, 'color': '2B6CB0'},
                {'text': 'The user steps on a base-level foot pedal. This motion unlatches the top lid automatically, ensuring zero hand contact and eliminating the disgust barrier.', 'sz': 1900, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 1100, 'runs': [
                {'text': '2. Class-1 Lever Force Transfer: ', 'sz': 1900, 'b': True, 'color': '2B6CB0'},
                {'text': 'A vertical 1/2-inch mild steel pushrod transmits user body weight (~40 kg) directly to an overhead lever arm with a 1.8x mechanical force advantage.', 'sz': 1900, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 1100, 'runs': [
                {'text': '3. 600N Downward Compaction: ', 'sz': 1900, 'b': True, 'color': '2B6CB0'},
                {'text': 'A perforated 8mm circular platen drives downward like a piston, crushing PET bottles and snack wrappers flat under 600+ Newtons of force.', 'sz': 1900, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 1100, 'runs': [
                {'text': '4. One-Way Anti-Bounce Retention: ', 'sz': 1900, 'b': True, 'color': '2B6CB0'},
                {'text': 'Downward-angled internal perimeter baffles allow bottles to pass downward freely but lock them down when the plate lifts, preventing plastic spring-back.', 'sz': 1900, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 0, 'runs': [
                {'text': '5. Dual Spring Recoil & Reset: ', 'sz': 1900, 'b': True, 'color': '2B6CB0'},
                {'text': 'When the user lifts their foot, heavy-duty helical tension springs pull the plate back to resting position in under 1.5 seconds, ready for the next user.', 'sz': 1900, 'color': '2D3748'}
            ]}
        ]
    ))
    
    # Right Card: Practical Design Guardrails
    shapes.append(make_shape_xml(
        shape_id=42, name="Design Guardrails Card",
        x=9900000, y=1950000, cx=7359300, cy=7500000,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=288000, bIns=216000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 3000, 'spc_aft': 1800, 'runs': [{'text': 'CRITICAL ENGINEERING GUARDRAILS', 'sz': 2200, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 1800, 'runs': [
                {'text': '• Strictly For Blue (Dry) Recyclable Bins: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': 'Under Swachh Bharat pairing rules (Green = Wet Food, Blue = Dry Packaging), IdleBin is deployed exclusively for Blue Bins. Wet waste is dense food scraps; it is uncrushed dry plastic that causes 90% of street overflow.', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 1800, 'runs': [
                {'text': '• Accidental Liquid Drainage & Odor Bio-Filter: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': 'If tea or soft drink residue is accidentally thrown inside, perforated drainage holes allow liquid to pass into a sealed false-bottom tray containing activated coconut charcoal and dry sawdust, neutralizing odor naturally.', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 0, 'runs': [
                {'text': '• Animal-Lock Baffle: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': 'The resting overhead platen acts as a physical ceiling. Stray cows and dogs cannot reach inside or drag out trash bags, keeping public sidewalks completely clean.', 'sz': 1950, 'color': '2D3748'}
            ]}
        ]
    ))
    
    return shapes

def build_slide5():
    """Slide 5: Engineering Anatomy & Technical Specifications."""
    shapes = make_header_shapes(
        slide_title="ENGINEERING ANATOMY & TECHNICAL SPECIFICATIONS",
        rubric_subtitle="PHYSICS CALCULATIONS, BIOMECHANICAL LEVERAGE & BILL OF MATERIALS",
        slide_num=5
    )
    
    card_w = 7900000
    card_h = 7500000
    y_top = 1950000
    
    # Left Card: Physics & Parameters
    shapes.append(make_shape_xml(
        shape_id=51, name="Physics Specs",
        x=1028700, y=y_top, cx=card_w, cy=card_h,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=288000, bIns=216000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 3000, 'spc_aft': 1600, 'runs': [{'text': 'BIOMECHANICAL PHYSICS & SPECIFICATIONS', 'sz': 2300, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 900, 'runs': [
                {'text': '• Mechanical Advantage (MA): ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': '1 : 1.8 Force Amplification (Effort Arm 27 cm / Load Arm 15 cm)', 'sz': 1950, 'color': '2B6CB0'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 900, 'runs': [
                {'text': '• Human Foot Input Force: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': '~350 N (Natural 35–40 kg bodyweight step)', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 900, 'runs': [
                {'text': '• Downward Compaction Force: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': '~630 N platen force (Sufficient to crush 3 PET bottles simultaneously)', 'sz': 1950, 'b': True, 'color': '1B4D3E'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 900, 'runs': [
                {'text': '• Volume Compaction Ratio: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': '3.5:1 to 4:1 Volume Reduction (75% volume saved)', 'sz': 1950, 'color': '2B6CB0'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 900, 'runs': [
                {'text': '• Compaction Cycle Time: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': '< 1.5 seconds per complete compression stroke', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 900, 'runs': [
                {'text': '• Power Consumption: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': '0.00 Watts (100% mechanical leverage)', 'sz': 1950, 'b': True, 'color': '1B4D3E'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 900, 'runs': [
                {'text': '• Operating Temperature: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': '-10°C to +60°C (Weatherproof, UV-stabilized HDPE drum)', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 0, 'runs': [
                {'text': '• Operating Lifespan / MTBF: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': '> 5 Years (Only springs & pivot bolts require periodic check)', 'sz': 1950, 'color': '2D3748'}
            ]}
        ]
    ))
    
    # Right Card: Bill of Materials
    shapes.append(make_shape_xml(
        shape_id=52, name="BOM Table Card",
        x=9350000, y=y_top, cx=card_w, cy=card_h,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=288000, bIns=216000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 3000, 'spc_aft': 1600, 'runs': [{'text': 'PROTOTYPE BILL OF MATERIALS (BOM)', 'sz': 2300, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'l', 'ln_spc': 2550, 'spc_aft': 950, 'runs': [
                {'text': '1. HDPE Outer Bin (25L–30L): ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': 'Rs. 250 (Durable waste drum)', 'sz': 1950, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2550, 'spc_aft': 950, 'runs': [
                {'text': '2. Compactor Platen (8mm Perforated): ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': 'Rs. 100 (Acrylic/Wood disk)', 'sz': 1950, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2550, 'spc_aft': 950, 'runs': [
                {'text': '3. Linkage Pushrod (1/2" Steel/PVC): ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': 'Rs. 120 (Vertical force rod)', 'sz': 1950, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2550, 'spc_aft': 950, 'runs': [
                {'text': '4. Foot Pedal Lever (Mild Steel Bar): ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': 'Rs. 80 (Pedal base arm)', 'sz': 1950, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2550, 'spc_aft': 950, 'runs': [
                {'text': '5. Dual Helical Return Springs: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': 'Rs. 50 (Instant plate recoil)', 'sz': 1950, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2550, 'spc_aft': 950, 'runs': [
                {'text': '6. Pivot Fasteners & Hinges (M6/M8): ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': 'Rs. 40 (Galvanized joints)', 'sz': 1950, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2550, 'spc_aft': 1300, 'runs': [
                {'text': '7. Activated Coconut Charcoal Tray: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': 'Rs. 40 (Natural odor filter)', 'sz': 1950, 'color': '4A5568'}
            ]},
            {'align': 'l', 'ln_spc': 2800, 'spc_aft': 1100, 'runs': [
                {'text': 'TOTAL PROTOTYPE FABRICATION COST: ', 'sz': 2100, 'b': True, 'color': '1B4D3E'},
                {'text': 'Rs. 680 (~$8.50 USD)', 'sz': 2100, 'b': True, 'color': '2B6CB0'}
            ]},
            {'align': 'just', 'ln_spc': 2450, 'spc_aft': 0, 'runs': [
                {'text': 'At batch production (1,000 units), sheet metal stamping and bulk sourcing reduce unit cost below ', 'sz': 1800, 'color': '2D3748'},
                {'text': 'Rs. 600 per bin.', 'sz': 1800, 'b': True, 'color': '1B4D3E'}
            ]}
        ]
    ))
    
    return shapes

def build_slide6():
    """Slide 6: Cost Comparison & Ground Impact (Rubric 3: 10 Marks)."""
    shapes = make_header_shapes(
        slide_title="UNIT ECONOMICS & SBM-U 2.0 GROUND IMPACT",
        rubric_subtitle="RUBRIC 3: COST JUSTIFICATION & MEASURABLE SWACHH BHARAT METRICS [10 MARKS]",
        slide_num=6
    )
    
    card_w = 7900000
    card_h = 7500000
    y_top = 1950000
    
    # Left Card: The 450:1 Municipal Cost Advantage
    shapes.append(make_shape_xml(
        shape_id=61, name="Economics Card",
        x=1028700, y=y_top, cx=card_w, cy=card_h,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=288000, bIns=216000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 3000, 'spc_aft': 1600, 'runs': [{'text': 'THE 450 : 1 MUNICIPAL COST ADVANTAGE', 'sz': 2200, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'just', 'ln_spc': 2600, 'spc_aft': 1200, 'runs': [
                {'text': '• Imported Smart Solar Bin Cost: ', 'sz': 1950, 'b': True, 'color': 'C53030'},
                {'text': 'Rs. 3,50,000+ per unit (exorbitant capital burden for Indian municipalities).', 'sz': 1950, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2600, 'spc_aft': 1600, 'runs': [
                {'text': '• IdleBin Unit Production Cost: ', 'sz': 1950, 'b': True, 'color': '1B4D3E'},
                {'text': 'Rs. 650 to Rs. 850 in production batches.', 'sz': 1950, 'b': True, 'color': '1B4D3E'}
            ]},
            {'align': 'just', 'ln_spc': 2700, 'spc_aft': 1600, 'runs': [
                {'text': 'The Transformational Municipal Ratio: ', 'sz': 1950, 'b': True, 'color': '2B6CB0'},
                {'text': 'For the price of just ONE imported solar smart bin (Rs. 3.5 Lakhs), a municipal corporation or rural Gram Panchayat can deploy ', 'sz': 1900, 'color': '2D3748'},
                {'text': '450+ IDLEBINS, ', 'sz': 1950, 'b': True, 'color': '1B4D3E'},
                {'text': 'fully blanketing an entire town, university campus, or temple corridor.', 'sz': 1900, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2650, 'spc_aft': 0, 'runs': [
                {'text': '• Zero Recurring Maintenance: ', 'sz': 1950, 'b': True, 'color': '2D3748'},
                {'text': 'Zero electricity bills, zero cloud SIM subscription costs, zero sensor cleaning downtime. 100% serviceable by any local blacksmith or village mechanic.', 'sz': 1900, 'color': '2D3748'}
            ]}
        ]
    ))
    
    # Right Card: Measurable SBM-U 2.0 Impact
    shapes.append(make_shape_xml(
        shape_id=62, name="Impact Card",
        x=9350000, y=y_top, cx=card_w, cy=card_h,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=288000, bIns=216000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 3000, 'spc_aft': 1600, 'runs': [{'text': 'MEASURABLE GROUND IMPACT (SBM-U 2.0)', 'sz': 2200, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'just', 'ln_spc': 2600, 'spc_aft': 1300, 'runs': [
                {'text': '1. Permanent Elimination of GVPs: ', 'sz': 1900, 'b': True, 'color': '2B6CB0'},
                {'text': 'Eliminating Garbage Vulnerable Points is a mandatory Swachh Bharat KPI. Preventing bin overflow stops the initial dump accumulation that creates black spots.', 'sz': 1900, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2600, 'spc_aft': 1300, 'runs': [
                {'text': '2. 50% Waste Logistics Fuel Savings: ', 'sz': 1900, 'b': True, 'color': '2B6CB0'},
                {'text': 'Because waste density is multiplied 4x, municipal auto-tippers and tractors need 50% fewer daily collection runs per ward, directly saving thousands of liters of diesel.', 'sz': 1900, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2600, 'spc_aft': 1300, 'runs': [
                {'text': '3. Worker Dignity & Health: ', 'sz': 1900, 'b': True, 'color': '2B6CB0'},
                {'text': 'Sanitation staff no longer have to shovel rotten, scattered waste from the road using hand trowels. Compacted waste is lifted out in dense, clean bags, preventing occupational injuries.', 'sz': 1900, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2600, 'spc_aft': 0, 'runs': [
                {'text': '4. 100% Pan-India Rural Feasibility: ', 'sz': 1900, 'b': True, 'color': '2B6CB0'},
                {'text': 'Operates identically in remote coastal fishing hamlets, hilly pilgrimage sites, or metropolitan markets without requiring electrical grid connections or cellular signals.', 'sz': 1900, 'color': '2D3748'}
            ]}
        ]
    ))
    
    return shapes

def build_slide7():
    """Slide 7: Plan of Action & 1 Lakh INR Prize Allocation (Rubric 4: 10 Marks)."""
    shapes = make_header_shapes(
        slide_title="PLAN OF ACTION & 1 LAKH INR BUDGET ALLOCATION",
        rubric_subtitle="RUBRIC 4: BUDGET UTILIZATION & IMMEDIATE 3 STEPS [10 MARKS]",
        slide_num=7
    )
    
    # Top Card: Budget Allocation of 1 Lakh INR
    shapes.append(make_shape_xml(
        shape_id=71, name="Budget Card",
        x=1028700, y=1950000, cx=16230600, cy=4400000,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=180000, lIns=288000, bIns=180000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2700, 'spc_aft': 1000, 'runs': [{'text': 'TRANSPARENT ALLOCATION OF 1 LAKH INR GRAND FINALE PRIZE', 'sz': 2150, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'just', 'ln_spc': 2450, 'spc_aft': 800, 'runs': [
                {'text': '1. Campus & Ward Pilot Batch Production (Rs. 45,000): ', 'sz': 1800, 'b': True, 'color': '2B6CB0'},
                {'text': 'Fabricate 50 outdoor-grade IdleBins (mild steel linkages + UV-stabilized HDPE drums @ Rs. 900/unit) for deployment across Pondicherry University canteens and bus shelters.', 'sz': 1800, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2450, 'spc_aft': 800, 'runs': [
                {'text': '2. Tooling, Dies & Retention Baffle Molds (Rs. 25,000): ', 'sz': 1800, 'b': True, 'color': '2B6CB0'},
                {'text': 'Develop dedicated sheet metal stamping dies for uniform pedal levers and injection-molded rubber retention teeth, slashing manufacturing cycle time by 60%.', 'sz': 1800, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2450, 'spc_aft': 800, 'runs': [
                {'text': '3. Municipal Pilot & SBM Compliance Certification (Rs. 15,000): ', 'sz': 1800, 'b': True, 'color': '2B6CB0'},
                {'text': 'Conduct certified field trials with local Panchayat and Municipal Corporation engineers, logging compaction density metrics and waste reduction telemetry.', 'sz': 1800, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2450, 'spc_aft': 0, 'runs': [
                {'text': '4. Intellectual Property & Design Patent Filing (Rs. 15,000): ', 'sz': 1800, 'b': True, 'color': '2B6CB0'},
                {'text': 'File Indian Design Patent & Utility Model applications for the unique dual-action pedal-platen linkage and one-way gravity retention baffle system.', 'sz': 1800, 'color': '2D3748'}
            ]}
        ]
    ))
    
    # Bottom Card: Immediate Next 3 Steps
    shapes.append(make_shape_xml(
        shape_id=72, name="Immediate Steps Card",
        x=1028700, y=6550000, cx=16230600, cy=2900000,
        fill_hex="EDF2F7", line_hex="CBD5E0", line_w=15000,
        tIns=180000, lIns=288000, bIns=180000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2700, 'spc_aft': 1000, 'runs': [{'text': 'OUR IMMEDIATE NEXT THREE STEPS', 'sz': 2150, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'just', 'ln_spc': 2450, 'spc_aft': 800, 'runs': [
                {'text': '• Step 1 (Within 14 Days): ', 'sz': 1800, 'b': True, 'color': '2B6CB0'},
                {'text': 'Install a 10-bin live pilot across Pondicherry University canteens & hostel gates to benchmark real-world compaction durability, student adoption rates, and spring recoil cycles.', 'sz': 1800, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2450, 'spc_aft': 800, 'runs': [
                {'text': '• Step 2 (Within 30 Days): ', 'sz': 1800, 'b': True, 'color': '2B6CB0'},
                {'text': 'Partner with local sheet-metal fabrication workshops in Puducherry and Chennai industrial corridors to standardize jigs and bring volume production cost below Rs. 600.', 'sz': 1800, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2450, 'spc_aft': 0, 'runs': [
                {'text': '• Step 3 (Within 45 Days): ', 'sz': 1800, 'b': True, 'color': '2B6CB0'},
                {'text': 'Submit verified field trial reports to Puducherry Smart City Development and Swachh Bharat Mission (SBM-U 2.0) officials for municipal ward adoption.', 'sz': 1800, 'color': '2D3748'}
            ]}
        ]
    ))
    
    return shapes

def build_slide8():
    """Slide 8: Execution Timeline & Live Demonstration Plan (Rubric 4: 10 Marks)."""
    shapes = make_header_shapes(
        slide_title="EXECUTION TIMELINE & LIVE DEMO PLAN",
        rubric_subtitle="RUBRIC 4: BUILD, TEST & ITERATE ROADMAP + STAGE DEMO [10 MARKS]",
        slide_num=8
    )
    
    card_w = 7900000
    card_h = 5400000
    y_top = 1950000
    
    # Left Card: 3-Month Roadmap
    shapes.append(make_shape_xml(
        shape_id=81, name="Roadmap Card",
        x=1028700, y=y_top, cx=card_w, cy=card_h,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=288000, bIns=216000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2800, 'spc_aft': 1400, 'runs': [{'text': '3-MONTH BUILD, TEST & ITERATE ROADMAP', 'sz': 2200, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'l', 'ln_spc': 2500, 'spc_aft': 400, 'runs': [
                {'text': '• Month 1 (November 2026): Campus Pilot & Rig Testing', 'sz': 1900, 'b': True, 'color': '2B6CB0'}
            ]},
            {'align': 'just', 'ln_spc': 2500, 'spc_aft': 1200, 'runs': [
                {'text': 'Deploy 50 pilot units across university canteens. Rig-test pedal linkage to 10,000 continuous compression cycles to measure spring fatigue and pivot wear.', 'sz': 1800, 'color': '2D3748'}
            ]},
            {'align': 'l', 'ln_spc': 2500, 'spc_aft': 400, 'runs': [
                {'text': '• Month 2 (December 2026): Feedback Iteration & Tooling', 'sz': 1900, 'b': True, 'color': '2B6CB0'}
            ]},
            {'align': 'just', 'ln_spc': 2500, 'spc_aft': 1200, 'runs': [
                {'text': 'Iterate internal retention teeth geometry based on bottle bounce-back logs; apply zinc-plated anti-corrosion coating; file Indian Design Patent.', 'sz': 1800, 'color': '2D3748'}
            ]},
            {'align': 'l', 'ln_spc': 2500, 'spc_aft': 400, 'runs': [
                {'text': '• Month 3 (January 2027): Municipal Ward Rollout', 'sz': 1900, 'b': True, 'color': '2B6CB0'}
            ]},
            {'align': 'just', 'ln_spc': 2500, 'spc_aft': 0, 'runs': [
                {'text': 'Deploy 100 units across selected commercial streets in Puducherry; conduct third-party waste density and collection frequency audit with municipal officials.', 'sz': 1800, 'color': '2D3748'}
            ]}
        ]
    ))
    
    # Right Card: Stage Demo Script
    shapes.append(make_shape_xml(
        shape_id=82, name="Stage Demo Card",
        x=9350000, y=y_top, cx=card_w, cy=card_h,
        fill_hex="F7FAFC", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=288000, bIns=216000, rIns=288000,
        paragraphs=[
            {'align': 'l', 'ln_spc': 2800, 'spc_aft': 1400, 'runs': [{'text': "TODAY'S 2-MINUTE LIVE STAGE DEMONSTRATION", 'sz': 2200, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 1100, 'runs': [
                {'text': 'Step 1: Touchless Foot Actuation', 'sz': 1850, 'b': True, 'color': '1B4D3E'},
                {'text': ' — Showing effortless pedal press; the lid unlatches without touching dirty surfaces.', 'sz': 1850, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 1100, 'runs': [
                {'text': 'Step 2: Dropping Bulky PET Bottles', 'sz': 1850, 'b': True, 'color': '1B4D3E'},
                {'text': ' — Placing 3 uncrushed water bottles inside, demonstrating how they choke a normal bin.', 'sz': 1850, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 1100, 'runs': [
                {'text': 'Step 3: Single Firm Compaction Stroke', 'sz': 1850, 'b': True, 'color': '1B4D3E'},
                {'text': ' — Stepping down once with an audible, satisfying mechanical crush.', 'sz': 1850, 'color': '2D3748'}
            ]},
            {'align': 'just', 'ln_spc': 2550, 'spc_aft': 0, 'runs': [
                {'text': 'Step 4: Proof of 75% Permanent Compaction', 'sz': 1850, 'b': True, 'color': '1B4D3E'},
                {'text': ' — Opening the inspection hatch to show flat bottles locked safely under the retention baffles.', 'sz': 1850, 'color': '2D3748'}
            ]}
        ]
    ))
    
    # Bottom Closing Statement
    shapes.append(make_shape_xml(
        shape_id=83, name="Closing Statement",
        x=1028700, y=7550000, cx=16230600, cy=1900000,
        fill_hex="EDF2F7", line_hex="CBD5E0", line_w=15000,
        tIns=216000, lIns=288000, bIns=216000, rIns=288000,
        paragraphs=[
            {'align': 'ctr', 'ln_spc': 2800, 'spc_aft': 800, 'runs': [{'text': 'OUR CLOSING COMMITMENT TO THE JURY', 'sz': 2100, 'b': True, 'color': '1B4D3E'}]},
            {'align': 'ctr', 'ln_spc': 2800, 'runs': [
                {'text': '"Respected Judges, instead of spending crores on electronics that break under Indian rain and dust, IdleBin uses simple mechanical physics for Rs. 700 to hold 4 times more plastic, keeping our streets permanently clean."', 'sz': 2000, 'b': True, 'i': True, 'color': '1A202C'}
            ]}
        ]
    ))
    
    return shapes

def assemble_deck():
    """Unpacks the template PPTX, generates 8 custom slide XMLs, updates metadata, and repacks."""
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR, exist_ok=True)
    
    print("1. Extracting base template...")
    with zipfile.ZipFile(TEMPLATE_PATH, 'r') as z:
        z.extractall(BUILD_DIR)
        
    slides_builders = [
        build_slide1,
        build_slide2,
        build_slide3,
        build_slide4,
        build_slide5,
        build_slide6,
        build_slide7,
        build_slide8
    ]
    
    print("2. Generating slide XML files...")
    for idx, builder in enumerate(slides_builders, start=1):
        shapes = builder()
        slide_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
    <p:cSld>
        <p:spTree>
            <p:nvGrpSpPr>
                <p:cNvPr id="1" name=""/>
                <p:cNvGrpSpPr/>
                <p:nvPr/>
            </p:nvGrpSpPr>
            <p:grpSpPr>
                <a:xfrm>
                    <a:off x="0" y="0"/>
                    <a:ext cx="0" cy="0"/>
                    <a:chOff x="0" y="0"/>
                    <a:chExt cx="0" cy="0"/>
                </a:xfrm>
            </p:grpSpPr>
            {''.join(shapes)}
        </p:spTree>
    </p:cSld>
    <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''
        
        slide_path = os.path.join(BUILD_DIR, "ppt", "slides", f"slide{idx}.xml")
        with open(slide_path, "w", encoding="utf-8") as f:
            f.write(slide_xml)
            
        # Write slide rels
        rels_dir = os.path.join(BUILD_DIR, "ppt", "slides", "_rels")
        os.makedirs(rels_dir, exist_ok=True)
        rels_path = os.path.join(rels_dir, f"slide{idx}.xml.rels")
        
        if idx == 1:
            # Slide 1 needs layout and image1.jpeg
            rels_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Target="../slideLayouts/slideLayout7.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"/>
    <Relationship Id="rId2" Target="../media/image1.jpeg" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"/>
</Relationships>'''
        else:
            rels_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Target="../slideLayouts/slideLayout7.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"/>
</Relationships>'''
            
        with open(rels_path, "w", encoding="utf-8") as f:
            f.write(rels_content)

    print("3. Updating presentation.xml with 8 slide IDs...")
    pres_path = os.path.join(BUILD_DIR, "ppt", "presentation.xml")
    sld_id_entries = []
    for i in range(1, 9):
        # IDs 256 to 263, rIds rId6 to rId13
        sld_id_entries.append(f'<p:sldId id="{255 + i}" r:id="rId{5 + i}"/>')
        
    pres_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation saveSubsetFonts="1" embedTrueTypeFonts="true" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
    <p:sldIdLst>
        {''.join(sld_id_entries)}
    </p:sldIdLst>
    <p:sldSz cx="{WIDTH_EMU}" cy="{HEIGHT_EMU}"/>
    <p:notesSz cx="6858000" cy="9144000"/>
    <p:defaultTextStyle>
        <a:defPPr><a:defRPr lang="en-US"/></a:defPPr>
    </p:defaultTextStyle>
</p:presentation>'''
    with open(pres_path, "w", encoding="utf-8") as f:
        f.write(pres_xml)

    print("4. Updating presentation.xml.rels with slide relationships...")
    pres_rels_path = os.path.join(BUILD_DIR, "ppt", "_rels", "presentation.xml.rels")
    rels_entries = [
        '<Relationship Id="rId1" Target="slideMasters/slideMaster1.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster"/>',
        '<Relationship Id="rId2" Target="presProps.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps"/>',
        '<Relationship Id="rId3" Target="viewProps.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps"/>',
        '<Relationship Id="rId4" Target="theme/theme1.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"/>',
        '<Relationship Id="rId5" Target="tableStyles.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles"/>'
    ]
    for i in range(1, 9):
        rels_entries.append(f'<Relationship Id="rId{5 + i}" Target="slides/slide{i}.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"/>')
        
    pres_rels_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    {''.join(rels_entries)}
</Relationships>'''
    with open(pres_rels_path, "w", encoding="utf-8") as f:
        f.write(pres_rels_xml)

    print("5. Updating [Content_Types].xml...")
    ct_path = os.path.join(BUILD_DIR, "[Content_Types].xml")
    slide_overrides = []
    for i in range(1, 9):
        slide_overrides.append(f'<Override ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml" PartName="/ppt/slides/slide{i}.xml"/>')
        
    with open(ct_path, "r", encoding="utf-8") as f:
        ct_content = f.read()
        
    # Replace slide1..slide5 overrides with slide1..slide8
    root = ET.fromstring(ct_content)
    # Remove existing slide overrides
    for child in list(root):
        pn = child.attrib.get('PartName', '')
        if pn.startswith('/ppt/slides/slide'):
            root.remove(child)
            
    for i in range(1, 9):
        ET.SubElement(root, 'Override', {
            'PartName': f'/ppt/slides/slide{i}.xml',
            'ContentType': 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
        })
        
    with open(ct_path, "wb") as f:
        f.write(ET.tostring(root, encoding='utf-8', xml_declaration=True))

    print(f"6. Repacking PPTX into {OUTPUT_PATH}...")
    with zipfile.ZipFile(OUTPUT_PATH, 'w', zipfile.ZIP_DEFLATED) as z_out:
        for root_dir, dirs, files in os.walk(BUILD_DIR):
            for file in files:
                full_p = os.path.join(root_dir, file)
                rel_p = os.path.relpath(full_p, BUILD_DIR)
                z_out.write(full_p, rel_p)

    print("Done! Pitch deck successfully built.")

if __name__ == '__main__':
    assemble_deck()
