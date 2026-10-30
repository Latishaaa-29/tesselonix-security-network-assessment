"""Optional printable report: pip install reportlab, then run this script."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted

root = Path(__file__).resolve().parents[1]
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CodeSmall', fontName='Courier', fontSize=6.5, leading=9))
styles['BodyText'].fontSize = 9
styles['BodyText'].leading = 13
story = [Paragraph('Tesselonix Assessment', styles['Title']),
         Paragraph('Application Security Audit &amp; Network Troubleshooting', styles['Heading2']),
         Paragraph('Target: Microblog a975ef64864354867c88e0ed3a17ba7d17dca752', styles['BodyText']),
         Paragraph('Prepared 30 October 2026. AI assistance disclosed in TOOLS_AND_AI.md. '
                   'Raw evidence and executable source are in the accompanying repository.', styles['BodyText']),
         Paragraph('Repository: https://github.com/Latishaaa-29/tesselonix-security-network-assessment', styles['BodyText'])]

for path in [root / 'TOOLS_AND_AI.md'] + sorted((root / 'reports').glob('0*.md')):
    story.append(PageBreak())
    buffer = []
    code = False
    def flush():
        if buffer:
            text = ' '.join(buffer)
            story.append(Paragraph(escape(text), styles['BodyText']))
            story.append(Spacer(1, 3*mm))
            buffer.clear()
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('```'):
            flush()
            code = not code
            continue
        if code or line.startswith('|'):
            flush()
            # Wrap long literal lines rather than clip the printable report.
            import textwrap
            story.append(Preformatted('\n'.join(textwrap.wrap(line, width=104, replace_whitespace=False)) or ' ', styles['CodeSmall']))
        elif line.startswith('#'):
            flush()
            level = min(len(line) - len(line.lstrip('#')), 3)
            story.append(Paragraph(escape(line.lstrip('#').strip()), styles['Heading' + str(level)]))
        elif not line.strip():
            flush()
        else:
            buffer.append(line)
    flush()

def footer(canvas, doc):
    canvas.setFont('Helvetica', 8)
    canvas.drawString(18*mm, 12*mm, 'Tesselonix | Local isolated lab | See repository for raw evidence')
    canvas.drawRightString(192*mm, 12*mm, str(doc.page))

SimpleDocTemplate(str(root / 'reports/assessment-report.pdf'), pagesize=A4,
    rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=20*mm,
    title='Tesselonix Security and Network Assessment').build(story, onFirstPage=footer, onLaterPages=footer)
print('Generated reports/assessment-report.pdf')
