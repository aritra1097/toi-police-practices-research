"""Join independently sourced incident-date governments; keep prior case CSV intact."""
from pathlib import Path
import csv,json,hashlib,html
R=Path(__file__).resolve().parent;BASE=R.parent
casefile=BASE/'evidence_table.csv';original_hash=hashlib.sha256(casefile.read_bytes()).hexdigest()
cases=list(csv.DictReader(casefile.open()));mappings={}
for name in ['national_spells.json','parade_spells.json']:
 x=json.loads((R/name).read_text())
 for z in x['event_mappings']:
  aid=z['event_id'];assert aid not in mappings,aid
  party=z['chief_minister_party_at_incident'];led=z.get('bjp_led_government','BJP' in party or 'Bharatiya Janata Party' in party)
  mappings[aid]=dict(chief_minister=z['chief_minister'],cm_party_at_incident=party,government_at_incident=z['government_at_incident'],government_date_display=z['event_date_ist'],government_date_basis=z.get('event_date_basis','source event date; see case date basis'),bjp_led_state_government=led,bjp_participation_note='BJP-led state government' if led else ('BJP coalition partner documented' if z.get('bjp_in_governing_coalition') else 'Not BJP-led; see dated government sources'),government_sources=';'.join(z['government_sources']),government_confidence=z['government_confidence'],reported_force=z['force_institution_as_reported'],institutional_authority=z.get('force_authority','respective state government for state police'),authority_note=z.get('uncertainty',z.get('force_review_basis','Government context does not establish political instructions.')),authority_sources=';'.join(z.get('force_authority_sources',[])),union_government_when_central=z.get('union_government_at_incident',''),government_input=name)
x=json.loads((R/'government_audit_wb.json').read_text())
for z in x['case_assignments']:
 aid=z['case_id'];assert aid not in mappings,aid
 date=z['frozen_input_event_date_ist'] or (z['government_date_start']+'/'+z['government_date_end'])
 institution=z['institutional_authority'];union='';authority_sources=[]
 if institution.startswith('Union_MHA'):
  if date[:4]<'2014':
   union='Manmohan Singh; Congress-led UPA'
   authority_sources=['https://www.pmindia.gov.in/en/former_pm/dr-manmohan-singh-2/','https://www.archivepmo.nic.in/drmanmohansingh/speech-details.php?nodeid=1025']
  else:
   union='Narendra Modi; BJP-led NDA';authority_sources=['https://www.pmindia.gov.in/en/pms-profile/']
 mappings[aid]=dict(chief_minister=z['state_chief_minister'],cm_party_at_incident=z['state_cm_party'],government_at_incident=z['state_government_coalition'],government_date_display=date,government_date_basis=z['government_date_basis'],bjp_led_state_government=z['state_BJP_led_at_incident'],bjp_participation_note='Not BJP-led; see dated government sources',government_sources=';'.join(z['source_urls']),government_confidence=z['government_assignment_confidence'],reported_force=z['force_or_institution'],institutional_authority=institution,authority_note=z['authority_note'],authority_sources=';'.join(authority_sources),union_government_when_central=union,government_input='government_audit_wb.json')
assert len(cases)==len(mappings)==41
assert {z['case_id'] for z in cases}==set(mappings)
rows=[dict(z,**mappings[z['case_id']]) for z in cases]
with (R/'evidence_with_governments.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
national_ids={z['event_id'] for z in csv.DictReader((BASE/'ordinary_crime_gun_reports.csv').open())}
with (R/'ordinary_crime_governments.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(z for z in rows if z['case_id'] in national_ids)
lines=['# State governments on the incident dates','',
 'This adds government context to all 41 reviewed case/context entries. The original evidence table is unchanged. Entries include different practices and exclusions; they are not a homogeneous outcome count.',
 '', 'Click a case name to read its TOI source. The chief minister links to government evidence. The CSV retains all sources, coalition qualifications, alternative dates and authority notes.',
 '', '**State government is not always the policing authority.** Delhi Police reports to the Union MHA; BSF and CISF are central forces, with separate election supervision for the Sitalkuchi deployment. Punjab 2015 is an alleged private assault involving a constable on leave. Government incumbency does not show who ordered an act.',
 '', '| Event date | State / case | Chief minister | Government then | Force / authority |','|---|---|---|---|---|']
for z in rows:
 def esc(s):return str(s).replace('|','/').replace('\n',' ')
 case='['+esc(z['case_name'])+']('+z['source_urls'].split(';')[0]+')'
 cm='['+esc(z['chief_minister'])+']('+z['government_sources'].split(';')[0]+')'
 authority=esc(z['reported_force'])
 if z['union_government_when_central']:authority+='; '+esc(z['union_government_when_central'])
 lines.append('| '+ ' | '.join([esc(z['government_date_display']),esc(z['state'])+' / '+case,cm,esc(z['government_at_incident']),authority])+' |')
lines += ['', '## How to validate', '',
 'Use the incident date rather than the article update date. Confirm the chief minister and party at that time, not the politician\'s later affiliation. Keep BJP leadership, coalition participation and Union authority separate. TRS is retained for Telangana in 2015/2019; Maharashtra 2020 uses the contemporary undivided Shiv Sena-led MVA; Bihar October 2023 is Nitish Kumar\'s JD(U)-led RJD/Congress alliance before the January 2024 NDA return.',
 '', 'Canning has conflicting weekday statements implying 4 or 6 February 2012. Both fall under the same AITC-INC government, so government assignment is stable while the incident date stays qualified.',
 '', 'Government tenure is primarily checked against official records. Some historical party/coalition details use contemporaneous reporting or a mirrored government handbook; each audit records its source type and limitations. No complete minister-by-minister cabinet history or causal party effect is asserted.',
 '', 'Detailed source audits: [national](national_spells.md), [West Bengal](government_audit_wb.md), [parades and Delhi authority](parade_spells.md). [Download the complete table](evidence_with_governments.csv).']
(R/'README.md').write_text('\n'.join(lines)+'\n')
assert hashlib.sha256(casefile.read_bytes()).hexdigest()==original_hash
manifest=dict(case_rows=len(rows),ordinary_crime_rows=len(national_ids),unmapped_ids=[],original_evidence_sha256=original_hash,government_input_sha256={name:hashlib.sha256((R/name).read_bytes()).hexdigest() for name in ['national_spells.json','parade_spells.json','government_audit_wb.json']},interpretation='Incident-date government/authority context only; not evidence of political direction or causation.')
(R/'join_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
