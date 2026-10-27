"""One-coder AI case review. Re-run to reconcile hand-coded events to live cohort.

Source bodies remain in the private acquisition file. No article body text is
republished here. Unreviewed records are not treated as negative events.
"""
from pathlib import Path
import json,csv,collections,datetime as dt,re
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'collection/output/article_review_cohort_private.jsonl'
articles=[]
for line in SOURCE.read_text().splitlines():
 try:articles.append(json.loads(line))
 except json.JSONDecodeError:pass # Ignore incomplete trailing streaming record.
byid={r['article_id']:r for r in articles}
events=[]
def event(eid,date,state,locality,subjects,kind,force,jurisdiction,gun_claim,taking,outcome,deaths,reconstruction,parade,clothing,ids,notes,date_quality='reported_event_date',in_scope=True):
 present=[str(i) for i in ids if str(i) in byid]
 if not present:return
 events.append(dict(event_id=eid,event_date_ist=date,date_quality=date_quality,state_actual=state,locality=locality,subjects=subjects,event_kind=kind,force=force,force_jurisdiction=jurisdiction,gun_taking_claim=gun_claim,taking_claim_stage=taking,police_shooting_outcome=outcome,reported_deaths=deaths,custodial_reconstruction_or_recovery=reconstruction,police_parade=parade,clothing=clothing,primary_four_state_scope=int(in_scope),source_article_ids=';'.join(present),source_urls=';'.join(byid[i]['URL'] for i in present),source_publication_dates=';'.join(byid[i].get('publication_date','') for i in present),notes=notes,reviewer='AI_assistant',review_status='one_coder_provisional_source_review_not_human_verified'))

