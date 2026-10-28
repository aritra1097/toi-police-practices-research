"""Readable plan and incident-date government validation packet, no raw bodies."""
from pathlib import Path
import csv,datetime as dt,html,json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'targeted_history'
OUT=ROOT/'output/pdf/Bengal_Research_Next_Steps_and_Governments.pdf';OUT.parent.mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader((DATA/'governments/evidence_with_governments.csv').open()))
ordinary_ids={x['event_id'] for x in csv.DictReader((DATA/'ordinary_crime_gun_reports.csv').open())}
assert len(rows)==41 and len(ordinary_ids)==14
REPO='https://github.com/aritra1097/toi-police-practices-research/blob/main/'
FONT=Path('/System/Library/Fonts/Supplemental/Arial.ttf');BOLD=FONT.with_name('Arial Bold.ttf')
if FONT.exists():
 pdfmetrics.registerFont(TTFont('Body',str(FONT)));pdfmetrics.registerFont(TTFont('BodyBold',str(BOLD)))
else:
 pdfmetrics.registerFont(TTFont('Body','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
 pdfmetrics.registerFont(TTFont('BodyBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
INK=colors.HexColor('#173C4D');TEAL=colors.HexColor('#087B88');GRAY=colors.HexColor('#53636C');LIGHT=colors.HexColor('#EEF4F6')
styles={
 'title':ParagraphStyle('title',fontName='BodyBold',fontSize=23,leading=27,textColor=INK,spaceAfter=10),
 'subtitle':ParagraphStyle('subtitle',fontName='Body',fontSize=11,leading=15,textColor=GRAY,spaceAfter=13),
 'h':ParagraphStyle('h',fontName='BodyBold',fontSize=12,leading=16,textColor=INK,spaceBefore=9,spaceAfter=5),
 'p':ParagraphStyle('p',fontName='Body',fontSize=10.3,leading=14.1,textColor=INK,spaceAfter=8),
 'small':ParagraphStyle('small',fontName='Body',fontSize=8.4,leading=11,textColor=GRAY,spaceAfter=6),
 'cell':ParagraphStyle('cell',fontName='Body',fontSize=8.5,leading=10.7,textColor=INK),
 'head':ParagraphStyle('head',fontName='BodyBold',fontSize=8.5,leading=10.7,textColor=colors.white),
}
def ascii_text(s):
 for a,b in [('—','-'),('–','-'),('‑','-'),('’',"'"),('‘',"'"),('“','"'),('”','"')]:s=s.replace(a,b)
 return s
def safe(s):return html.escape(ascii_text(str(s)))
def P(s,k='p'):return Paragraph(ascii_text(s),styles[k])
def link(label,url):return '<link href="'+html.escape(url,quote=True)+'" color="#087B88">'+safe(label)+'</link>'
story=[]
def add(s,k='p'):story.append(P(s,k))
def heading(s):add(s,'h')
def date_label(value):
 if '/' in value:
  a,b=value.split('/',1)
  if a[:7]==b[:7]:return str(int(a[8:]))+'-'+str(int(b[8:]))+' '+dt.datetime.strptime(a,'%Y-%m-%d').strftime('%b %Y')
 try:return dt.datetime.strptime(value,'%Y-%m-%d').strftime('%d %b %Y').lstrip('0')
 except ValueError:
  try:return dt.datetime.strptime(value,'%Y-%m').strftime('%b %Y')
  except ValueError:return value or 'Date qualified'
short={
 'KA-2001-12-14-Pampanagar-Deepika-case-pair':'Deepika-case pair; fatal / group allegation',
 'UK-2009-07-03-Dehradun-Ranbir-Singh':'Ranbir Singh; fatal / disputed encounter',
 'UP-2015-03-16-Bareilly-Mehran-escort-escape':'Mehran; fatal / custody transport',
 'TG-2015-04-07-Alair-five-undertrials':'Alair five undertrials; terrorism-suspect transport',
 'KA-2015-08-16-NIMHANS-Vishwanath':'Vishwanath; fatal / hospital armed standoff',
 'TG-2019-12-06-Chattanpally-Disha-four':'Disha four accused; fatal / scene investigation',
 'UP-2019-11-30-Kanpur-Ehtisham':'Ehtisham; nonfatal / custody escort',
 'UP-2020-07-09-Panki-Prabhat-Mishra':'Prabhat Mishra; fatal / transport',
 'UP-2020-07-10-Sachendi-Vikas-Dubey':'Vikas Dubey; fatal / transport',
 'DL-2021-07-13-Rohini-Sumit-Bagga':'Sumit Bagga; nonfatal / custody escort',
 'OD-2021-07-24-Simulia-Sheikh-Hyder':'Sheikh Hyder; fatal / prison transfer',
 'UP-2022-03-14-Ghaziabad-Kamal-Kallu':'Kamal/Kallu; nonfatal / chase after taking',
 'UP-2022-04-26-Gorakhpur-Alok-Paswan':'Alok Paswan; nonfatal / evidence recovery',
 'AS-2022-05-25-Kokrajhar-Afruddin-Islam':'Afruddin Islam; nonfatal / evidence recovery',
 'UP-2023-09-21-Noida-unnamed-rape-accused':'Unnamed Noida accused; nonfatal / evidence gathering',
 'BR-2023-10-16-Vaishali-Bittu-Satya-Prakash':'Bittu Kumar and Satya Prakash; fatal / transport',
 'WB_2012_Canning':'Canning rifle-taking; no accused-shot outcome',
 'WB-2000-03-20-Howrah-MohanSingh':'Mohan Singh; fatal / disputed crowd involvement',
 'WB_2008_Liluah':'Liluah bank robbery; ASI disarmed',
 'WB_2009_Bandih':'Farmer\'s civilian gun taken; insurgency context',
 'WB-2010-06-16_17-Salboni-Murmu':'Rameshwar Murmu media display; insurgency context',
 'WB-2010-08-23-DumDum':'Nine prisoners; alleged nude jail parade',
 'WB_2010_Palsanda':'Purna Chandra Ghosh; disputed crowd firing',
 'WB_2011_Bagula':'Rajeswari Mallick; disputed crowd firing',
 'WB-2011-12-16_17-CoochBehar-BSF':'BSF border confrontations; group-attribution limits',
 'WB-2014-06-27-Haridevpur':'Homeguard killed; police shooting suspect not reported',
 'WB_2015_Ganga':'Ganga Mahato; firearm-taking not stated',
 'WB_2019_Dulal':'Md Dulal; BSF group weapon-taking claim',
 'WB_2020_Kasem':'Kasem; BSF individual-attributed attempt',
 'WB-2021-04-10-Sitalkuchi-CISF':'Four CISF firing deaths; election crowd',
 'RJ-2019-09-22-Behror':'13 accused in innerwear; explicit reconstruction',
 'MP-2013-07-23_25-Sehore':'Sehore stripping/torture allegation in custody',
 'MP-2014-10-04-Bhopal-Anees':'Anees Khan; underwear court escort',
 'PB-2015-05-26-Chinkot':'Private assault allegation; constable on leave',
 'DL-2018-05-17-Inderpuri-Virender':'Virender; disputed naked police escort',
 'MH-2020-09-23-Jaripatka':'Nagpur innerwear parade; reconstruction not established',
 'RJ-2022-12-01-Kardhani':'Murder suspects; spot verification / clothes unknown',
 'RJ-2024-02-27-Pragpura':'Shooting suspects; spot verification / clothes unknown',
 'RJ-2025-01-Gudhagorji':'House-firing suspects; underwear / rationale unresolved',
 'RJ-2025-08-01-Merta':'Lottery-scam suspects; court escort in salwar suits',
 'RJ-2026-01-08-Chittorgarh':'Extortion suspects; spot verification / clothes unknown',
}
def government_label(x):
 cm=x['chief_minister'];gov=x['government_at_incident']
 if cm=='Mamata Banerjee':gov='AITC-led; Congress partner' if 'INC cabinet partner' in gov else 'AITC-led government'
 elif cm in ['Jyoti Basu','Buddhadeb Bhattacharjee']:gov='CPI(M)-led Left Front'
 elif cm=='Uddhav Thackeray':gov='Shiv Sena-led MVA (NCP, Congress)'
 elif cm=='Parkash Singh Badal':gov='SAD-led; BJP coalition partner'
 elif cm=='Nitish Kumar':gov='JD(U)-led; RJD and Congress alliance'
 elif cm=='Himanta Biswa Sarma':gov='BJP-led; AGP and UPPL partners'
 elif cm=='K. Chandrashekar Rao':gov='TRS government'
 elif cm=='Arvind Kejriwal':gov='AAP elected NCT government'
 return link(cm,x['government_sources'].split(';')[0])+'<br/>'+safe(gov)
def authority_label(x):
 a=x['institutional_authority'];force=x['reported_force']
 if x['state']=='Delhi':return 'Delhi Police / Union MHA<br/>Modi; BJP-led NDA'
 if a.startswith('Union_MHA'):
  label='CISF' if 'CISF' in force else 'BSF'
  label+=' / Union MHA<br/>'
  label+='Manmohan Singh; Congress-led UPA' if 'Manmohan' in x['union_government_when_central'] else 'Modi; BJP-led NDA'
  if 'ECI' in a:label+='<br/>ECI election supervision'
  return label
 if x['case_id']=='PB-2015-05-26-Chinkot':return 'Private assault allegation<br/>Constable on leave'
 if 'insurgency' in x['context'] or 'Maoist' in x['context']:return safe(force)+'<br/>Outside ordinary-crime main table'
 return safe(force)
def case_table(group):
 data=[[P('Event date / state','head'),P('Report to read','head'),P('Chief minister and government then','head'),P('Reported force / authority','head')]]
 for x in sorted(group,key=lambda z:z['government_date_display']):
  shown_date='4 or 6 Feb 2012' if x['case_id']=='WB_2012_Canning' else date_label(x['government_date_display'])
  first=safe(shown_date)+'<br/>'+safe(x['state'])
  data.append([P(first,'cell'),P(link(short.get(x['case_id'],x['case_name']),x['source_urls'].split(';')[0]),'cell'),P(government_label(x),'cell'),P(authority_label(x),'cell')])
 t=Table(data,colWidths=[79,143,153,128],repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#C7D4DA'))]))
 return t
add('Bengal research: next steps<br/>and governments at the time','title')
add('A source-checking packet | 27 October 2026 (New York date)','subtitle')
q=Table([[P('<b>Research question</b><br/>Did this particular police account occur previously in ordinary criminal cases in Bengal, and how closely do earlier cases resemble the recent ones?')]],colWidths=[503]);q.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#C7D4DA')),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.append(q)
heading('1. Finish Bengal\'s historical body review')
add('There are <b>255 usable Bengal-related candidate articles still awaiting full-body reading</b>. These are location/desk-screened reports, not 255 verified Bengal incidents. Read the bodies and separate ordinary crime, custody/reconstruction, border operations, crowds and insurgency.')
heading('2. Build the closest-comparison table')
add('For each relevant episode, record custody status, alleged firearm-taking, individual/group attribution, reconstruction, who was shot, outcome and incident date. Deduplicate repeated reports. Keep broader similarities and unresolved sources explicit.')
heading('3. Independently check the strongest matches')
add('Open the linked originals and check the coding yourself. Additional AI agreement is not human validation. Record corrections using the case ID, source URL and the passage that changes your assessment.')
heading('4. Reassess Bengal before and after May 2026')
add('Apply the same retrieval and coding to comparator states before estimating differences. Sparse or flat pre-period outcomes and changing coverage can leave synthetic comparisons poorly determined. The selected examples below are not an event-rate denominator.')
heading('How to read and validate this packet')
add('On the following pages, <b>case labels link to TOI reports</b> and <b>chief ministers link to government evidence</b>. Verify incident date separately from publication/update date; check who allegedly took whose gun, who fired, and whether reconstruction is stated. Government at the time is context, not proof of political instructions.','small')
add(link('Readable research findings',REPO+'targeted_history/FINDINGS.md')+' | '+link('Government table and detailed source audits',REPO+'targeted_history/governments/README.md')+' | '+link('Source-linked case catalogue',REPO+'targeted_history/evidence_table.csv'),'small')
add('Prepared by OpenAI Codex at Aritra Basu\'s direction. AI source-context coding remains provisional; police allegations are not independently established facts.','small')
story.append(PageBreak())
add('Ordinary-crime gun-taking reports','title')
add('14 selected historical event examples: eight report fatalities and six nonfatal shooting injuries. Individual/group and attempted/completed claims remain separate in the linked data.','subtitle')
story.append(case_table([x for x in rows if x['case_id'] in ordinary_ids]));story.append(Spacer(1,10))
add('Delhi is an important exception: the elected NCT government was AAP, while Delhi Police reported to Union authority. Historical party names are used: TRS in 2019, and Nitish Kumar\'s JD(U)-RJD-Congress alliance in October 2023. Date and timing uncertainties remain in the full CSV.','small')
story.append(PageBreak())
add('Bengal: related cases and exclusions','title')
add('14 catalogue entries across different settings. Insurgency, border forces, crowds and jail allegations are not pooled with individual ordinary-crime custodial shootings.','subtitle')
story.append(case_table([x for x in rows if x['state']=='West Bengal']));story.append(Spacer(1,10))
add('Canning: conflicting weekday statements imply 4 or 6 February 2012; both dates fall under the same AITC-INC government. BSF/CISF are central forces; Sitalkuchi also involves election supervision. Administrative authority is not a finding about who ordered firing.','small')
story.append(PageBreak())
add('Other practices and special contexts','title')
add('13 remaining entries: reconstruction/parade reports, broader alleged humiliation and two special firearm-taking contexts. These are deliberately different categories.','subtitle')
story.append(case_table([x for x in rows if x['state']!='West Bengal' and x['case_id'] not in ordinary_ids]));story.append(Spacer(1,10))
add('Punjab 2015: the allegation concerns a private attack involving a constable on leave, not an established official police operation. Maharashtra 2020 uses contemporary undivided Shiv Sena/NCP names. Source confidence and coalition qualifications are retained in the government ledger; no exhaustive cabinet history is asserted.','small')
add('Government tenure is primarily checked against official records; some party/coalition details use contemporaneous reporting or a mirrored government handbook. '+link('Open the complete CSV and source audits',REPO+'targeted_history/governments/README.md')+'.','small')
def footer(c,doc):
 c.setStrokeColor(colors.HexColor('#C7D4DA'));c.line(46,37,549,37)
 c.setFont('Body',7.5);c.setFillColor(GRAY);c.drawString(46,24,'TOI research | Incident-date governments | AI-assisted, provisional source coding')
 c.drawRightString(549,24,str(doc.page))
doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=46,leftMargin=46,topMargin=42,bottomMargin=50,title='Bengal research: next steps and historical state governments',author='OpenAI Codex, at Aritra Basu\'s direction')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
