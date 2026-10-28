"""Read-only historical headline retrieval extension, not event or truth classification.

Uses manifest-canonical dated sources only. Baseline IDs reproduce analyze.py's
date + normalized-headline key. Different dates remain separate report records.
No HTTP requests, body retrieval, or edits to original inputs.
"""
from pathlib import Path
import argparse, collections, csv, datetime as dt, hashlib, json, re, unicodedata

ROOT = Path(__file__).resolve().parent
RESEARCH = ROOT.parent
DEFAULT_SOURCE = Path('local-input/Times_of_India_News_Headlines')
PATTERN_VERSION = 'historical-supplement-v1-2026-10-27'
PATTERNS = {
    'police': r'\b(?:police\w*|cops?|constables?|officers?|inspectors?|custod\w*|stf|ats|crpf|bsf|security forces|home ?guards?)\b',
    'suspect': r'\b(?:accused|suspects?|criminals?|gangsters?|undertrials?|prisoners?|convicts?|dacoits?|robbers?|rapists?|offenders?|miscreants?|thieves|thief|arrest\w*|detain\w*|culprits?|rowd\w*|goons?|molesters?|eve teasers?|eve teasing|peddlers?|chain snatchers?|smugglers?|burglars?|murderers?|extortionists?|fraudsters?|bookies|bootleggers?|cheats?|history sheeters?|steal\w*|stolen|theft|loot\w*|rob\w*|rape\w*|murder\w*|harass\w*|molest\w*|assault\w*)\b',
    'weapon': r'\b(?:guns?|pistols?|revolvers?|rifles?|fire ?arms?|weapons?|arms|carbines?|insas|ak ?47|service (?:gun|pistol|rifle|revolver|weapon))\b',
    'taking_expanded': r'\b(?:snatch\w*|grab\w*|wrest\w*|seiz\w*|disarm\w*|overpower\w*|steal\w*|stole|stolen|theft|loot\w*|rob\w*|tak\w*|took|taken|pull\w*|decamp\w*)\b',
    'weapon_escape': r'\b(?:flee\w*|fled|escap\w*|run\w* away|ran away|make\w* off|made off|walk\w* away)\b',
    'parade': r'\b(?:parad\w*|march\w*|perp walk\w*|procession\w*)\b',
    'underclothing': r'\b(?:naked|nude|nudity|semi ?nude|semi ?naked|half ?naked|undress\w*|uncloth\w*|underwear|underpants?|under ?garments?|innerwear|loincloth\w*|boxers?|briefs?|chadd\w*|kachch?ha\w*|panties|bras?|bare bod\w*|bare chest\w*)\b',
    'stripping': r'\b(?:strip\w*|disrob\w*|denud\w*)\b',
    'reconstruction': r'\b(?:reconstruct\w*|re enact\w*|reenact\w*|recreat\w*|crime scene|scene of crime)\b',
    'public_humiliation': r'\b(?:humiliat\w*|sham\w*|barefoot|tonsured?|shaved?|thrash\w*|beaten|beat\w* up|public\w*)\b',
    'ceremonial_or_identification_hint': r'\b(?:republic day|independence day|passing out|ceremon\w*|military|army day|flag march|march past|rehears\w*|recruit\w*|identification|identify\w*|identifi\w*|test identification|tip|gandhi jayanti|sports|beauty|fashion)\b',
}
RX = {k: re.compile(v, re.I) for k,v in PATTERNS.items()}
PRE = re.compile('|'.join(PATTERNS[k] for k in ('weapon','parade','underclothing','stripping')) + r'|\bbare[\W_]*(?:bod|chest)|\bperp[\W_]*walk', re.I)

