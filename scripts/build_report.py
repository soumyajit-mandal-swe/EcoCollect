"""Render the editable Markdown report as a standalone PDF using ReportLab."""
from pathlib import Path
from html import escape
import re
import textwrap
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4

root=Path(__file__).resolve().parents[1]
out=root/'output/pdf'; out.mkdir(parents=True,exist_ok=True)
styles=getSampleStyleSheet()
styles['Normal'].fontName='Helvetica'; styles['Normal'].fontSize=10; styles['Normal'].leading=14; styles['Normal'].spaceAfter=7
styles['Title'].fontSize=30; styles['Title'].leading=36; styles['Title'].textColor=colors.HexColor('#172a20')
styles['Heading2'].fontSize=14; styles['Heading2'].leading=19; styles['Heading2'].spaceBefore=17; styles['Heading2'].spaceAfter=10; styles['Heading2'].textColor=colors.HexColor('#184e34')
styles.add(ParagraphStyle('TableText',parent=styles['Normal'],fontSize=8,leading=11,spaceAfter=0))
styles.add(ParagraphStyle('CodeSmall',fontName='Courier',fontSize=7.2,leading=10,spaceAfter=12))
styles.add(ParagraphStyle('Caption',parent=styles['Normal'],fontSize=9,textColor=colors.HexColor('#65746b'),alignment=TA_CENTER))

def clean(s):
    return s.replace('→',' -> ').replace('—','-').replace('–','-').replace('’',"'").replace('“','"').replace('”','"')
def inline(s):
    s=escape(clean(s))
    s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    return s.replace('`','')

lines=(root/'docs/PROJECT_REPORT.md').read_text(encoding='utf-8').splitlines()
story=[]; i=0
while i<len(lines):
    line=lines[i]
    if not line.strip(): i+=1; continue
    if line.startswith('# '):
        story += [Spacer(1,70),Paragraph('EcoCollect',styles['Title'])]
    elif line.startswith('## E-Waste'):
        story += [Paragraph('E-Waste Collection and Recycling<br/>Management System',styles['Heading2']),Spacer(1,28)]
    elif line.startswith('## '):
        if line.startswith('## 1. '): story.append(PageBreak())
        story.append(Paragraph(inline(line[3:]),styles['Heading2']))
    elif line.startswith('```'):
        language=line[3:]; block=[]; i+=1
        while i<len(lines) and not lines[i].startswith('```'):
            block.append(lines[i]); i+=1
        if language=='mermaid':
            if any('erDiagram' in s for s in block):
                rows=[['Parent','Relationship','Child'],['users','1 to many','collection_requests'],['recycling_centres','0 or 1 to many','collection_requests'],['collection_requests','1 to many','request_items'],['ewaste_categories','1 to many','request_items'],['collection_requests','1 to many','status_history'],['users','1 to many','status_history']]
                table=Table([[Paragraph(inline(x),styles['TableText']) for x in row] for row in rows],colWidths=[180,100,190],repeatRows=1)
                table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9f1eb')),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#d7e1d9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
                story += [table,Spacer(1,12),Paragraph('Reproducible diagram source: docs/ER_DIAGRAM.md',styles['Caption'])]
            else:
                story.append(Paragraph('Browser (React) -> Vite /api proxy -> FastAPI -> SQLAlchemy / PyMySQL -> Local MySQL',styles['Normal']))
        else:
            wrapped='\n'.join('\n'.join(textwrap.wrap(clean(s),width=100,replace_whitespace=False,drop_whitespace=False)) or ' ' for s in block)
            story.append(Preformatted(wrapped,styles['CodeSmall']))
    elif line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            cells=[c.strip() for c in lines[i].strip('|').split('|')]
            if not all(re.fullmatch(r'[-: ]+',c) for c in cells): rows.append([Paragraph(inline(c),styles['TableText']) for c in cells])
            i+=1
        i-=1
        widths=[100,145,225] if len(rows[0])==3 else [125,345]
        table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9f1eb')),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#d7e1d9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
        story += [table,Spacer(1,12)]
    elif line.startswith('- '): story.append(Paragraph('• '+inline(line[2:]),styles['Normal']))
    else: story.append(Paragraph(inline(line),styles['Normal']))
    i+=1

screenshot=root/'docs/screenshots/dashboard.png'
if screenshot.exists():
    from PIL import Image as PILImage
    w,h=PILImage.open(screenshot).size
    story += [PageBreak(),Paragraph('Appendix A - Actual application screenshot',styles['Heading2']),Paragraph('Administrator overview captured from the running local application.',styles['Normal']),Image(str(screenshot),width=470,height=470*h/w)]

def footer(canvas,doc):
    canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#7a887f'))
    canvas.drawString(58,30,'EcoCollect | DBMS Mini-Project')
    canvas.drawRightString(A4[0]-58,30,str(doc.page))
doc=SimpleDocTemplate(str(out/'EcoCollect_Project_Report.pdf'),pagesize=A4,rightMargin=58,leftMargin=58,topMargin=48,bottomMargin=48,title='EcoCollect DBMS Mini-Project Report',author='')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out/'EcoCollect_Project_Report.pdf')