event('WB-2026-07-08-Baruipur','2026-07-08','West Bengal','Suryapur/Baruipur','Prabash/Prabhas/Prabhash/Probhas Mondal','fatal_police_shooting','Baruipur/Canning police','state_police','yes_police_claim','attempted_or_completed_reports_differ','fatal',1,'yes','no','not_applicable',[132272311,132252905,133740020,132748334,132395952,132266227,132267429,132266613,132259399,132254344,134268046,132315840,132272170,132270120,132263449],'One event despite many reports. July8 supported by chargesheet report and HC account nightJuly7/earlyJuly8. Detailed July9 article internally says Tuesday and Wednesday. Initial report says attempted; detailed report says completed. Political comments do not independently verify gun-taking.')
event('WB-2026-10-27-Gaighata','2026-10-27','West Bengal','Gaighata/Bongaon, North24Parganas','Prahlad Das','fatal_police_shooting','Gaighata police','state_police','yes_police_claim','completed_claimed','fatal',1,'yes','no','not_applicable',[135223012,135237727,135245318],'One event. Times vary 02:30,02:50,03:00-03:30 across reporting. Sources outside this cohort sometimes say Mondaynight; retain date uncertainty. October28 publication is distinct from October27 event.','reported_event_date_with_midnight_conflict')
event('WB-2026-10-27-Shamsherganj','2026-10-27','West Bengal','Shamsherganj/Samserganj/Dhuliyan, Murshidabad','Samiul/Samaul/Samayun/Samaun Sheikh','fatal_police_shooting','West Bengal CID','state_police','yes_police_claim','attempted_or_completed_reports_differ','fatal',1,'yes','no','not_applicable',[135245318],'Combined article gives 14:30 Oct27 and describes attempt to seize firearm; general opening describes guns being snatched. Do not count publicationOct28 as eventdateOct28.')
event('TG-2025-10-20-Nizamabad-Riyaz','2025-10-20','Telangana','Nizamabad Government General Hospital','Shaik/Sk Riyaz','fatal_police_shooting','Nizamabad police/City Armed Reserve','state_police','yes_police_claim','attempted_or_completed_reports_differ','fatal',1,'no_hospital_custody','no','not_applicable',[124702391,124728472,124858171,124714340],'One event. Police articles differ over attempted versus completed rifle seizure and firing. Family disputes account. Followup says six chest shots. Not crime-scene reconstruction. Party association alone does not determine truth.')
event('WB-2025-03-07-Khalpara-BSF','2025-03-07','West Bengal','Khalpara, Rajganj, Jalpaiguri','Mohammad Al Amin; group of border crossers','fatal_security_force_shooting','Border Security Force','central_force','yes_force_claim','attempted_group_seizure','fatal',1,'no_border_patrol','no','not_applicable',[118806741],'Broader-force sensitivity only. Report says group attempted weapon taking; cannot attribute act specifically to the man killed. Exclude from accused-in-state-police-custody reconstruction estimand.','inferred_Friday_before_Saturday_publication')
event('WB-2025-01-15-Goalpokhar-escape','2025-01-15','West Bengal','Panjipara/Goalpokhar, UttarDinajpur','Sajjak/Sajjak Alam','escape_and_police_injury','West Bengal police escorts','state_police','unresolved_in_initial_report','weapon_source_unknown','no_accused_fatality_in_this_escape',0,'no_prison_transport','no','not_applicable',[117274157,117288390],'Initial report cannot determine gun source; followup117288390 says hidden in blanket. Retain original uncertainty and later clarification. Later encounter death is separate linked event.')
event('WB-2025-01-18-Chopra-Alam','2025-01-18','West Bengal','Chopra, UttarDinajpur','Sajjak Alam','fatal_police_shooting','West Bengal police','state_police','not_established_by_reviewed_followup','unknown','fatal',1,'no_later_manhunt','no','not_applicable',[117402811],'HC followup confirms encounter death but does not establish immediate gun-snatching. DateJan18 derives separately verified primary TOI article117362643, not available in this acquisition snapshot; primary body needs joining.','external_primary_report_date_pending_cohort_join')
event('WB-2025-07-01-Gede-BSF','2025-07-01','West Bengal','Gede Halderpara BOP, Krishnaganj, Nadia','Unidentified suspected Bangladeshi smuggler','fatal_security_force_shooting','Border Security Force32Battalion','central_force','not_reported_in_reviewed_body','own_or_unspecified_gunfire_claim','fatal',1,'no_border_patrol','no','not_applicable',[122210056],'Report describes border crossers firing first; no taking of force weapon reported. Body absence is narrative absence, not independent proof no gun-taking occurred.','inferred_Tuesday_before_Wednesday_publication')
event('WB-2026-07-23-Malda-fratricide','2026-07-23','West Bengal','Baishnabnagar BSF camp, Malda','Ajay Kumar Singh; Ambadar Suresh Durgu; shooterShivamMishra','fratricide','Border Security Force','central_force','not_reported_in_reviewed_body','not_applicable','fatal_colleagues_not_accused',2,'no','no','not_applicable',[132588793],'Exclude target: BSF member shooting colleagues after argument, not accused taking police gun.')
event('TG-2025-07-20-Sriganesh-attack','2025-07-20','Telangana','Near RTC Hospital, Hyderabad','MLA N Sriganesh; unidentified attackers','attempted_weapon_taking_without_police_shooting','MLA security gunman','security_jurisdiction_not_established','yes_complainant_claim','attempted_group_seizure','no_police_shooting_reported',0,'no','no','not_applicable',[122804732],'Exclude fatal target. MLA alleges crowd attempted to take security gunman weapon. Date inferred Sunday before Monday publication.','inferred_weekday_before_publication')
event('TN-2026-03-16-Madhavaram-Ganesh','2026-03-16','Tamil Nadu','Madhavaram/Manjampakkam, Chennai','R Ganesh/DilliGanesh/ThoppaiGanesan','fatal_police_shooting','Chennai police','state_police','not_reported_in_reviewed_body','sickle_attack_claim','fatal',1,'no_arrest_attempt','no','not_applicable',[129599260],'Police describe sickle assault, not seizure of police firearm. Retrospective list of four other encounters must not be counted as new2026events.')
event('TN-2025-03-26-Taramani-Irani','2025-03-26','Tamil Nadu','Taramani MRTS,Chennai','JafferGulamHussainIrani','fatal_police_shooting','Chennai police','state_police','not_reported_in_reviewed_body','own_concealed_pistol_claim','fatal',1,'yes_vehicle_property_recovery','no','not_applicable',[119577022,119559380],'Sources describe a pistol concealed in a motorcycle used in civilian chain snatchings. This is not a claim of taking a police firearm. One shooting despite followup reported from Thane; actual shooting state Tamil Nadu.')
event('TN-2026-01-27-Perambalur-Raja','2026-01-27','Tamil Nadu','Near Thirumandurai, Perambalur','C Azhagu Raja/KottaiRaja','fatal_police_shooting','TamilNadu police','state_police','not_reported_in_reviewed_body','concealed_bomb_and_blade_claim','fatal',1,'yes_weapon_recovery','no','not_applicable',[127647427,127638821],'Two articles same event. Claimed retrieved hidden bomb and blade assault; no police-gun-taking narrative in reviewed bodies.')
event('TN-2026-07-10-Veeravanallur-Ajith','2026-07-10','Tamil Nadu','Veeravanallur forest/canal, Tirunelveli','Krishnan/Ajith','nonfatal_police_shooting','Tirunelveli police','state_police','not_reported_in_reviewed_body','sickle_attack_claim','nonfatal_leg_injury',0,'no_arrest_attempt','no','not_applicable',[132319530,132305051],'Two articles same event. Accused injured and arrested; police allege sickle assault. Do not count as death.')
event('TN-2026-07-18-Thirumudivakkam-Tamilazhagu','2026-07-18','Tamil Nadu','Kavanur/Thirumudivakkam,Chennai','Karuppu/Tamilazhagu','nonfatal_police_shooting','Thirumudivakkam police','state_police','not_reported_in_reviewed_body','concealed_sickle_recovery_claim','nonfatal_ankle_injury',0,'yes_weapon_recovery','no','not_applicable',[132519425,132499549],'Same Saturday-night event in two reports; police allege sickle attack during weapon recovery. No police-gun-taking claim in reviewed bodies.','inferred_Saturday_before_dated_reports')
event('TG-2026-06-30-ORR-Srikanth','2026-06-30','Telangana','BonguluruGate,HyderabadORR','BhusmiSrikanth','nonfatal_police_shooting','Nalgonda police','state_police','not_reported_in_reviewed_body','knife_and_stick_attack_claim','nonfatal_leg_injury',0,'no_arrest_attempt','no','not_applicable',[132110180],'Suspect from AndhraPradesh but actual shooting in Telangana; police allege knife and stick attack.','inferred_Tuesday_before_Wednesday_publication')
event('TN-2025-08-07-Tirupur-Manikandan','2025-08-07','Tamil Nadu','UpparuStream,Chikkanur,Gudimangalam','MManikandan','fatal_police_shooting','Gudimangalam police','state_police','not_reported_in_reviewed_body','concealed_sickle_recovery_claim','fatal',1,'yes_weapon_recovery','no','not_applicable',[123154744],'Police allege suspect used recovered sickle to assault officers, then was shot in forehead. No police-firearm seizure claim in reviewed body.')
event('TN-2025-07-29-Pappakudi-teen','2025-07-29','Tamil Nadu','Rasthavanur/Pappakudi,Ambasamudram,Tirunelveli','Shanmughasundaram;minorcompanion','nonfatal_police_shooting','Pappakudi police','state_police','not_reported_in_reviewed_body','machete_attack_claim','nonfatal_chest_injury',0,'no_patrol_response','no','not_applicable',[122982535,122983294],'Two reports one event; one young man shot and both detained. Distinguish chest injury from fatal shooting.','inferred_Tuesday_before_Wednesday_publication')
event('TN-2025-03-31-Madurai-Bose','2025-03-31','Tamil Nadu','Viraganur,Madurai','SubashChandraBose','fatal_police_shooting','Madurai city police','state_police','not_reported_in_reviewed_body','own_pistol_and_billhook_claim','fatal',1,'no_vehicle_interception','no','not_applicable',[119880690,119820636],'Police report suspect carrying private pistol and billhook; family disputes shooting. Not a police-weapon seizure account.','inferred_Monday_before_Tuesday_publication')
event('TN-2025-03-24-Madurai-Moovendran','2025-03-24','Tamil Nadu','Madurai crime scene','MMoovendran','nonfatal_police_shooting','Perungudi police','state_police','not_reported_in_reviewed_body','knife_attack_claim','nonfatal_leg_injury',0,'yes_scene_inquiry','no','not_applicable',[119440116],'Police allege knife attack during scene visit; no police-firearm seizure claim.','inferred_Monday_before_Tuesday_publication')
event('TN-2025-03-21-Guindy-Maharaja','2025-03-21','Tamil Nadu','GuindyRaceCourse,Chennai','Maharaja/HighCourtMaharaja','nonfatal_police_shooting','Chennai police','state_police','not_reported_in_reviewed_body','own_concealed_pistol_claim','nonfatal_below_knee_injury',0,'yes_vehicle_recovery','no','not_applicable',[119315257],'Suspect allegedly pulled privately concealed pistol when taken to recover bike; not taking police gun.','inferred_Friday_before_Saturday_publication')
event('TN-2025-11-29-Coimbatore-three','2025-11-29','Tamil Nadu','Kavundampalayam/Coimbatore','Threeunnamedburglarysuspects','police_shooting_with_delayed_death','Coimbatore police','state_police','not_reported_in_reviewed_body','attack_claim_mechanism_unspecified','one_fatal_two_nonfatal',1,'unknown','no','not_applicable',[125965814],'Retrospective summary reports three shot onNov29; one diedNov30. One event, not three. Requires dedicated initial report before complete broad-event denominator.')
event('TN-2025-12-12-Trichy-Rajasekar','2025-12-12','Tamil Nadu','Trichy','KRajasekar','nonfatal_police_shooting','Coimbatore police specialteam','state_police','not_reported_in_reviewed_body','knife_attack_claim','nonfatal_leg_injury',0,'no_arrest_attempt','no','not_applicable',[125965814],'Separate event mentioned in summary; police team basedCoimbatore but arrest/shooting reported inTrichy. Date derived from arrest reference; verify dedicated source.','reported_arrest_date_used_provisionally')
event('TN-2025-11-03-Coimbatore-three','2025-11-03','Tamil Nadu','Coimbatore','Sathish;Guna;Karthik','nonfatal_police_shooting','Coimbatore police','state_police','not_reported_in_reviewed_body','circumstances_not_supplied','nonfatal_hospitalised',0,'unknown','no','not_applicable',[125072455],'Three persons shot and arrested in one reported event. Body gives no further shooting circumstances; unresolved mechanism.','inferred_Monday_before_Tuesday_publication')
event('TN-2010-02-16-Madurai-two','2010-02-16','Tamil Nadu','Near Madurai checkpost','Murugan/Kallumandaiyan;Kaviarasu/Kaviarasan','retrospective_fatal_police_shooting','Police team led by ACP S Velladurai','state_police','not_reported_in_reviewed_body','police_attack_claim_disputed','fatal',2,'disputed_custody','no','not_applicable',[125807686],'2025 report concerns2010 incident and later criminalcase. Exclude2024-26 incidence; preserve retrospective evidence.')
event('AP-2003-Zaheerabad-retrospective','2003','Andhra Pradesh','Zaheerabad; currently Telangana','Unnamed suspect','retrospective_fatal_police_shooting','Undivided AndhraPradesh police','state_police','yes_police_claim','completed_claimed','fatal',1,'unknown','no','not_applicable',[124264609,124267491],'Two2025HCfollowups ofone2003event. HistoricaljurisdictionundividedAndhraPradesh,currentgeographyTelangana. Reportshighcourtupheldexonerationandpoliceprotectionoflifeclaim; donotcodethecaseasprovenillegal. Excludefrom2024-26incidence.','year_only_in_reviewed_body',False)
event('WB-2026-10-27-Behala-police-parade','2026-10-27','West Bengal','KhudiramPally/Manasatala,Sarsuna,Behala','Three accused relatives/associate in earlier mob parade','police_public_parade','Kolkata police','state_police','no_target_claim','not_applicable','no_shooting',0,'yes_claimed_reconstruction','yes','shirtless_barefoot_ropes_around_waist_semi_naked_reported',[135245410,135229430],'Distinct from antecedentOct25mobparade. ReportsOct27andOct28refer samepoliceevent; threepeopleoneparadeevent. Initialarticlegeneralisationwithoutclothes refinedbydetailedarticle.')
event('WB-2026-10-25-Behala-mob-parade','2026-10-25','West Bengal','Sarsuna,Behala','18yearold youth;father;19yearoldfriend','mob_public_parade','Privatefamily/associates','private_actors','no_target_claim','not_applicable','no_police_shooting',0,'no','no','naked_at_gunpoint_reported',[135243300,135219213,135211948],'Exclude policeparadeoutcome. Related antecedent toOct27policeparade; do not collapse actors or dates.','inferred_Sunday_from_dated_reports')
event('WB-2026-05-28-Bijpur-Bonny-parade','2026-05-28','West Bengal','Kanchrapara/Bijpur','AbhijitRoy/Bonny','police_public_parade','WestBengal police','state_police','no_target_claim','not_applicable','no_shooting',0,'probe_only_reconstruction_not_explicit','yes','sleeveless_vest_Bermuda_shorts_rope_around_waist',[131374883],'ArticlementionsadditionalearlierparadesincludingMondayMay25 but insufficientdetailtodistinguishall; currentrowcountsMay28only. Nevercountheadlineasfullynaked.')
event('WB-2026-07-02-Jibantala-Saokat-parade','2026-07-02','West Bengal','Jibantala,Canning','SaokatMolla','police_public_parade','Jibantala police','state_police','no_target_claim','not_applicable','no_shooting',0,'yes','yes','not_described',[132141546,132241992],'Police describe investigative reconstruction and deny publicdisplaypurpose. Crowdabuse reported. No clothingclaim established.')
event('WB-2026-07-18-Panihati-Tirthankar-parade','2026-07-18','West Bengal','Sodepur/Panihati','TirthankarGhosh/Puchida','police_public_parade','WestBengal police','state_police','no_target_claim','not_applicable','no_shooting',0,'investigation_reconstruction_not_explicit','yes','not_described',[132481039],'Saturday dateequalspublicationday; crowdchantsreported. No stripping or clothingclaim established.')
event('WB-2026-10-13-Jangipara-mob-parade','2026-10-13','West Bengal','Jangipara,Hooghly','JaydebSil/BabluSil','party_worker_public_parade','BJPworkers/supporters','private_party_actors','no_target_claim','not_applicable','no_police_shooting',0,'no','no','rope_around_waist_no_nudity_claim',[134920981],'Exclude policeparadeoutcome because identifiedactorsarepartyworkers; politicalidentityaloneisnotstatepoliceaction.')
event('TG-2025-03-15-CM-parade-threat','2025-03-15','Telangana','State legislative assembly','CM ARevanthReddy statement concerning online critics','threatened_public_parade','ChiefMinister speech','state_executive_speech','no_target_claim','not_applicable','no_shooting',0,'no','threat_only_not_observed','stripping_threatened',[119055370],'Non-BJP control has explicit stripping/parading threat by chief minister. This is a speech, not proof of an implemented parade. Keep separate from actual police public-parade event outcome.','inferred_Saturday_before_Sunday_publication')
event('WB-2025-03-01-Panagarh-Yadav-reconstruction','2025-03-01','West Bengal','PanagarhNH19','BabluYadav','ordinary_crime_reconstruction','Kanksa police','state_police','no_target_claim','not_applicable','no_shooting',0,'yes','no_coercive_public_parade_claim','black_full_sleeved_shirt_black_pants_slippers',[118653306,118667677],'Pre-treatment ordinary reconstruction with crowd gathered; normal clothing explicitly described. Do not classify every public scene visit as humiliating parade.')
event('WB-2026-06-11-Falta-Jahangir-parade','2026-06-11','West Bengal','Falta/Sahararhat, South 24 Parganas','Jahangir Khan','police_public_parade','West Bengal police with CAPF escorts','state_police_with_central_escort','no_target_claim','not_applicable','no_shooting',0,'yes','yes','white_T_shirt_Bermuda_shorts',[131656577],'Headline describes parading; body describes investigative reconstruction with ordinary T-shirt and shorts. No claim police stripped him. One escorted event; central escort does not establish who ordered it.')
event('TN-2024-05-02-Foreshore-private-assault','2024-05-02','Tamil Nadu','Foreshore Estate, Chennai','Manivannan; accused constable Gopinath and three other men','private_road_rage_assault_with_police_member','Armed Reserve constable and private associates; traffic police alleged bystanders','private_action_by_serving_officer_not_custodial_police_operation','no_target_claim','not_applicable','no_shooting',0,'no','no_formal_police_parade','shirt_removed_during_chase_and_assault',[109828827],'Counterexample for broad police-member involvement in public stripping: serving constable among private road-rage attackers. Do not label state custodial parade. Police arrested and suspended constable. Thursday before Saturday publication.','inferred_Thursday_before_Saturday_publication')
event('TN-2024-07-14-Madhavaram-Thiruvengadam','2024-07-14','Tamil Nadu','Madhavaram/Puzhal Vegetarian Nagar, Chennai','K Thiruvengadam','fatal_police_shooting','Chennai police','state_police','not_reported_in_reviewed_body','own_hidden_unlicensed_pistol_claim','fatal',1,'yes_weapon_recovery_then_escape','no','not_applicable',[111741044,111739045,111737061,111723967,116481625],'One event across initial and court followup reports. Initial says attack during recovery; detailed accounts say escaped at toilet stop and used private hidden pistol at later hideout. No taking of officer firearm reported.')
event('TN-2024-09-18-Perambur-Balaji','2024-09-18','Tamil Nadu','P and T quarters, Perambur/Vyasarpadi, Chennai','Kakkathope Balaji','fatal_police_shooting','Chennai police','state_police','not_reported_in_reviewed_body','own_country_made_gun_claim','fatal',1,'no_vehicle_chase','no','not_applicable',[113467327,113467328,113440994],'Three reports one event. Police claim private firearm fired during vehicle chase; no officer firearm seizure reported. Early and detailed versions vary in times and officer identities.')
event('TN-2024-09-23-ECR-Raja','2024-09-23','Tamil Nadu','Buckingham Canal near ISKCON, Chennai ECR','Seizing Raja','fatal_police_shooting','Chennai police','state_police','not_reported_in_reviewed_body','own_buried_gun_recovery_claim','fatal',1,'yes_weapon_recovery','no','not_applicable',[113630572],'Name Seizing is not a gun-seizure claim: police say he dug up concealed gun and fired during recovery. Monday before Tuesday publication.','inferred_Monday_before_Tuesday_publication')
event('TN-2024-10-04-Dindigul-Sachin','2024-10-04','Tamil Nadu','Malapatti crematorium, Dindigul','Richard Sachin/Sarchin','nonfatal_police_shooting','Dindigul police','state_police','not_reported_in_reviewed_body','concealed_billhook_or_sickle_recovery_claim','nonfatal_right_leg_injury',0,'yes_weapon_recovery','no','not_applicable',[113940448,113929904],'Two reports one event; police claim attack with recovered civilian murder weapon. Not taking officer firearm.')
event('TN-2024-12-09-Perambur-Arivalagan','2024-12-09','Tamil Nadu','Panathoppu/Perambur, Chennai','Arivalagan','nonfatal_police_shooting','Chennai police','state_police','not_reported_in_reviewed_body','own_illegal_firearm_claim','nonfatal_below_right_knee',0,'no_arrest_attempt','no','not_applicable',[116149380],'Police say suspect bought illegal gun in Bihar for35000 and opened fire; no taking police firearm. Monday before Tuesday publication.','inferred_Monday_before_Tuesday_publication')
event('TN-2024-06-28-Mamallapuram-Sathya','2024-06-28','Tamil Nadu','Near Mamallapuram/Pazhaveli, Chengalpet','Sirkazhi Sathya','nonfatal_police_shooting','Chengalpet police','state_police','not_reported_in_reviewed_body','machete_attack_claim','nonfatal_below_knee',0,'yes_scene_visit_to_find_associates','no','not_applicable',[111352735],'Police allege machete attack; a pistol recovered from suspects separately is not officer firearm-taking. Suspect BJP affiliation is distinct from governing party. Friday before Saturday publication.','inferred_Friday_before_Saturday_publication')
event('TG-2024-09-05-Kothagudem-six','2024-09-05','Telangana','Neeladrigutta/Mothe forest, Bhadradri Kothagudem','Six alleged Maoists including Lacchanna and Tulsi','fatal_counterinsurgency_shooting','Greyhounds and district police','state_police','not_reported_in_reviewed_body','insurgent_owned_firearms_claim','fatal',6,'no_forest_combing','no','not_applicable',[113106572,113105589,113082970],'Three reports same event; police claim return fire during combing and recover insurgents weapons. Separate Chhattisgarh encounters are background. No immediate seizure of force gun in reviewed bodies.')

