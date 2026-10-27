# Political exposure audit

As of 27 October 2026. This is a coding audit, not an outcome analysis or a complete minister-by-minister history.

## Recommended definitions

1. **BJP-led state executive:** the chief minister belongs to BJP on the incident date. Code a time-varying state-day exposure. A BJP governor does not satisfy this definition. Treat President's Rule separately.
2. **BJP state cabinet participation:** at least one BJP politician holds a state ministerial portfolio on the incident date. This includes some governments whose chief minister belongs to another party.
3. **NDA/NEDA or electoral alliance:** a separate variable. An alliance or outside legislative support does not establish BJP state cabinet participation.

Do not call a no-BJP-chief-minister state a state where BJP has never been in power. Do not use a current party label for older incidents. Count state-police operations separately from BSF and other centrally controlled forces. The March 2025 Jalpaiguri BSF case is not a clean state-executive outcome.

Party affiliation means affiliation **while holding the relevant office**, not the politician's later affiliation. A former non-BJP chief minister joining BJP later does not retrospectively create a BJP government. BJP's predecessors, Janata Party governments, and regional parties are not automatically BJP under this definition; code any alternative ideological-family exposure separately.

## Candidate control universe

Among the 28 current states, the complete candidate set under **never a BJP chief minister through the as-of date** is Andhra Pradesh, Kerala, Meghalaya, Mizoram, Nagaland, Punjab, Sikkim, Tamil Nadu, and Telangana. This enumeration is corroborated by the current list of BJP chief ministers, whose never-held-office list additionally contains the Union Territories Jammu and Kashmir and Puducherry: https://en.wikipedia.org/wiki/List_of_chief_ministers_from_the_Bharatiya_Janata_Party . It is a secondary universe check, not a substitute for a complete primary government-spell dataset.

The accompanying CSV records primary evidence recovered and remaining audit limits. Never-BJP-cabinet claims are not established by this bounded audit. Andhra Pradesh, Meghalaya, and Nagaland have direct primary evidence of BJP ministers. Punjab's long SAD-BJP cabinet participation is well established but its primary historical minister record was not recovered in this bounded search. Sikkim and Mizoram have alliance/support histories that require cabinet-level checking before a strict never-participated coding.

Kerala, Tamil Nadu, and Telangana are useful proposed core controls under the chief-minister definition. Calling only these three the complete universe would be selection, so report them as a prespecified subset and explain geographic/data-coverage restrictions. A strict cabinet-free subset remains provisional until the minister histories are audited.

## Important dates and boundaries

- **West Bengal treatment onset: 9 May 2026.** PMO/PIB release explicitly dates Suvendu Adhikari's oath that day: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2259319&lang=1&reg=3 . Official state CM page: https://wb.gov.in/government-meet-the-chief-minister.aspx . The definition is BJP chief minister, not any central BJP influence before that date.
- **Bihar is not a never-BJP-CM control in 2026.** The official CM secretariat dates Samrat Choudhary's oath to 15 April 2026: https://cm.bihar.gov.in/users/home1.aspx . Historical BJP cabinet participation predates this change.
- **Tamil Nadu also changed government in May 2026**, to C. Joseph Vijay on 10 May. The Governor's official site records the oath: https://lokbhavan.tn.gov.in/ . This is not a BJP-led change. The historical Assembly list URL was discovered but timed out: https://www.assembly.tn.gov.in/history/cmlist.php . Current official government pages support Vijay's office: https://deg.tn.gov.in/ . Do not claim the historical list was successfully fetched in this audit.
- **Kerala also changed government in May 2026**, to V. D. Satheesan on 18 May. PMO dates the oath: https://www.pmindia.gov.in/en/news_updates/pm-congratulates-shri-vd-satheesan-ji-on-taking-oath-as-the-chief-minister-of-keralam/ . The state GAD page supplies the complete prior CM list and current officeholder: https://gad.kerala.gov.in/en/chief-ministers . Its Pinarayi end date of 4 May should not be used as a new-ministry start date. The intervening caretaker/transition must be distinguished if daily government identity is needed.
- **Telangana exists as a separate state only from 2 June 2014.** Official state portal: https://www.telangana.gov.in/ . First CM K. Chandrashekar Rao is confirmed by the official Khammam profile: https://khammam.telangana.gov.in/kcr-profile/ . Revanth Reddy is current CM: https://www.telangana.gov.in/government/chief-minister/ . A state record places him in the CM role on 7 December 2023: https://www.telangana.gov.in/gallery/2023/12/chief-minister-sri-a-revanth-reddy-visits-secretariat/ . Pre-2014 Hyderabad observations belong to undivided Andhra Pradesh; they are not zero Telangana-state observations.

