## Technical Analysis of the Mailster Reference HTML

The provided HTML file is a template for an email newsletter, specifically designed to be compatible with the Mailster WordPress plugin. Here's a breakdown of the key technical aspects:

### 1. Email HTML Best Practices

The HTML structure and styling adhere to common best practices for email design, which prioritize compatibility across a wide range of email clients (like Outlook, Gmail, Apple Mail, etc.).

*   **Table-Based Layout:** The entire layout is built using `<table>` elements. This is a long-standing practice in email development to ensure consistent rendering, as modern CSS layout properties like Flexbox and Grid are not well-supported in many email clients.
*   **Inline CSS:** The majority of the styling is applied using inline `style` attributes on individual HTML elements (e.g., `<td style="background-color: #ffffff;">`). This is crucial because many email clients strip out `<style>` blocks or external stylesheets.
*   **CSS Resets:** The template includes CSS resets to normalize default styles across different email clients. For example, `body { width: 100% !important; -webkit-text-size-adjust: 100%; }` and `table { border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }`. The `mso-` prefixes are specifically for Microsoft Outlook.
*   **Media Queries:** The template uses `@media` queries to create a responsive design for mobile devices. When the screen width is 599px or less, the layout adjusts to a single column, and font sizes are increased for better readability.
*   **Image Handling:** Images have attributes like `border="0"`, `outline: none`, and `text-decoration: none` to prevent unwanted borders and spacing that some email clients might add.

### 2. Mailster Plugin Integration

The template is clearly intended for use with the Mailster plugin, as evidenced by the presence of several proprietary tags and attributes:

*   **Template Tags:** The HTML includes various Mailster-specific template tags that are replaced with dynamic content when the email is sent:
    *   `{lang}`: Sets the language of the email.
    *   `{preheader}`:  A short summary text that follows the subject line when an email is viewed in the inbox.
    *   `{webversionlink}`: A link to view the email in a web browser.
    *   `{emailaddress}`: The recipient's email address.
*   **Editable Content Areas:** Mailster's editable content system is implemented through custom HTML tags and attributes:
    *   `<modules>` and `<module>`: These tags define modular sections of the email that can be rearranged or edited in the Mailster drag-and-drop editor.
    *   `editable=""`: This attribute is used on elements like `<img>` to make them replaceable in the editor.
    *   `<single>` and `<multi>`: These tags define single-line and multi-line text areas that are editable.
    *   `<buttons>`: This tag is used to create editable buttons.

### 3. Fonts

*   **Google Fonts:** The template imports "Raleway" and "Open Sans" from Google Fonts using `@import`.
*   **Font Stacks:** It specifies fallback fonts (e.g., `font-family: Helvetica, Arial, sans-serif;`) to ensure that the email still looks acceptable even if the custom fonts don't load.

### 4. Overall Structure

The email has a main wrapping table with the class `bodytbl`. The content is then broken down into logical sections (modules), each contained within its own `<table>`. This modular structure makes it easier to manage and edit the content in the Mailster editor.

## New Project Instructions

For making a html file.. i will be giving a skeleton layout of elements in image format.. you need to understand structure and make a html file with appropriate placeholders for image element

The reference image skeleton is in the folder `/home/zazikant/skeleton`.

### Element Identification

*   **Text box:** Black color
*   **Image:** Grey color
*   **Container boxes:** Strokes (for reference only, code tables with exact dimensions)
*   **Button:** Yellow color

### Spacing

To add spacing above or below a section, table, or any element, use the following format:

```html
<tr>
    <td height="12" colspan="3"></td>
</tr>
```

### Button Code

```html
<tr>
    <td width="552" valign="top" align="center">
        <div class="btn">
            <buttons data-tmpl="%3Ctable%20class%3D%22textbutton%22%20align%3D%22center%22%20role%3D%22presentation%22%3E%3Ctbody%3E%3Ctr%3E%3Ctd%20align%3D%22center%22%20width%3D%22auto%22%3E%3Ca%20href%3D%22%22%20editable%3D%22%22%20label%3D%22Read%20More%22%3ERead%20More%3C%2Fa%3E%3C%2Ftd%3E%3C%2Ftr%3E%3C%2Ftbody%3E%3C%2Ftable%3E">
                <table class="textbutton" align="center" role="presentation">
                    <tbody>
                        <tr>
                            <td align="center" width="auto"><a href="https://gemengserv.com/light-guase-steel-lgs-a-modern-technology-for-faster-construction/?utm_source=Newsletter_Mar2025&amp;utm_medium=Email&amp;utm_campaign=Newsletter_Mar2025" editable="" label="Read More">Read Full Article →</a></td>
                        </tr>
                    </tbody>
                </table>
            </buttons>
        </div>
    </td>
</tr>
```

## Updated Workflow

1.  **Understand:** Analyze the user's request and the provided materials (e.g., skeleton image, reference files).
2.  **Plan and Review:** Break down the task into smaller steps. For HTML creation, this includes identifying each element, its dimensions, and its position in the layout.
3.  **To-Do List:** Create a detailed to-do list based on the plan. This list will be shared with the user for review.
4.  **Confirmation:**  Wait for the user's confirmation before executing the to-do list.
5.  **Execution:** Create the HTML file based on the confirmed to-do list.

### Coding Conventions

*   **Table Widths:** Do not use percentage widths (e.g., `width="50%"`). Always consider the maximum width as 600px and calculate the exact pixel values for `width` attributes.
*   **Spacing `<td>`:** For spacing above or below a section, table, or any element, use the following mandatory format:

    ```html
    <tr>
        <td height="12" colspan="3"></td>
    </tr>
    ```