event('TN-2024-03-07-Tirunelveli-Pechidurai','2024-03-07','Tamil Nadu','Thirupudaimarudur,Tirunelveli','K Pechidurai','police_shooting_with_later_hospital_death','Tirunelveli district police','state_police','not_reported_in_reviewed_body','sickle_attack_claim','hospital_death_March11_cause_pending_postmortem',1,'no_arrest_attempt','no','not_applicable',[108416738],'Shot in leg onThursdayMar7; hospitaldeathMondayMar11; cause expressly pending postmortem. Do not assume legshot causeddeath. Gun-taking lexical match in raw text came from recommendation tail.','shooting_date_inferred_Thursday_before_March12_report')
article_events=collections.defaultdict(list)
for e in events:
 for aid in e['source_article_ids'].split(';'):article_events[aid].append(e['event_id'])
exclusions={
 '132269201':'retrospective historical overview; quoted generic1970saccounts cannot supplydated2024-26events',
 '116803983':'civilian cricketfight andgoldchain theft; firearmalsoappearsbutnopoliceseizure',
 '113605220':'landgrabbingandseizedillegalweapons; no takingofpolicefirearm inretrievedcontext',
 '124676882':'Riyaz antecedent constable-stabbing story; chain-snatching criminalhistory plusknife, not takingpolicefirearm',
 '124658327':'Same antecedent constable-stabbing report; habitualchain-snatchingnotpoliceweaponseizure',
}
for aid in ['134799632','131580351','130961175','127492164']:
 exclusions[aid]='Parade Ground place-name or facility reference, not publicparadingofaccused'