## Direct primary evidence separating BJP leadership from BJP cabinet participation

- Andhra Pradesh: the official Sri Sathya Sai district representative table identifies Satya Kumar Yadav as BJP and Minister for Health, Family Welfare, and Medical Education: https://srisathyasai.ap.gov.in/public-representatives/ . The chief minister is TDP. Exclude AP from a never-BJP-cabinet control group.
- Meghalaya: official December 2019 press statement identifies A. L. Hek as BJP leader: https://meghalaya.gov.in/sites/default/files/press_release/Delegation_of_MDA.pdf . Official July 2019 notification explicitly lists him among cabinet ministers: https://meghalaya.gov.in/sites/default/files/circulars/23.07.19_4.pdf . Exclude Meghalaya from a never-BJP-cabinet group. The original official past-CM list at https://megassembly.gov.in/governors_chiefministers.htm returned 502 in this audit; current official CM profile is https://meghalaya.gov.in/shri-conrad-kongkal-sangma-1 .
- Nagaland: official legislative profile identifies Y. Patton as BJP and Deputy CM with Home portfolio from 2018: https://nla.nagaland.gov.in/shri-y-patton/ . Official complete CM history lists no BJP chief minister and records Rio's coalition with BJP: https://www.nagaland.gov.in/chief-ministers . Exclude Nagaland from a never-BJP-cabinet group.

## Additional primary histories and current checks

- Mizoram official district CM list with parties: https://dcserchhip.mizoram.gov.in/page/list-of-chief-ministers-governors-of-mizoram . Current CM Lalduhoma and ZPM affiliation: https://dipr.mizoram.gov.in/page/the-chief-minister . Current office is corroborated by an August 2026 Governor release: https://rajbhavan.mizoram.gov.in/governor-hosts-at-home-function-at-lok-bhavan/ .
- Sikkim official current CM and council: https://ipr.sikkim.gov.in/Home/LegislativeAssembly . Official June 2026 release confirms Prem Singh Tamang in office: https://www.sikkim.gov.in/media/news-announcement/news-info?name=Hon%27ble+Chief+Minister+Highlights+Need+for+Stronger+EAP+Framework+at+Seminar+Chaired+by+Union+Finance+Minister . A complete primary historical CM/cabinet list was not recovered.
- Punjab: central public broadcaster confirms Bhagwant Mann in office during 2026: https://newsonair.gov.in/chief-ministers-of-punjab-haryana-discuss-sutlej-yamuna-link-canal-issue/ . Historical enumeration and BJP cabinet record remain secondary in this audit.

## Implications for causal analysis

Define the outcome and exposure before inspecting party-specific counts. Use all eligible controls or a transparent prespecified subset. Include pre-treatment reporting/coverage diagnostics and state trends. Kerala and Tamil Nadu's contemporaneous non-BJP government turnover may matter even though their BJP-chief-minister exposure remains zero. A difference in a few selected news reports is not an identified BJP effect. Report any estimate as descriptive unless a credible comparative design and comparable event ascertainment support stronger inference.

## Mechanism positive control under a non-BJP government

The TOI report at https://timesofindia.indiatimes.com/india/4-rape-accused-snatched-2-guns-from-10-cops-shot-dead-police/articleshow/72408291.cms was updated 7 December 2019 and describes an event on Friday 6 December 2019, approximately 05:45-06:15 IST, near Shadnagar in Telangana. Four accused died in one incident. Police attributed the firing to seizure of two pistols from their escorts during property recovery. Code **one incident, four deaths, alleged gun-snatching claim**, not four independent events. This is a positive control for the mechanism under the established TRS/K. Chandrashekar Rao government. The official KCR profile above establishes his TRS affiliation and first-CM role; a complete party-spell table should still retain a dated 2019 office record. Its existence establishes non-exclusivity, not the relative frequency under different governments.
