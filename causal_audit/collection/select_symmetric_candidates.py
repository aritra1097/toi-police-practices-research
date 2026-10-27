"""Symmetric URL retrieval for a four-state exploratory measurement cohort.

This selects reports for body review. URL slugs and lastmod timestamps are not
headlines, publication dates, events, or causal outcomes. Geography is provisional.
"""
from pathlib import Path
import csv,gzip,json,re,collections,hashlib,datetime

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]/'scraping/sitemap_output/sitemap_url_inventory.csv.gz'
CACHED=ROOT.parents[1]/'scraping/sitemap_output/selected_article_metadata.jsonl'
GAZETTEER={
 'West Bengal':{
  'city_desks':['kolkata','calcutta','siliguri','darjeeling','asansol','durgapur'],
  'place_phrases':['west bengal','bengal','kolkata','calcutta','howrah','hooghly','hugli','siliguri','darjeeling','jalpaiguri','cooch behar','coochbehar','alipurduar','dinajpur','raiganj','malda','maldah','murshidabad','berhampore','nadia','krishnanagar','24 parganas','barasat','basirhat','bongaon','gaighata','baruipur','canning','barrackpore','bidhannagar','asansol','durgapur','burdwan','bardhaman','birbhum','bolpur','bankura','purulia','midnapore','medinipur','jhargram','lalgarh','nandigram','singur','kharagpur','tamluk','haldia','balurghat','chopra','goalpokhar','samserganj','shamsherganj']},
 'Kerala':{
  'city_desks':['thiruvananthapuram','kochi','kozhikode','thrissur','kannur','kollam','kottayam','palakkad','alappuzha','malappuram','kasaragod'],
  'place_phrases':['kerala','thiruvananthapuram','trivandrum','kochi','cochin','ernakulam','kozhikode','calicut','thrissur','trichur','kannur','cannanore','kollam','quilon','kottayam','palakkad','palghat','alappuzha','alleppey','malappuram','kasaragod','kasargod','pathanamthitta','idukki','wayanad','varkala','nedumangad','attingal','neyyattinkara','aluva','alwaye','perumbavoor','angamaly','muvattupuzha','kothamangalam','thodupuzha','changanassery','pala','thalassery','tellicherry','payyannur','kanhangad','kondotty','tirur','ponnani','manjeri','sulthan bathery','kalpetta','mannarkkad','ottapalam','shoranur','chalakudy','irinjalakuda','kodungallur','kunnamkulam']},
 'Tamil Nadu':{
  'city_desks':['chennai','coimbatore','madurai','trichy','salem','erode','tirupur','vellore','tuticorin','tirunelveli'],
  'place_phrases':['tamil nadu','tamilnadu','chennai','madras','coimbatore','madurai','trichy','tiruchirappalli','tiruchi','salem','erode','tirupur','tiruppur','vellore','tuticorin','thoothukudi','tirunelveli','nagercoil','kanyakumari','hosur','thanjavur','tanjore','kumbakonam','cuddalore','villupuram','viluppuram','kanchipuram','kancheepuram','chengalpet','chengalpattu','kallakurichi','tiruvarur','nagapattinam','dharmapuri','krishnagiri','namakkal','karur','ariyalur','perambalur','pudukkottai','ramanathapuram','sivaganga','virudhunagar','tenkasi','ranipet','tirupattur','nilgiris','ooty','udhagamandalam','mettupalayam','tindivanam','tiruvannamalai','thiruvannamalai','dindigul','theni','avadi','tambaram']},
 'Telangana':{
  'city_desks':['hyderabad','warangal','nizamabad','karimnagar','khammam','nalgonda','ramagundam','mahbubnagar','adilabad'],
  'place_phrases':['telangana','hyderabad','secunderabad','cyberabad','rachakonda','warangal','hanamkonda','nizamabad','karimnagar','khammam','nalgonda','ramagundam','mahbubnagar','mahabubnagar','adilabad','bhadradri','bhadrachalam','sangareddy','siddipet','suryapet','miryalaguda','mancherial','nirmal','kamareddy','medchal','shamshabad','vikarabad','wanaparthy','narayanpet','jagtial','jagitial','jangaon','mahabubabad','bhuvanagiri','bhongir','sircilla','medak','bhupalpally','mulugu','asifabad','jogulamba','gadwal','yadadri','peddapalli','nagarkurnool','rangareddy','ranga reddy','sathupally']}
}
PATTERNS={
 'encounter':r'\b(?:encounters?|gunfights?|gunbattles?|shootouts?|crossfire)\b',
 'police':r'\b(?:police\w*|cops?|constables?|officers?|custody|custodial|stf|crpf|bsf|cisf|security forces|task force)\b',
 'shoot_or_death':r'\b(?:shot|shoot\w*|gunned|firing|fire[ds]?|kill\w*|dead|death\w*|dies?|died|bullets?|gunshot\w*|wound\w*)\b',
 'weapon':r'\b(?:guns?|pistols?|revolvers?|rifles?|firearms?|weapons?|arms|carbines?)\b',
 'taking':r'\b(?:snatch\w*|grab\w*|wrest\w*|disarm\w*|overpower\w*)\b',
 'parade':r'\b(?:parade[ds]?|parading)\b',
 'stripping':r'\b(?:strip(?:ped|ping|s)?|naked|underwear|undergarments?|boxers?|chaddi)\b',
 'reconstruction':r'\b(?:reconstruction|reconstruct\w*|crime scene)\b'
}
RX={k:re.compile(v,re.I) for k,v in PATTERNS.items()}
PLACES={s:re.compile(r'\b(?:'+'|'.join(re.escape(x) for x in g['place_phrases'])+r')\b') for s,g in GAZETTEER.items()}
DESKS={city:s for s,g in GAZETTEER.items() for city in g['city_desks']}
ARTICLE=re.compile(r'/(?:amp_)?articleshow/(\d+)\.cms')