def normalize(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', unicodedata.normalize('NFKC',s).lower())).strip()

def article_id(url):
    m=re.search(r'/(?:articleshow|photostory|videoshow|msid)[/-](\d+)|/(\d+)\.cms',url)
    return next((x for x in m.groups() if x), '') if m else ''

def key_for(date, text):
    return hashlib.blake2b((date+'|'+normalize(text)).encode(),digest_size=16).hexdigest()

def dump_csv(path, rows):
    fields=['id','date','date_type','headline','category','url','article_id','all_urls_json','all_article_ids_json','baseline_candidate','supplemental_candidate','retrieval_routes','review_priority','ceremonial_or_identification_hint','provenance_json']+list(PATTERNS)
    # Hint is both a regular signal and a convenience column; emit it once.
    fields=list(dict.fromkeys(fields))
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
        for row in rows:
            x=dict(row)
            for k in ('all_urls','all_article_ids','provenance'):
                if k in x:x[k+'_json']=json.dumps(x[k],ensure_ascii=False,separators=(',',':'))
            x['retrieval_routes']=';'.join(sorted(x.get('routes',[])))
            w.writerow(x)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=DEFAULT_SOURCE);p.add_argument('--out',type=Path,default=ROOT)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    started=dt.datetime.now(dt.timezone.utc).isoformat()
    manifest=json.loads((RESEARCH/'data/manifest.json').read_text())
    baseline={r['id']:r for r in csv.DictReader((RESEARCH/'data/candidates.csv').open())}
    selected=[];excluded=[]
    for m in manifest:
        if m.get('alias_of'):excluded.append({'file':m['file'],'reason':'byte-identical manifest alias','alias_of':m['alias_of']});continue
        if not m.get('min_date'):excluded.append({'file':m['file'],'reason':'no valid dated rows in audited manifest'});continue
        selected.append(m)
    matches={}; per_file=[]; cache={}; routes_raw=collections.Counter();flags_raw=collections.Counter()
    for m in selected:
        f=args.source/m['file'];stats=collections.Counter(); date_type='dataset_publish_date' if m['file'].startswith('india-news-headlines') else 'archive_listing_date'
        # Verify source bytes against the previously audited manifest before reading rows.
        h=hashlib.sha256()
        with f.open('rb') as stream:
            for block in iter(lambda:stream.read(2**20),b''):h.update(block)
        if h.hexdigest()!=m['sha256']:raise ValueError(f'Source hash changed: {m["file"]}')
        with f.open(newline='',encoding='utf-8-sig') as stream:
            for rowno,row in enumerate(csv.DictReader(stream),2):
                stats['rows']+=1
                if stats['rows']%500000==0:print(json.dumps({'progress_file':m['file'],'rows':stats['rows'],'unique_supplemental_matches_so_far':len(matches)}),flush=True)
                text=row.get('headline_text',row.get('Text','')).strip()
                if not text:stats['empty_headline']+=1;continue
                raw=row.get('publish_date',row.get('Date','')).strip()
                if not raw:stats['missing_date']+=1;continue
                try:
                    if raw not in cache:cache[raw]=dt.datetime.strptime(raw,'%Y%m%d' if len(raw)==8 and raw.isdigit() else '%d %b, %Y').strftime('%Y-%m-%d')
                    date=cache[raw]
                except ValueError:stats['invalid_date']+=1;continue
                stats['valid_dated_headline_rows']+=1
                if not PRE.search(text):continue
                norm=normalize(text);flags={k:int(bool(rx.search(norm))) for k,rx in RX.items()}
                firearm=flags['weapon'] and (flags['taking_expanded'] or (flags['weapon_escape'] and flags['police']))
                parade=flags['parade'] and any(flags[k] for k in ('police','suspect','underclothing','stripping','reconstruction','public_humiliation'))
                stripping=(flags['underclothing'] or flags['stripping']) and any(flags[k] for k in ('police','suspect','parade','reconstruction'))
                if not (firearm or parade or stripping):continue
                routes=[k for k,v in [('national_firearm_taking_expanded',firearm),('national_police_or_suspect_parade',parade),('national_underclothing_or_stripping',stripping)] if v]
                stats['matched_rows']+=1;routes_raw.update(routes);flags_raw.update(k for k,v in flags.items() if v)
                key=key_for(date,text);url=row.get('URL','').strip();aid=article_id(url);category=row.get('headline_category',row.get('City','')).strip()
                provenance=dict(file=m['file'],row_number_including_header=rowno,source_date=raw,date=date,date_type=date_type,category=category,url=url,article_id=aid)
                if key not in matches:
                    matches[key]=dict(id=key,date=date,date_type=date_type,headline=text,category=category,url=url,article_id=aid,all_urls=[],all_article_ids=[],baseline_candidate=int(key in baseline),supplemental_candidate=int(key not in baseline),routes=set(),provenance=[],**flags)
                out=matches[key];out['routes'].update(routes);out['provenance'].append(provenance)
                if date_type not in out['date_type'].split(';'):out['date_type']+=';'+date_type
                if url and url not in out['all_urls']:out['all_urls'].append(url)
                if aid and aid not in out['all_article_ids']:out['all_article_ids'].append(aid)
                if url and not out['url']:out.update(url=url,article_id=aid)
                for k,v in flags.items():out[k]=max(out[k],v)
        per_file.append(dict(file=m['file'],sha256=h.hexdigest(),date_type=date_type,**stats));print(json.dumps({'file_complete':per_file[-1],'unique_matches':len(matches)}),flush=True)
    for r in matches.values():
        r['review_priority']='high' if (r['weapon'] and r['police']) or (r['underclothing'] and (r['parade'] or r['police'] or r['reconstruction'])) else 'standard'
    supplemental=sorted((r for r in matches.values() if not r['baseline_candidate']),key=lambda r:(r['date'],r['headline']))
    all_matches=sorted(matches.values(),key=lambda r:(r['date'],r['headline']))
    dump_csv(args.out/'supplemental_candidates.csv',supplemental)
    dump_csv(args.out/'expanded_pattern_matches.csv',all_matches)
    combined={r['id']:r for r in all_matches}
    for key,b in baseline.items():
        if key in combined:combined[key]['routes'].add('baseline_original');continue
        urls=[b['url']] if b.get('url') else [];aids=[article_id(u) for u in urls if article_id(u)]
        prov=[]
        for src in b.get('provenance','').split('; '):
            name,number=src.rsplit(':',1);dtype='dataset_publish_date' if name.startswith('india-news-headlines') else 'archive_listing_date'
            prov.append(dict(file=name,row_number_including_header=int(number),date=b['date'],date_type=dtype,provenance_origin='baseline_candidates_csv'))
        combined[key]=dict(id=key,date=b['date'],date_type=';'.join(sorted({q['date_type'] for q in prov})),headline=b['headline'],category=b['category'],url=b['url'],article_id=aids[0] if aids else '',all_urls=urls,all_article_ids=aids,baseline_candidate=1,supplemental_candidate=0,routes={'baseline_original'},review_priority='baseline_review',provenance=prov)
    dump_csv(args.out/'combined_candidate_inventory.csv',sorted(combined.values(),key=lambda r:(r['date'],r['headline'])))
    counts=dict(pattern_version=PATTERN_VERSION,started_at_utc=started,finished_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),baseline_candidates=len(baseline),expanded_pattern_unique_date_headlines=len(matches),expanded_matches_already_in_baseline=sum(r['baseline_candidate'] for r in matches.values()),new_supplemental_candidates=len(supplemental),combined_candidates=len(combined),supplemental_with_article_id=sum(bool(r['article_id']) for r in supplemental),unique_article_ids_in_supplement=len({a for r in supplemental for a in r['all_article_ids']}),raw_route_matches=dict(routes_raw),raw_flag_matches=dict(flags_raw),unique_route_matches={k:sum(k in r['routes'] for r in matches.values()) for k in routes_raw},supplemental_route_matches={k:sum(k in r['routes'] for r in supplemental) for k in routes_raw},sources=per_file,excluded_sources=excluded,date_semantics={'dataset_publish_date':'Date supplied by main headline dataset; not independently verified against article metadata.','archive_listing_date':'Historical archive listing date; not actual publication or event date.'},limitations=['Retrieval flags are review prompts, not validated events or police mechanism claims.','Coverage remains that of the saved headline files; no headline-only search establishes body-level recall.','Date-headline duplicates are collapsed; reports on different dates and multiple articles about one incident remain separate.','Unmapped city desks and headline wording can conceal event geography.','No article bodies were fetched.'])
    (args.out/'audit_counts.json').write_text(json.dumps(counts,indent=2))
    (args.out/'retrieval_patterns_v1.json').write_text(json.dumps(dict(version=PATTERN_VERSION,patterns=PATTERNS,routes={'national_firearm_taking_expanded':'weapon AND (taking_expanded OR (weapon_escape AND police))','national_police_or_suspect_parade':'parade AND (police OR suspect OR underclothing OR stripping OR reconstruction OR public_humiliation)','national_underclothing_or_stripping':'(underclothing OR stripping) AND (police OR suspect OR parade OR reconstruction)'},ceremonial_policy='Retained and flagged; no automatic ceremonial/identification exclusion.',deduplication='BLAKE2b-128 of ISO source date + | + NFKC lowercase punctuation-to-space whitespace-collapsed headline; compatible with baseline analyze.py.',provenance='CSV record number including header, not physical line number when quoted cells contain newlines.'),indent=2))
    print(json.dumps({k:v for k,v in counts.items() if k not in ('sources','excluded_sources','limitations')},indent=2),flush=True)

if __name__=='__main__':main()