for aid in ['133810361','133189926','131700251','131700247','131470911','127565739','127417586','126491546','123738759','123325514','122354166']:
 exclusions[aid]='Military/civicpassingoutorceremonialparade; not coercive publicparadingofaccused'
for aid in ['131687296','129785892','128824032','125469367','125328476','125004065','124794535','124585659','120355016','119610404']:
 exclusions[aid]='Testidentificationparade; not publichumiliationparade'
for aid in ['132630820','130498702']:
 exclusions[aid]='Elephantparading case; nothumanaccused'
for aid in ['128521028','122801109']:
 exclusions[aid]='Rumblestriptrafficfeature; notclothingremoval'
for aid in ['130128681','130121065']:
 exclusions[aid]='Metaphoricalstrippingofvotingrights; notclothingremoval'
for aid in ['118104385','133771553','112769834']:
 exclusions[aid]='Victimnudityorevidentiaryclothing; notpoliceparadingofaccused'
exclusions.update({'117211725':'MedicationstripseizureinBSFreport; noaccusedparade','126512440':'Politicalpresentationofvotersmarkeddead; notpoliceparade','126359611':'PlasticstripusedinATMtheft; notclothing','124480627':'Roadcrashdeathofheadconstable; nopoliceparade','123542696':'CelebrityIndiaDayParade; nocoercivepoliceparade'})
for aid in ['132812649','125771837','119819877','108089377','133619089']:
 exclusions[aid]='Civilian assault or murder weapon recovered by police; not taking a police firearm'
