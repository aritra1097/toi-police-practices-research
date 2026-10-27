"""Generate the four-page descriptive comparative report from audited outputs.

Run with Python having reportlab installed. No source-body text is republished.
The adjacent analysis outputs must exist; the script does not refit the SCM.
"""
from pathlib import Path
import csv, json, html, hashlib, re
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
OUT=HERE/'comparative_police_practices_note.pdf'
TMP=HERE/'rendered'
TMP.mkdir(exist_ok=True)
ledger=list(csv.DictReader((BASE/'event_coding/event_ledger.csv').open()))
counts=list(csv.DictReader((BASE/'analysis/detected_case_window_counts.csv').open()))
scm=json.loads((BASE/'analysis/scm_gun_taking_police_shooting/summary.json').read_text())
cohort_path=BASE/'collection/output/collection_summary.json'
if not cohort_path.exists():cohort_path=BASE/'collection/collection_summary.json'
cohort=json.loads(cohort_path.read_text())
audit=json.loads((BASE/'collection/audit_negatives/review_summary.json').read_text())
rows={e['event_id']:e for e in ledger}
def n(st, outcome, window):
 return next(int(r['detected_case_count']) for r in counts if r['state']==st and r['outcome']==outcome and r['window']==window)
assert n('WB','gun_taking_police_shooting','post_main')==3
assert n('WB','police_public_parade_broad','post_main')==4
assert n('WB','police_reconstruction_shirtless','post_main')==1
assert n('WB','police_public_parade_broad','post_transition_inclusive')==5
assert scm['weight_set_nonunique'] and scm['treated_pre_all_zero']

FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
if Path(FONT).exists():
 pdfmetrics.registerFont(TTFont('Body',FONT));pdfmetrics.registerFont(TTFont('BodyBold',BOLD))
