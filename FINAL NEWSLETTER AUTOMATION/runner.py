import subprocess
import json
import sys
import os

def get_sections(image_path):
    print(f"Running worker.py on {image_path}...")
    result = subprocess.run(["python", "worker.py", "--analyze", "--input", image_path], capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error parsing worker output. Raw output:\n{result.stdout}")
        return None

def main():
    print("====================================")
    print(" Vision Agent CLI Pipeline Started")
    print("====================================")
    
    image_path = "Skeleton.png"
    if not os.path.exists(image_path):
         print(f"Error: {image_path} not found.")
         return
         
    data = get_sections(image_path)
    
    if not data or "sections" not in data:
        print("Could not find sections. Exiting.")
        return
        
    sections = data["sections"]
    print(f"Detected {len(sections)} layout elements.")
    
    final_html_parts = []
    
    for idx, sec in enumerate(sections):
        # We will group all into sections for simplicity, or step by step
        print(f"\n" + "="*40)
        print(f" PROCESSING SECTION {idx+1}/{len(sections)}")
        print(f" ID: {sec['id']}, Width: {sec['width']}, Height: {sec['height']}")
        print(f" Elements found: {len(sec.get('elements', []))}")
        print("="*40)
        
        # Optional: crop the section so the agent can see it directly
        subprocess.run(["python", "worker.py", "--crop", "--input", image_path, "--section", str(idx+1)])
        print(f"\n[SYSTEM] Agent, please look at 'section_{idx+1}.png' and context above.")
        
        while True:
            print(f"[SYSTEM] Agent, generate the Mailster HTML for Section {idx+1}.")
            print("Type your HTML code below. When done, type 'EOF' on a new line to submit.")
            
            lines = []
            while True:
                try:
                    line = input()
                    if line.strip() == "EOF":
                        break
                    lines.append(line)
                except EOFError:
                    break
            
            generated_html = "\n".join(lines)
            
            print("\n[HITL REVIEW]")
            print("-" * 50)
            print(generated_html)
            print("-" * 50)
            
            choice = input(f"[HUMAN] Approve this HTML for section {idx+1}? (y = approve, n = retry, s = skip): ").strip().lower()
            
            if choice == 'y' or choice == 'yes':
                final_html_parts.append(generated_html)
                print(f"[SYSTEM] Section {idx+1} approved and saved.")
                break
            elif choice == 's' or choice == 'skip':
                print(f"[SYSTEM] Section {idx+1} skipped.")
                break
            else:
                print(f"[SYSTEM] Human requested retry. Please provide updated HTML.")
                
    # Assemble final template
    print("\n" + "="*40)
    print(" ALL SECTIONS COMPLETED")
    print("="*40)
    
    header = """<!DOCTYPE html>
<html lang="{lang}" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width,initial-scale=1 user-scalable=yes" />
    <meta name="format-detection" content="telephone=no, date=no, address=no, email=no, url=no" />
    <meta name="x-apple-disable-message-reformatting" />
    <style type="text/css" data-embed>
        @import url("https://fonts.googleapis.com/css?family=Raleway:400,700|Open+Sans:400,700");

        @media only screen {
            h1, h2, h3, h4, h5, h6, table.textbutton a {
                font-family: Raleway, sans-serif !important;
                font-weight: 700 !important;
            }
            th, td {
                font-family: "Open Sans", sans-serif !important;
            }
            p, li {
                font-family: "Georgia", "Times New Roman", Times, serif !important;
                font-weight: 450 !important;
            }
        }
    </style>
    <style type="text/css">
        body {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            background-color: #f3f4f4;
        }
        table {
            border-collapse: collapse;
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
            font-family: Helvetica, Arial, sans-serif;
            font-size: 16px;
        }
        .o-fix table, .o-fix td {
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }
        img {
            outline: none;
            text-decoration: none;
            max-width: 100%;
        }
        .padd { width: 24px; }
        table.textbutton td {
            background: #fecf07;
            padding: 9px 16px;
            border-radius: 6px;
        }
        table.textbutton a {
            color: #341ec4;
            font-size: 18px;
            text-decoration: none;
        }
        @media only screen and (max-width: 599px) {
            .wrap { width: 96% !important; }
            .wrap table { width: 100% !important; }
            .wrap img { max-width: 100% !important; height: auto !important; }
        }
    </style>
    <title>{subject}</title>
</head>
<body>
    <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background-color: #f3f4f4;">
        <tbody>
            <tr>
                <td align="center">
                    <div style="display: none;">{preheader}</div>
                    
                    <table width="600" cellpadding="0" cellspacing="0" role="presentation" style="background-color: white">
                        <tbody>
                            <tr>
                                <td width="24" class="padd">&zwnj;</td>
                                <td width="552" valign="top" align="center">
                                    <multi label="Body"><p>Click on the <span style="text-decoration: underline;" data-mce-style="text-decoration: underline;"><a href="{webversionlink}" data-mce-href="https://gemengserv.net/sz/wp-admin/{webversionlink}">webview </a></span>if the message is not displayed properly.<br>For business enquiries, write to us at <a href="mailto:business@gemengserv.com?subject=Interest%20in%20your%20service%20offerings&amp;body=You%20can%20type%20your%20requirement%20here." data-mce-href="mailto:business@gemengserv.com?subject=Interest%20in%20your%20service%20offerings&amp;body=You%20can%20type%20your%20requirement%20here.">business@gemengserv.com </a></p></multi>
                                </td>
                                <td width="24" class="padd">&zwnj;</td>
                            </tr>
                            <tr>
                                <td width="24" class="padd">&zwnj;</td>
                                <td width="552" valign="top" align="center">
                                    <img src="https://gemengserv.com/wp-content/uploads/2025/09/GEM-logo_sept2025.png" alt="Header Image 1" width="120" height="auto" border="0" editable="" class="">
                                </td>
                                <td width="24" class="padd">&zwnj;</td>
                            </tr>
"""
    footer = """                            <tr>
                                <td width="24" class="padd">&zwnj;</td>
                                <td width="552" valign="top">
                                    <table cellpadding="0" cellspacing="0" class="o-fix" role="presentation">
                                        <tbody>
                                            <tr>
                                                <td valign="top" align="left">
                                                    <multi label="Body"><p style="font-size: 12px !important; line-height: 1.4em;" data-mce-style="font-size: 12px !important; line-height: 1.4em;">Liked this newsletter? Send it to your colleagues and help us grow. You have received this email because you have subscribed to GEM Engserv as {emailaddress}. If you no longer wish to receive emails please <strong><a href="https://gemengserv.com/gem-newsletter-unsubscribe/" data-mce-href="https://gemengserv.com/gem-newsletter-unsubscribe/">Unsubscribe.</a></strong></p></multi>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                                <td width="24" class="padd">&zwnj;</td>
                            </tr>
                            <tr>
                                <td height="24" colspan="3"></td>
                            </tr>
                        </tbody>
                    </table>

                    <table width="600" cellpadding="0" cellspacing="0" role="presentation" style="background-color: white">
                        <tbody>
                            <tr>
                                <td width="600" valign="top" align="left">
                                    <table cellpadding="0" cellspacing="0" role="presentation">
                                        <tbody>
                                            <tr>
                                                <td width="600" valign="top" align="center"><img src="https://gemengserv.net/sz/wp-content/uploads/mailster/templates/mymail/img/shadow.png" alt="Shadow for Newsletter" width="600" height="25" border="0" style="max-width: 600px; max-height: 25px">
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                            </tr>
                        </tbody>
                    </table>                    
                </td>
            </tr>
        </tbody>
    </table>
</body>
</html>"""
    final_html = header + "\n".join(final_html_parts) + "\n" + footer
    
    with open("mailster_template.html", "w") as f:
        f.write(final_html)
    print("[SYSTEM] Output saved to mailster_template.html. Pipeline finished.")

if __name__ == "__main__":
    main()