for aid in ['129478757','118632696','108839635','132590843']:
 exclusions[aid]='Officer self-inflicted shooting or suspected suicide, not accused taking police firearm'
for aid in ['123704568']:
 exclusions[aid]='Police officer allegedly shot parents with own service firearm; not an accused-seizes-police-gun encounter'
for aid in ['130253911','122800027','120558709','117529592','112971504','111389926','108416195']:
 exclusions[aid]='Weapon possession, recovery, transport security, or civilian crime context; no target taking-of-police-firearm or police-parade narrative in reviewed contexts'
for aid in ['118692149','112179584','134941899']:
 exclusions[aid]='Ordinary or planned investigation/reconstruction; no coercive public parade or police shooting established'
for aid in ['120670561','117157609','107096161']:
 exclusions[aid]='Central BSF border firing account with no force-weapon-taking claim in reviewed body; excluded narrow state-police mechanism'
for aid in ['120497341']:
 exclusions[aid]='Actual police warning shots/arrest in Jharsuguda Odisha, not West Bengal despite suspects linked to Murshidabad'
for aid in ['115149070']:
 exclusions[aid]='Border suspect died after being found in river; no gun-taking or shooting cause established'
for aid in ['112412410']:
 exclusions[aid]='Alleged police threats occurred in Dhaka Bangladesh, not West Bengal'
