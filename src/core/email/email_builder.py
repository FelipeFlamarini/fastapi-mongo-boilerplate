class EmailBuilder:
    """Helper class for building structured HTML emails"""
    
    def __init__(self):
        self._content = []
        self._style = """
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { padding: 20px; background-color: #f8f9fa; text-align: center; }
                .footer { padding: 20px; background-color: #f8f9fa; text-align: center; font-size: 12px; }
                .content { padding: 20px; }
                .button { 
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }
            </style>
        """

    def add_header(self, content: str) -> 'EmailBuilder':
        """Add a header section to the email"""
        self._content.append(f'<div class="header">{content}</div>')
        return self

    def add_footer(self, content: str) -> 'EmailBuilder':
        """Add a footer section to the email"""
        self._content.append(f'<div class="footer">{content}</div>')
        return self

    def add_text(self, text: str) -> 'EmailBuilder':
        """Add regular text paragraph"""
        self._content.append(f'<p>{text}</p>')
        return self

    def add_bold(self, text: str) -> 'EmailBuilder':
        """Add bold text"""
        self._content.append(f'<p><strong>{text}</strong></p>')
        return self

    def add_inline_text(self, text: str) -> 'EmailBuilder':
        """Add text that doesn't create a new line"""
        self._content.append(f'<span>{text}</span>')
        return self

    def add_link(self, text: str, url: str) -> 'EmailBuilder':
        """Add a hyperlink"""
        self._content.append(f'<a href="{url}">{text}</a>')
        return self

    def add_button(self, text: str, url: str) -> 'EmailBuilder':
        """Add a button-style link"""
        self._content.append(f'<a href="{url}" class="button">{text}</a>')
        return self

    def add_list(self, items: list[str], ordered: bool = False) -> 'EmailBuilder':
        """Add a bulleted or numbered list"""
        tag = 'ol' if ordered else 'ul'
        items_html = ''.join([f'<li>{item}</li>' for item in items])
        self._content.append(f'<{tag}>{items_html}</{tag}>')
        return self

    def add_divider(self) -> 'EmailBuilder':
        """Add a horizontal divider line"""
        self._content.append('<hr>')
        return self

    def add_custom_html(self, html: str) -> 'EmailBuilder':
        """Add custom HTML content"""
        self._content.append(html)
        return self

    def build(self) -> str:
        """Build the final HTML email content"""
        content_html = ''.join(self._content)
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            {self._style}
        </head>
        <body>
            <div class="content">
                {content_html}
            </div>
        </body>
        </html>
        """