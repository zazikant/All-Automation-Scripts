import cv2
import numpy as np
import json
import argparse
import os

def identify_elements(img, x_offset, y_offset):
    elements = []
    
    # Define color ranges in HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Black (Text)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 30])
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    
    # Grey (Image) - Adjust ranges carefully based on typical skeleton grey
    lower_grey = np.array([0, 0, 50])
    upper_grey = np.array([180, 50, 230])
    mask_grey = cv2.inRange(hsv, lower_grey, upper_grey)
    
    # Yellow (Button)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([40, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    def find_and_append(mask, elem_type):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 10 and h > 10:  # Ignore noise
                elements.append({
                    "id": f"{elem_type}_{i}",
                    "type": elem_type,
                    "x": x_offset + x,
                    "y": y_offset + y,
                    "width": w,
                    "height": h
                })
                
    find_and_append(mask_black, "text")
    find_and_append(mask_grey, "image")
    find_and_append(mask_yellow, "button")
    
    # Sort elements top to bottom
    elements.sort(key=lambda e: e['y'])
    
    return elements

def analyze_image(filepath):
    img = cv2.imread(filepath)
    if img is None:
        return {"error": f"Could not open or find the image {filepath}"}
    
    # Simple approach to find sections: find horizontal lines 
    # Or find large bounding boxes. Let's use edge detection to find sections
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    sections = []
    
    # We assume large external contours are sections
    for i, cnt in enumerate(reversed(contours)): # reversed often gives top-to-bottom
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 100 and h > 50: # Minimum section size
            section_img = img[y:y+h, x:x+w]
            elements = identify_elements(section_img, x, y)
            sections.append({
                "id": f"section_{i+1}",
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "elements": elements
            })
            
    # Sort sections top to bottom 
    sections.sort(key=lambda s: s['y'])
    # re-index
    for i, s in enumerate(sections):
        s["id"] = f"section_{i+1}"
            
    return {"sections": sections}

def crop_section(filepath, section_index, output_dir="."):
    img = cv2.imread(filepath)
    analysis = analyze_image(filepath)
    
    if "error" in analysis:
        return analysis
        
    sections = analysis.get("sections", [])
    # 1-based indexing for CLI
    if section_index < 1 or section_index > len(sections):
        return {"error": f"Invalid section {section_index}. Found {len(sections)} sections."}
        
    s = sections[section_index - 1]
    cropped = img[s['y']:s['y']+s['height'], s['x']:s['x']+s['width']]
    
    out_path = os.path.join(output_dir, f"section_{section_index}.png")
    cv2.imwrite(out_path, cropped)
    return {"status": "success", "file": out_path, "section": s}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Worker to analyze Skeleton images.")
    parser.add_argument("--analyze", action="store_true", help="Analyze the image and return JSON")
    parser.add_argument("--crop", action="store_true", help="Crop a specific section")
    parser.add_argument("--input", type=str, help="Input image file")
    parser.add_argument("--section", type=int, default=1, help="Section index to crop (1-based)")
    parser.add_argument("--outdir", type=str, default=".", help="Output directory for cropped images")
    
    args = parser.parse_args()
    
    if not args.input:
        print(json.dumps({"error": "Missing --input"}))
        exit(1)
        
    if args.analyze:
        result = analyze_image(args.input)
        print(json.dumps(result, indent=2))
        
    elif args.crop:
        result = crop_section(args.input, args.section, args.outdir)
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps({"error": "Must specify --analyze or --crop"}))