for aid in ['112091639','107788772','134925459']:
 exclusions[aid]='Sports or shooting competition; recommendation tails are not incident evidence'
for aid in ['110662247']:
 exclusions[aid]='Political threat about future encounters, not an observed event'
for aid in ['117866238','117854737','117841785']:
 exclusions[aid]='Suspect fired privately purchased/concealed weapon; police overpowered him, not suspect taking officer firearm'
# Context review of expanded signals in final 1,132 article snapshot.
for aid in ['132318614','132109123','120529792','113695728','108030825','107929933','107806311','129664736','129618059']:
 exclusions[aid]='Reviewed weapon/taking context concerns civilian crime, private firearm possession, police seizure, or non-police assailants; no target police-firearm-taking or custodial public-parade claim in reviewed text'
for aid in ['131808221','125620919','125066532','116378112','116354625','110256484','108862491','108909123']:
 exclusions[aid]='Reviewed shooting context concerns officer suicide, accident, funeral gun salute, or private family violence; not accused taking officer firearm'
for aid in ['125427912','125419959','125403171','121346996','121328490','117361541']:
 exclusions[aid]='Actual encounter geography is Andhra Pradesh or Chhattisgarh, not Telangana despite dateline, victims origin, or regional context'
for aid in ['121165671']:
 exclusions[aid]='Multi-day anti-Maoist operation along Chhattisgarh-Telangana border; exact state-event allocation unresolved, no custody/officer-firearm-taking claim in reviewed body; excluded narrow mechanism outcome'
