from reportlab.platypus import BaseDocTemplate, Paragraph, Spacer, PageBreak, PageTemplate, Frame, NextPageTemplate, FrameBreak
from reportlab.platypus.doctemplate import NextFrameFlowable
from reportlab.platypus.tableofcontents import TableOfContents, ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import PolyLine, Rect, Drawing, Line
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.lib.colors import coral, chartreuse, darkgray, gray

__author__ = 'Gyfis'


class Page(PageTemplate):
    def beforeDrawPage(self, c, _):
        c.setFont('Helvetica', 12)


class MyDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 0

        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('normal', [Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')])
        self.addPageTemplates(template)

    def afterFlowable(self, flowable):
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style
            if style == s_h1:
                key = 'h1-%s' % self.seq.nextf('heading1')
                self.canv.bookmarkPage(key)
                self.notify('TOCEntry', (0, text, self.page, key))
            if style == s_h2:
                key = 'h2-%s' % self.seq.nextf('heading2')
                self.canv.bookmarkPage(key)
                self.notify('TOCEntry', (1, text, self.page, key))


PAGE_WIDTH = A4[0]
PAGE_HEIGHT = A4[1]
styles = getSampleStyleSheet()

summary_splitline_width = 1.8 * mm
summary_splitline_left_x = int(A4[0] / 2 - summary_splitline_width)
summary_splitline_right_x = int(A4[0] / 2 + summary_splitline_width)

separator_height = A4[1] * 0.25 * 0.25
low_separator_height = A4[1] * 0.25 * 0.25 * 0.25
head_height = A4[1] * 0.80 + separator_height


s_normal = styles['Normal']
s_right = ParagraphStyle(name='Right', parent=styles['Normal'], alignment=TA_RIGHT)
s_center = ParagraphStyle(name='Center', parent=styles['Normal'], alignment=TA_CENTER)
s_h1 = styles['Heading1']
s_h1_center = styles['Heading1']
s_h1_center.alignment = TA_CENTER
s_h1n = ParagraphStyle(name='Heading1n', parent=styles['Normal'], fontSize=18, leading=22, spaceAfter=6, alignment=TA_CENTER)
s_h1_toc = ParagraphStyle(name='Heading1toc', parent=styles['Heading1'], fontName='Helvetica', fontSize=16, leading=22, spaceBefore=4, spaceAfter=6, alignment=TA_LEFT)
s_h2_toc = ParagraphStyle(name='Heading2toc', parent=styles['Heading2'], fontName='Helvetica', fontSize=13, leading=22, spaceBefore=2, spaceAfter=4, alignment=TA_LEFT)
s_h2 = styles['Heading2']
s_code = styles['Code']

doc = None
story = []
toc = TableOfContents()
toc.levelStyles = [s_h1_toc, s_h2_toc]

global_alignment_generated = False
local_alignment_generated = False


def add_page_number(canvas, _):
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    text = "Page %s" % canvas.getPageNumber()
    canvas.drawRightString(A4[0] - 0.4 * inch, 0.25 * inch, text)
    canvas.restoreState()


def generate_splitline(width, height, color_a=chartreuse, color_b=coral):
    left_x = 0
    right_x = 2 * summary_splitline_width

    points1 = [[left_x, y[0] - int(0.6 * inch), right_x, y[1] - int(0.6 * inch)] for y in zip(
            xrange(-int(inch / 2.0), int(height + inch), int(inch)),
            xrange(0, int(height + 2 * inch), int(inch)))]

    points2 = [[left_x, y[0] - int(0.6 * inch), right_x, y[1] - int(0.6 * inch)] for y in zip(
            xrange(0, int(height + inch), int(inch)),
            xrange(int(inch / 2.0), int(height + 2 * inch), int(inch)))]

    points1l = [k for x in points1 for k in x]
    points2l = [k for x in points2 for k in x]

    d = Drawing(width=width, height=height)
    d.add(PolyLine(points1l, strokeColor=color_b, strokeWidth=summary_splitline_width))
    d.add(PolyLine(points2l, strokeColor=color_a, strokeWidth=summary_splitline_width))

    for point1 in points1:
        d.add(Line(point1[0], point1[1], point1[2], point1[3], strokeColor=color_b, strokeWidth=summary_splitline_width))

    return d


def generate_separator():
    d = Drawing(width=A4[0] * 1.05, height=separator_height)
    d.add(Rect(0, 0, A4[0] * 1.05, separator_height, fillColor=darkgray, strokeColor=None))
    d.add(Rect(0, 0, A4[0] * 1.05, separator_height / 5.0, fillColor=gray, strokeColor=None))
    return d


def generate_separator_frame(x, y, frame_id='separator'):
    separator = Frame(x, y, A4[0], separator_height,
                      id=frame_id,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    return separator


def generate_low_separator():
    d = Drawing(width=A4[0] * 1.05, height=low_separator_height)
    d.add(Rect(0, 0, A4[0] * 1.05, low_separator_height, fillColor=darkgray, strokeColor=None))
    d.add(Rect(0, 0, A4[0] * 1.05, low_separator_height / 3.0, fillColor=gray, strokeColor=None))
    return d


def generate_low_separator_frame(x, y, frame_id='separator'):
    separator = Frame(x, y, A4[0], low_separator_height,
                      id=frame_id,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    return separator


def generate_histogram(data, left=True):
    chart = HorizontalBarChart()
    drawing = Drawing(300, 400)

    chart.bars.strokeColor = None
    chart.bars[0].fillColor = chartreuse if left else coral
    chart.x = 20 if left else 0
    chart.y = 0
    chart.width = 245
    chart.height = 400
    chart.data = [[data['hist'][c] for c in data['hist']]]
    chart.strokeColor = None
    chart.fillColor = None
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(chart.data[0]) * 1.1
    # chart.valueAxis.visibleTicks = False
    # chart.valueAxis.valueStep = 10
    chart.valueAxis.reverseDirection = 1 if left else 0
    chart.categoryAxis.labels.boxAnchor = 'nw' if left else 'ne'
    chart.categoryAxis.labels.dx = 6 if left else -6
    chart.categoryAxis.labels.dy = 8
    chart.categoryAxis.categoryNames = [c for c in data['hist']]
    chart.categoryAxis.joinAxisMode = 'right' if left else 'left'
    chart.categoryAxis.reverseDirection = 1
    chart.categoryAxis.visibleTicks = False
    chart.categoryAxis.visibleAxis = False
    chart.categoryAxis.strokeColor = None
    drawing.add(chart)
    return drawing


def init_summary(sequence_a_name, sequence_b_name, source_a, source_b, format_a, format_b, summary_data):

    # using global document and story
    global doc, story

    doc = MyDocTemplate('pdf_out/%s_%s.pdf' % (sequence_a_name, sequence_b_name), pagesize=A4)

    # summary frames
    summary_head = Frame(0, head_height, A4[0], A4[1] - head_height, id='summary_head')
    summary_separator = generate_separator_frame(0, A4[1] * 0.80, frame_id='summary_separator')
    summary_splitline = Frame(summary_splitline_left_x, 0, summary_splitline_width * 2, A4[1] * 0.80, id='summary_splitline', topPadding=0, bottomPadding=0)
    summary_left = Frame(0, 0, summary_splitline_left_x, A4[1] * 0.80, id='summary_left', leftPadding=10, rightPadding=16)
    summary_right = Frame(summary_splitline_right_x + 4.5 * summary_splitline_width, 0, summary_splitline_left_x, A4[1] * 0.80, id='summary_right')
    summary_frames = [summary_head, summary_separator, summary_splitline, summary_left, summary_right]

    # init of control objects
    summary = Page(id='summary', pagesize=A4, frames=summary_frames)
    doc.addPageTemplates([summary])

    # summary story building
    story.append(Paragraph('Table of contents', s_h1n))
    story.append(toc)
    story.append(NextPageTemplate('summary'))
    story.append(PageBreak())

    story.append(NextFrameFlowable('summary_head'))
    story.append(Spacer(0, cm))
    story.append(Paragraph('Comparison of %s and %s' % (sequence_a_name, sequence_b_name), s_h1))
    story.append(Paragraph('Sequence A source: <b><i>%s</i></b>, format: <b><i>%s</i></b>' % (source_a, format_a), s_center))
    story.append(Paragraph('Sequence B source: <b><i>%s</i></b>, format: <b><i>%s</i></b>' % (source_b, format_b), s_center))
    story.append(NextFrameFlowable('summary_splitline'))
    story.append(generate_splitline(summary_splitline_width * 2, A4[1] * 0.80))
    story.append(NextFrameFlowable('summary_separator'))
    story.append(generate_separator())
    story.append(NextFrameFlowable('summary_left'))
    story.append(FrameBreak())

    story.append(Paragraph('Sequence: <b>%s</b>' % sequence_a_name, s_right))
    story.append(Spacer(0, 2 * mm))
    story.append(Paragraph('Length of sequence', s_right))
    story.append(Spacer(0, mm))
    story.append(Paragraph('<b>%s</b>' % summary_data[0]['len'], s_right))
    story.append(Spacer(0, 5 * mm))
    story.append(Paragraph('Histogram of sequence (in %)', s_right))
    story.append(Spacer(0, 2 * mm))
    story.append(generate_histogram(summary_data[0]))

    story.append(NextFrameFlowable('summary_right'))
    story.append(FrameBreak())

    story.append(Paragraph('Sequence: <b>%s</b>' % sequence_b_name, s_normal))
    story.append(Spacer(0, 2 * mm))
    story.append(Paragraph('Length of sequence', s_normal))
    story.append(Spacer(0, mm))
    story.append(Paragraph('<b>%s</b>' % summary_data[1]['len'], s_normal))
    story.append(Spacer(0, 5 * mm))
    story.append(Paragraph('Histogram of sequence (in %)', s_normal))
    story.append(Spacer(0, 2 * mm))
    story.append(generate_histogram(summary_data[1], left=False))


def add_global_alignment_section():
    global doc, story

    global_alignment_head = Frame(0, head_height, A4[0], A4[1] - head_height, leftPadding=20, id='global_alignment_head')
    global_alignment_separator = generate_low_separator_frame(0, A4[1] * 0.90, frame_id='global_alignment_separator')
    global_alignment_paragraph = Frame(0, 0, A4[0], A4[1] * 0.90, leftPadding=20, id='global_alignment_paragraph')
    global_alignment_frames = [global_alignment_head, global_alignment_separator, global_alignment_paragraph]

    global_alignment = Page(id='global_alignment', pagesize=A4, frames=global_alignment_frames, onPage=add_page_number)
    doc.addPageTemplates([global_alignment])

    story.append(NextPageTemplate('global_alignment'))
    story.append(PageBreak())
    story.append(Paragraph('Global alignment', s_h1))


def add_global_alignment(global_alignment_data):
    global doc, story, global_alignment_generated

    if not global_alignment_generated:
        add_global_alignment_section()
        global_alignment_generated = True
    else:
        story.append(PageBreak())
        story.append(Spacer(0, 6 * mm))

    story.append(NextFrameFlowable('global_alignment_head'))
    story.append(Paragraph('Global alignment { %s }' % global_alignment_data['header'], s_h2))
    story.append(NextFrameFlowable('global_alignment_separator'))
    story.append(FrameBreak())
    story.append(generate_low_separator())
    story.append(NextFrameFlowable('global_alignment_paragraph'))
    story.append(FrameBreak())
    story.append(Paragraph('Score of the alignment: %s' % global_alignment_data['score'], s_normal))
    story.append(Spacer(0, 2 * mm))
    story.append(Paragraph('Alignment:', s_normal))
    story.append(Paragraph(global_alignment_data['string'], s_code))


def add_local_alignment_section():
    global doc, story

    local_alignment_head = Frame(0, head_height, A4[0], A4[1] - head_height, leftPadding=20, id='local_alignment_head')
    local_alignment_separator = generate_low_separator_frame(0, A4[1] * 0.93, frame_id='local_alignment_separator')
    local_alignment_paragraph = Frame(0, 0, A4[0], A4[1] * 0.93, leftPadding=20, id='local_alignment_paragraph')
    local_alignment_frames = [local_alignment_head, local_alignment_separator, local_alignment_paragraph]

    local_alignment = Page(id='local_alignment', pagesize=A4, frames=local_alignment_frames, onPage=add_page_number)
    doc.addPageTemplates([local_alignment])

    story.append(NextPageTemplate('local_alignment'))
    story.append(PageBreak())
    story.append(NextFrameFlowable('local_alignment_head'))
    story.append(Paragraph('Local alignment', s_h1))


def add_local_alignment(local_alignment_data):
    global doc, story, local_alignment_generated

    if not local_alignment_generated:
        add_local_alignment_section()
        local_alignment_generated = True

        story.append(NextFrameFlowable('local_alignment_separator'))
        story.append(FrameBreak())
        story.append(generate_low_separator())
        story.append(NextFrameFlowable('local_alignment_paragraph'))
        story.append(FrameBreak())
    else:
        story.append(Spacer(0, 6 * mm))

    story.append(Paragraph('Local alignment { %s }' % local_alignment_data['header'], s_h2))
    story.append(Paragraph('Score of the alignment: %s' % local_alignment_data['score'], s_normal))
    story.append(Spacer(0, 1.5 * mm))
    story.append(Paragraph('Alignment:', s_normal))
    story.append(Paragraph(local_alignment_data['string'], s_code))


def build():
    global doc, story
    doc.multiBuild(story)