def main():
 ROOT.mkdir(parents=True,exist_ok=True)
 cache={json.loads(line)['article_id']:json.loads(line) for line in CACHED.read_text().splitlines() if line.strip()}
 selected={};n=0;article_rows=0;core_n=0
 with gzip.open(SOURCE,'rt',newline='') as f:
  for row in csv.DictReader(f):
   n+=1;url=row['URL'];aid=row.get('article_id','')
   if not aid or not ARTICLE.search(url):continue
   article_rows+=1
   text=re.sub(r'[^a-z0-9]+',' ',url.lower().split('indiatimes.com',1)[-1]).strip()
   encounter=bool(RX['encounter'].search(text));police=bool(RX['police'].search(text));outcome=bool(RX['shoot_or_death'].search(text))
   taking=bool(RX['taking'].search(text) and RX['weapon'].search(text))
   core=encounter or (police and outcome)
   parade=bool(RX['parade'].search(text))
   stripping=bool(RX['stripping'].search(text) and (police or RX['reconstruction'].search(text)))
   if not(core or taking or parade or stripping):continue
   core_n+=int(core)
   city=re.search(r'/city/([^/]+)/',url);desk=city[1] if city else '';deskstate=DESKS.get(desk,'')
   states=[];evidence={}
   for state,pattern in PLACES.items():
    hits=sorted(set(m.group() for m in pattern.finditer(text)))
    if hits or deskstate==state:
     states.append(state);evidence[state]=dict(city_desk=desk if deskstate==state else '',place_phrase_hits=hits)
   if not states:continue
   if aid not in selected:
    selected[aid]=dict(article_id=aid,URL=url,state_candidates=[],geography_evidence={},routes=[],source_sitemap_lastmod=row.get('sitemap_lastmod',''),source_sitemap=row.get('sitemap_source',''),source_inventory_retrieved_at_utc=row.get('retrieved_at_utc',''),cached_metadata_available=aid in cache,headline='',publication_date='',event_state_verified=False)
   item=selected[aid]
   item['state_candidates']=sorted(set(item['state_candidates'])|set(states))
   item['geography_evidence'].update(evidence)
   item['routes']=sorted(set(item['routes'])|({'encounter'} if encounter else set())|({'police_shoot_or_death'} if police and outcome else set())|({'weapon_taking'} if taking else set())|({'parade'} if parade else set())|({'stripping_police_or_reconstruction'} if stripping else set()))
   if aid in cache:item['headline']=cache[aid]['article_headline'];item['publication_date']=cache[aid]['publication_date']
 records=sorted(selected.values(),key=lambda x:(x['source_sitemap_lastmod'],x['article_id']),reverse=True)
 (ROOT/'symmetric_candidates.json').write_text(json.dumps(records,indent=2,ensure_ascii=False))
 (ROOT/'gazetteer_and_patterns.json').write_text(json.dumps(dict(gazetteer=GAZETTEER,patterns=PATTERNS,notes=['Cities and explicit phrases provide provisional retrieval geography, never verified incident location.','Articles may match multiple states. Body review must assign actual incident state and exclude references to origin/residence, unrelated mentions, and reporting desks.','Puducherry and Andhra Pradesh are not controls; Hyderabad-desk reports may concern Andhra Pradesh and require explicit exclusion after body review.','All four states use identical event-language patterns. New acquisition has corrected fire[ds]?|firing, avoiding the earlier WB pilot fir*→first false positive.','No candidate count, URL lastmod, or recovered metadata denominator is an incidence measure.']),indent=2))
 summary=dict(source_inventory=str(SOURCE),source_inventory_rows=n,article_url_rows=article_rows,national_core_candidate_url_rows=core_n,distinct_selected_article_ids=len(records),multi_state_candidate_article_ids=sum(len(x['state_candidates'])>1 for x in records),cached_selected_article_ids=sum(x['cached_metadata_available'] for x in records),new_http_requests_required=sum(not x['cached_metadata_available'] for x in records),state_counts={s:dict(distinct_candidate_article_ids=sum(s in x['state_candidates'] for x in records),core_candidate_article_ids=sum(s in x['state_candidates'] and any(a in x['routes'] for a in ['encounter','police_shoot_or_death']) for x in records),weapon_taking_candidate_article_ids=sum(s in x['state_candidates'] and 'weapon_taking' in x['routes'] for x in records),parade_candidate_article_ids=sum(s in x['state_candidates'] and 'parade' in x['routes'] for x in records),stripping_police_reconstruction_candidate_article_ids=sum(s in x['state_candidates'] and 'stripping_police_or_reconstruction' in x['routes'] for x in records),cached_metadata=sum(s in x['state_candidates'] and x['cached_metadata_available'] for x in records)) for s in GAZETTEER},created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Predeclared feasibility subset KL/TN/TG plus WB, not exhaustive never-BJP states. Symmetric URL-selected article review cohort only; not full state news or event coverage. Party-history comparator eligibility must be separately verified. Parade route includes ceremonial/mob false positives requiring body exclusions.')
 (ROOT/'candidate_counts.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