for aid in ['123051081','122323076','112775523']:
 exclusions[aid]='Historical retrospective outside2024-26 and/or actual incident outside four target states; not a new target event'
for aid in ['123131196','121009059']:
 exclusions[aid]='Police killed by assailants; no accused killed after taking officer firearm; May2025 report expressly denies weapons looting'
for aid in ['122788463','122402748','112388625','109854534','108720615','108316170','108313422']:
 exclusions[aid]='Custodial death/torture allegation or investigation, without target firearm shooting or implemented public-parade claim in reviewed text; outside narrow outcomes'
for aid in ['119988446']:
 exclusions[aid]='Accidental service-weapon discharge during cleaning; injured colleague from flying tile, not accused taking officer firearm'
for aid in ['118768296','118653146','118611353','116407925','116397450','116225519','116183519','116086868','116086856','115982142','115947340','115909907','115818169','115815294','115392007','114988355','114597005','109385824','109280343','107594261']:
 exclusions[aid]='Reviewed parade context is captive elephants or temple festival regulation, not public parading of accused'
for aid in ['118074491','117465984','117437185','117338528','110670434','110545359']:
 exclusions[aid]='Reviewed parade context is planetary alignment, not police action'
for aid in ['117562162','117533510','117529417','117497947','117497895','117491635','116403684','115634852','114329503','114041210','113827287','112536418','112452828','111028992','108476045','108249717','107572445','107276184','107177998','107097423','107097316','106972286','106744914','124217713']:
 exclusions[aid]='Reviewed parade/shooting context is a military, school, cultural, commemorative, sports or civic ceremony; not coercive accused parade'
for aid in ['117276909','117138366']:
 exclusions[aid]='Reviewed parade context is unauthorised political procession or student ceremonial welcome; police are not parading criminal accused'
for aid in ['116261876']:
 exclusions[aid]='Bengal-origin workers stripped by private mob in Sundargarh Odisha; police rescued them, not WB police-parade event'
for aid in ['114821038','111589589']:
 exclusions[aid]='Test identification parade, not public humiliation parade'
for aid in ['112574464']:
 exclusions[aid]='Actual incident Lucknow Uttar Pradesh, officer family murder-suicide; Krishnanagar keyword is not WB geography'
for aid in ['111199083','111184253']:
 exclusions[aid]='Warning shots/mobile-phone-snatching suspects escape unhurt or mob-control context; not officer-firearm-taking fatality or police public parade'
for aid in ['110855488']:
 exclusions[aid]='Death of dogs in animal facility custody; not human police encounter'
for aid in ['110324865']:
 exclusions[aid]='Complainant arrived voluntarily in underwear after alleged domestic violence; police did not strip or parade him'
for aid in ['109828330']:
 exclusions[aid]='2024 chargesheet about2023 Wayanad gunbattle; private insurgent weapons and arrests, no taking police firearm or death established'
for aid in ['109208551']:
 exclusions[aid]='Attempted self-immolation near police station, not police firearm shooting'
for aid in ['108216073','108134427']:
 exclusions[aid]='Student stripped by other students in alleged ragging; police investigate, not custodial police-parade event'
for aid in ['107161732']:
 exclusions[aid]='Private mob stripped and paraded teenager in Sangareddy; police rescued him, not police implemented public parade'