else:
 pdfmetrics.registerFont(TTFont('Body','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
 pdfmetrics.registerFont(TTFont('BodyBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
NAVY=colors.HexColor('#153D50'); TEAL=colors.HexColor('#087F8C'); GRAY=colors.HexColor('#556570'); LIGHT=colors.HexColor('#EDF3F5')
styles={
 'title':ParagraphStyle('Title',fontName='BodyBold',fontSize=24,leading=28,textColor=NAVY,spaceAfter=12),
 'deck':ParagraphStyle('Deck',fontName='Body',fontSize=12,leading=17,textColor=NAVY,spaceAfter=14),
 'h':ParagraphStyle('H',fontName='BodyBold',fontSize=14,leading=18,textColor=NAVY,spaceBefore=12,spaceAfter=7),
 'p':ParagraphStyle('P',fontName='Body',fontSize=10,leading=14,textColor=colors.HexColor('#26343B'),spaceAfter=9),
 'small':ParagraphStyle('Small',fontName='Body',fontSize=8.5,leading=11.5,textColor=GRAY,spaceAfter=7),
 'cell':ParagraphStyle('Cell',fontName='Body',fontSize=9,leading=12,textColor=colors.HexColor('#26343B')),
 'headcell':ParagraphStyle('HeadCell',fontName='BodyBold',fontSize=8.7,leading=11,textColor=colors.white),
 'source':ParagraphStyle('Source',fontName='Body',fontSize=8.6,leading=11.8,textColor=GRAY,spaceAfter=6),
}
# Register bold markup through font family.
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
def P(t,style='p'):
 # Normalise visible date/count spacing without touching hyperlink attributes.
 parts=re.split(r'(<[^>]*>)',t)
 for i in range(0,len(parts),2):
  z=parts[i]
  z=re.sub(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)(?=\d)',r'\1 ',z)
  z=re.sub(r'(\d)(January|February|March|April|May|June|July|August|September|October|November|December)',r'\1 \2',z)
  z=re.sub(r'\b(on|in|from|through|only|all|every|with|over|for|than|to|per|a|zero|one|three|these)(?=\d)',r'\1 ',z)
  z=re.sub(r'(?<=\d)(?=days|day|articles|bodies|events|reports|people|accused|explicit|possible|unique|available|times)',r' ',z)
  z=z.replace('0to1','0 to 1').replace('central50/50','central 50/50').replace('screen flagged245','screen flagged 245').replace('random48','random 48').replace('correction139','correction 139').replace('were completed139','were completed 139').replace('records.139','records. 139').replace('outstanding.139','outstanding. 139').replace('independent expanded','independent expanded')
  z=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',z).replace('aritra 1097','aritra1097').replace('captured.139','captured. 139').replace('snapshot:27','snapshot: 27')
  parts[i]=z
 return Paragraph(''.join(parts),styles[style])
def link(title,url):return '<link href="'+html.escape(url,quote=True)+'" color="#087F8C">'+html.escape(title)+'</link>'
def source(eid,title=None):
 e=rows[eid];return link(title or e['event_id'],e['source_urls'].split(';')[0])
def table(data,widths):
 styled=[[P(str(x),'headcell' if i==0 else 'cell') for x in row] for i,row in enumerate(data)]
 t=Table(styled,colWidths=widths,hAlign='LEFT',repeatRows=1)
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('LINEBELOW',(0,-1),(-1,-1),0.6,colors.HexColor('#C8D5DB'))]))
 return t
story=[]
def add(t,style='p'):story.append(P(t,style))
def heading(t):add(t,'h')
def newpage():story.append(PageBreak())

add('Police shootings and public parades after Bengal\'s 2026 government change','title')
add('A descriptive four-state comparison of detected Times of India cases<br/>Observation endpoint: 27 October 2026 (Indian event dates)','deck')
add('<b>The pipeline identifies three West Bengal shootings after alleged officer-gun-taking in the post-change window, versus none identified there before it.</b> This is an association in detected reporting. The current data do not identify an effect caused by BJP rule.')
heading('What the numbers measure')
add('A case is an event, not an article or a person. The main outcome requires a report that an accused took or attempted to take an officer\'s firearm and was then shot by state police. Fatal and nonfatal shootings are both eligible; the four qualifying events identified across the entire cohort happen to be fatal. Police accounts remain claims, not established facts or legal findings of extrajudicial killing.')
data=[['State','Pre: Jan2024-<br/>Apr2026<br/>(851 days)','Same season:<br/>Jun1-Oct27<br/>2025 (149 days)','Post: Jun1-<br/>Oct27 2026<br/>(149 days)']]
for st,name in [('WB','West Bengal'),('KL','Kerala'),('TN','Tamil Nadu'),('TG','Telangana')]:
 data.append([name,n(st,'gun_taking_police_shooting','pre_all'),n(st,'gun_taking_police_shooting','pre_season_2025'),n(st,'gun_taking_police_shooting','post_main')])
story.append(table(data,[128,120,130,125]));story.append(Spacer(1,9))
add('Every zero means no qualifying positive detected by this fixed pipeline; it does not mean no actual event occurred. The unequal pre/post durations are shown explicitly. May2026 is excluded from the main monthly fit because the government changed during that month.','small')
heading('The four main reported events')
data=[['Event date','State / event','Claim and source']]
for eid,date,label,note in [
 ('TG-2025-10-20-Nizamabad-Riyaz','20 Oct2025','Telangana / Nizamabad','Hospital custody; attempted/completed taking differs.'),
 ('WB-2026-07-08-Baruipur','8 Jul2026','WB / Baruipur','Crime-scene reconstruction; some early date wording conflicts.'),
 ('WB-2026-10-27-Gaighata','27 Oct2026*','WB / Gaighata','Reconstruction; overnight chronology requires caution.'),
 ('WB-2026-10-27-Shamsherganj','27 Oct2026*','WB / Shamsherganj','CID reconstruction; detailed report gives14:30.')]:
 data.append([date,label,source(eid,'TOI reporting')+'<br/>'+note])
story.append(table(data,[90,147,266]));story.append(Spacer(1,7))
add('*The paired October27 chronology is provisional; publication dates remain separate from event dates. One combined report describes both events. Repeated articles and variant spellings have been collapsed. The March2025 BSF border case is excluded from the state-police outcome.','small')

newpage()
add('A synthetic comparison with weak pre-period information','title')
add('West Bengal is compared with Kerala, Tamil Nadu and Telangana using only pre-change outcome histories to choose weights.','deck')
plot=BASE/'analysis/scm_gun_taking_police_shooting/actual_vs_synthetic.png'
story.append(Image(str(plot),width=472,height=243));story.append(Spacer(1,8))
add('Monthly detected cases per30 eligible days. October2026 includes27 days; May2026 is omitted. The displayed band spans weights compatible with the specified pre-fit rule. It is not a confidence interval, a causal bound, or an allowance for missed cases.','small')
heading('What the fit actually learns')
add('West Bengal has an all-zero detected pre-period. Kerala and Tamil Nadu also have all-zero pre histories, while Telangana has the October2025 Riyaz event. An exact match to West Bengal puts essentially zero weight on Telangana, but cannot distinguish any mixture of Kerala and Tamil Nadu. Each of those two donors can have any weight from0 to1. The central50/50 mixture is a computational tie-break, not a uniquely learned counterfactual.')
add('All three donors have zero detected cases in the post-period. Consequently every pre-fit-compatible mixture predicts zero there. West Bengal has three detected cases over149 days: <b>0.604 detected cases per30 days</b>, versus zero for the synthetic series. The pooled cumulative gap is three detected events. Its numerical stability across these weights does not establish causal identification.')
heading('Why this is not a BJP effect estimate')
add('The observed cluster motivated this exploratory comparison. There is one treated state, three selected donors and no informative treated pre-event pattern. Reporting intensity, political salience, police custody/reconstruction opportunities and lexical recall may change across time and states. No prisoner-transport or reconstruction denominator is available. Flat detected pre-counts do not establish comparable trends in underlying misconduct.')
add('No significance test is reported. With four state labels, a treatment-label rank comparison has only four possible ranks; exchangeability is not justified here. Better evidence would need comparable source ascertainment, independently checked event coding, longer informative histories, exposure denominators and a defensible untreated comparison group.')

newpage()
add('Public parades: three definitions give different counts','title')
add('The label must separate police action from private mobs, reconstruction from other escorts, and described clothing from unknown clothing.','deck')
data=[['Detected police event label','Pre: Jan2024-<br/>Apr2026','Post: Jun1-<br/>Oct27 2026','From May9-<br/>Oct27 2026']]
for outcome,label in [('police_public_parade_broad','Broad explicit police public parade'),('police_reconstruction_parade','Public parade explicitly linked to reconstruction'),('police_reconstruction_shirtless','Reconstruction plus explicitly shirtless')]:
 data.append([label,n('WB',outcome,'pre_all'),n('WB',outcome,'post_main'),n('WB',outcome,'post_transition_inclusive')])
story.append(table(data,[245,84,87,87]));story.append(Spacer(1,9))
add('For all three labels, Kerala, Tamil Nadu and Telangana have zero detected qualifying events in these windows. Those are pipeline counts, not proof of absence. The June-start broad count is four; including May adds Bonny/Roy and gives five.','small')
heading('The five identified West Bengal public-parade reports')
data=[['Date / subject','Clothing reported','Reconstruction explicit?']]
for eid,dt,name,clothing,recon in [
 ('WB-2026-05-28-Bijpur-Bonny-parade','28 May','Bonny/Roy','Sleeveless vest, Bermuda shorts, waist rope','No; police probe described'),
 ('WB-2026-06-11-Falta-Jahangir-parade','11 Jun','Jahangir Khan','White T-shirt and Bermuda shorts','Yes'),
 ('WB-2026-07-02-Jibantala-Saokat-parade','2 Jul','Saokat Molla','Not described','Yes'),
 ('WB-2026-07-18-Panihati-Tirthankar-parade','18 Jul','Tirthankar Ghosh','Not described','No; investigation described'),
 ('WB-2026-10-27-Behala-police-parade','27 Oct','Three Behala accused','Shirtless, barefoot, waist ropes','Yes')]:
 data.append([dt+'2026 / '+source(eid,name),clothing,recon])
story.append(table(data,[190,192,121]));story.append(Spacer(1,8))
add('Unknown clothing is not evidence that clothing was ordinary. It simply fails the strict reported-shirtless label. The separate October25 Behala naked parade was allegedly by relatives/associates; the October27 police parade concerns men accused in that earlier incident. The two episodes must not be merged.')
heading('A documented earlier example, and a capture warning')
add(link('TOI, Behror, Rajasthan (published23 September2019)','https://timesofindia.indiatimes.com/city/jaipur/rajasthan-cops-parade-13-in-underwear-in-public/articleshow/71251170.cms')+' describes thirteen accused taken through public streets in innerwear, barefoot, on Sunday22 September2019. The superintendent of police explicitly described recreation of the crime scene. This is one episode involving thirteen people, and establishes that the reconstruction-and-underclothing narrative predates the2026 Bengal cluster; no party attribution is inferred here.')
add('External reporting describes Howrah police reconstruction parades around24-25 May2026, with episode identity/date uncertainty. These are outside this fixed TOI-derived panel and are not added to its counts: a completed pipeline remains an incomplete event census.','small')

newpage()
add('How to read this comparison','title')
heading('Political exposure and control selection')
add('Treatment means a BJP chief minister in office on the event date. The official oath date for West Bengal is9 May2026. This definition differs from BJP cabinet participation, central influence, alliance membership or a BJP-appointed governor. The BSF sensitivity event therefore remains separate from state-police outcomes.')
add('Kerala, Tamil Nadu and Telangana form a transparent feasibility subset of states without a BJP chief minister, not the full universe of states where BJP has never been in power. Cabinet histories and alliances require separate coding. Tamil Nadu and Kerala also had non-BJP government turnovers in May2026 (Vijay on10 May; V.D. Satheesan on18 May). They remain donors under the stated BJP-CM definition, but those contemporaneous changes can affect comparability.')
heading('What was completed, and what remains unknown')
add('A symmetric URL screen selected1,132 unique TOI article IDs from the public sitemap inventory; all had available headline, date and body metadata. The independent expanded firearm/taking, reconstruction and parade screen flagged245 articles, all of which received AI source-context review. Repeated reports were joined into event records, and actual event geography and state/central/private actors were separated. There are no unread positive-signal candidates.')
add('An independent AI agent read a stratified random48 available low-signal bodies (12 per state; seed20261027): no visible missed target shooting or underclothed reconstruction parade was found. One sampled body appeared truncated. A further seven-report synonym sensitivity check found no additional qualifying gun-taking shooting. These checks are not a human gold standard, measured recall, or assurance that unlisted, differently worded or missing news was captured.139 explicit recommendation tails were removed while raw bodies were retained.')
add('The comparison therefore concerns <b>confirmed positive reports detected by a fixed, incomplete measurement process</b>. It does not estimate real-event incidence, whether police accounts are true, whether a shooting was legally justified, or a causal effect of BJP government. Source-context review and subagent agreement are disclosed AI assistance; independent human verification remains outstanding.')
heading('Sources and reproducibility')
refs=[
 ('Government dates',link('West Bengal oath, PMO/PIB','https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259319&lang=1&reg=3')+'; '+link('Tamil Nadu Governor','https://lokbhavan.tn.gov.in/')+'; '+link('Kerala oath, PMO','https://www.pmindia.gov.in/en/news_updates/pm-congratulates-shri-vd-satheesan-ji-on-taking-oath-as-the-chief-minister-of-keralam/')+'; '+link('Telangana chief minister','https://www.telangana.gov.in/government/chief-minister/')),
 ('Main event evidence',source('WB-2026-07-08-Baruipur','Baruipur')+'; '+source('WB-2026-10-27-Gaighata','Gaighata')+'; '+source('WB-2026-10-27-Shamsherganj','Combined October27 report')+'; '+source('TG-2025-10-20-Nizamabad-Riyaz','Nizamabad/Riyaz')),
 ('Additional parade evidence',link('Howrah reconstruction reports, Indian Express','https://indianexpress.com/article/cities/kolkata/howrah-police-public-parade-accused-controversy-10708947/')+'; '+link('Howrah date check, India Today','https://www.indiatoday.in/amp/india/west-bengal/story/akash-singh-howrah-police-reconstruction-underwear-political-row-2916439-2026-05-24')),
 ('Methods',link('Abadie (2021), Synthetic Controls','https://www.aeaweb.org/articles?id=10.1257%2Fjel.20191450')+'; '+link('Conley and Taber, few policy changes','https://www.nber.org/papers/t0312')),
]
for title,body in refs:add('<b>'+title+':</b> '+body,'source')
add('Reproduce from event_coding/event_ledger.csv; analysis/detected_case_window_counts.csv; analysis/scm_gun_taking_police_shooting/{summary.json,trajectory.csv,weight_bounds.csv}; and this generating Python file. The synthetic plot uses those saved actual analysis outputs; no illustrative or simulated event observations are substituted. Full URLs, publication dates and date qualifications remain in the event ledger.','small')
add('Public research repository: '+link('aritra1097/toi-police-practices-research','https://github.com/aritra1097/toi-police-practices-research')+'. Research snapshot:27 October2026; TOI publication times just after midnight28 October IST can precede the retrieval endpoint in New York. Event-window inclusion uses event dates.','small')

def footer(canvas,doc):
 canvas.saveState();w,h=A4
 canvas.setStrokeColor(colors.HexColor('#C8D5DB'));canvas.line(46,41,w-46,41)
 canvas.setFont('Body',8);canvas.setFillColor(GRAY)
 canvas.drawString(46,28,'Detected reported cases | Descriptive comparison | AI-assisted provisional coding')
 canvas.drawRightString(w-46,28,str(doc.page));canvas.restoreState()
doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=46,leftMargin=46,topMargin=44,bottomMargin=51,title='Detected police practices: Bengal and three comparison states',author='AI-assisted research for Aritra Basu')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
manifest={'pdf':str(OUT),'source_inputs':{str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BASE/'event_coding/event_ledger.csv',BASE/'analysis/detected_case_window_counts.csv',BASE/'analysis/scm_gun_taking_police_shooting/summary.json',plot]},'interpretation':'Detected positive reports conditional on fixed incomplete pipeline; no causal BJP effect identified.'}
(HERE/'report_manifest.json').write_text(json.dumps(manifest,indent=2))
print(OUT)