exclusions.update({'112819233':'Custody chest-pain death with disputed detention; no shooting claim in main article; reconstruction term was recommendation contamination','110283478':'RTI penalty against fire officer; firearm term was recommendation contamination','108358874':'Officer suicide report; firearm term was recommendation contamination','107159012':'Fear of future encounter and retrospective2023 shooting, not a new2024 target event; other-state firearm content was recommendation contamination'})
weapon_rx=re.compile(r'\b(?:guns?|rifles?|pistols?|revolvers?|firearms?|weapons?|carbines?|arms)\b',re.I)
taking_rx=re.compile(r'\b(?:snatch\w*|grab\w*|wrest\w*|disarm\w*|overpower\w*|seiz\w*|tak\w*|took|taken)\b',re.I)
log=[];unresolved=[]
for r in articles:
 aid=r['article_id']
 body=re.split('We also published the following articles recently',r.get('analysis_body',r.get('articleBody','')),flags=re.I)[0]
 weapon=bool(weapon_rx.search(body) and taking_rx.search(body))
 reconstruction=bool(re.search('reconstruc|re.enact|recreat',body,re.I))
 parade=bool(r.get('body_parade_or_stripping_flag'))
 expanded=weapon or reconstruction or parade
 if aid in article_events:status='mapped_to_event_ledger'
 elif aid in exclusions:status='reviewed_signal_context_exclusion'
 elif expanded:status='target_signal_not_yet_reviewed';unresolved.append(r)
 else:status='deterministic_no_target_signal_not_validated_negative'
 log.append(dict(article_id=aid,URL=r['URL'],publication_date=r.get('publication_date',''),headline=r.get('article_headline',''),case_review_status=status,event_ids=';'.join(article_events.get(aid,[])),exclusion_reason=exclusions.get(aid,''),expanded_weapon_taking_flag=int(weapon),expanded_reconstruction_flag=int(reconstruction),expanded_parade_flag=int(parade),expanded_any_target_signal=int(expanded),retrieval_weapon_flag=r.get('body_weapon_taking_context_flag',''),retrieval_parade_flag=r.get('body_parade_or_stripping_flag','')))


# Positive source labels only. False means not meeting this strict reported label;
# it does not establish real-world absence of the underlying act.
for e in events:
 current='2024-01-01' <= e['event_date_ist'] <= '2026-10-27'
 state_scope=e['state_actual'] in ['West Bengal','Kerala','Tamil Nadu','Telangana']
 state_force=e['force_jurisdiction']=='state_police'
 claimed=e['gun_taking_claim']=='yes_police_claim'
 shot=e['police_shooting_outcome']=='fatal' or e['police_shooting_outcome'].startswith('nonfatal')
 main=bool(current and state_scope and state_force and claimed and shot)
 broad=bool(current and state_scope and e['police_parade']=='yes' and e['force_jurisdiction'] in ['state_police','state_police_with_central_escort'])
 recon=e['custodial_reconstruction_or_recovery'] in ['yes','yes_claimed_reconstruction']
 shirtless=e['clothing'].startswith('shirtless_')
 e['main_reported_gun_taking_then_police_shot']=int(main)
 e['main_fatal_subset']=int(main and e['police_shooting_outcome']=='fatal')
 e['main_nonfatal_subset']=int(main and e['police_shooting_outcome'].startswith('nonfatal'))
 e['secondary_reported_police_public_parade_broad']=int(broad)
 e['secondary_reported_reconstruction_public_parade']=int(broad and recon)
 e['secondary_reported_reconstruction_shirtless_police_parade_strict']=int(broad and recon and shirtless)
 e['strict_label_zero_interpretation']='no_matching_reported_label_not_proven_real_world_absence'

ROOT.mkdir(parents=True,exist_ok=True)
def save(name,rows):
 with (ROOT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['article_id']);w.writeheader();w.writerows(rows)
save('event_ledger.csv',events);save('article_coding.csv',log)
save('unresolved_context_candidates.csv',[dict(article_id=r['article_id'],URL=r['URL'],publication_date=r.get('publication_date',''),headline=r.get('article_headline',''),weapon_flag=r.get('body_weapon_taking_context_flag'),parade_flag=r.get('body_parade_or_stripping_flag')) for r in unresolved])
(ROOT/'event_ledger.json').write_text(json.dumps(events,indent=2))
summary=dict(snapshot_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),cohort_articles=len(articles),cohort_distinct_ids=len(byid),events_in_ledger=len(events),mapped_articles=sum(x['case_review_status']=='mapped_to_event_ledger' for x in log),reviewed_exclusion_articles=sum(x['case_review_status']=='reviewed_signal_context_exclusion' for x in log),unresolved_flagged_articles=len(unresolved),deterministic_no_target_signal=sum(x['case_review_status']=='deterministic_no_target_signal_not_validated_negative' for x in log),expanded_target_signal_articles=sum(x['expanded_any_target_signal'] for x in log),scope='case finding snapshot, not a complete event census; unreviewed records are not negative',coder='AI assistant one-coder source review; not human verified')
(ROOT/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
