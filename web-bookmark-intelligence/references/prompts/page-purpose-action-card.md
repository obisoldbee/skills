# Page-purpose and action-card prompt

```text
Background:
Assess this candidate evidence case using page text, OCR, visual evidence, permitted user context, and GitHub snapshots. Attribute each conclusion to its source. A final evidence status may be full_body, full_body_with_media_supplement, needs_image_supplement, or failed.

Materials:
- Intake case: {{case_json}}
- Fused evidence assessment: {{evidence_assessment_json}}
- Text evidence with spans: {{body_text_and_spans}}
- Media inventory/OCR/visual evidence: {{media_evidence}}
- Permitted context snapshot: {{context_snapshot}}
- GitHub repository snapshots: {{github_snapshots}}

Constraints:
- Cite a text span, image region, or video time range for every substantive claim or repository lead.
- Meta descriptions, titles, covers, and video metadata are summaries, never body/video evidence.
- If final_status is failed, report evidence_insufficient and do not infer page purpose.
- If final_status is needs_image_supplement, state the DOM limitation and cite image-level evidence for any visual claim.
- If context is missing, return context_insufficient; never infer an active user priority.
- Preserve privacy labels. Do not request or expose credentials, tokens, cookies, private paths, or unapproved external uploads.
- For GitHub, retain source URL, intended use, discussion conclusion, star/fork/watch snapshot time, repository update time, and freshness uncertainty.
- Classify each candidate only as poc_candidate, research_refresh, catalog_only, rule_candidate, duplicate_existing, ignore_low_value, or reject_conflict_or_risk.
- No classification grants installation, adoption, deployment, or formal writeback.
- Stop rule: stop when evidence is missing, privacy blocks use, or permitted context is insufficient. Report the blocker; do not retry with another source class or provider.

Evidence handling:
Before each substantive claim, locate its supplied text span, image region, or video time range. Mark unsupported claims unknown. Match content units only against context whose privacy and allowed-use fields permit that comparison. Return context_insufficient when no permitted match exists.

Example 1:
Input has only a long-image project list and a short meta description. Output final evidence as needs_image_supplement, request/cite OCR and image regions, and do not invent ten repository records from the description.

Example 2:
Input has substantive DOM text and the decisive feature comparison is in annotated screenshots. Output full_body_with_media_supplement only when those screenshots have image-level evidence; otherwise leave the comparison unknown.

Example 3:
A repository overlaps with an existing formal-current rejection. Report the overlap and use reject_conflict_or_risk unless the new source supplies a cited material delta.

Example 4:
A screenshot shows a tool but has no source URL. Set source_url to null, retain the screenshot hash, state uncertainty, and recommend catalog_only or research_refresh rather than a factual repository claim.

Task:
Turn the supplied, fused capture evidence into page-purpose notes, content units, comparison notes, and user-gated action cards. Write Chinese unless the caller requests another language. Do not call a provider, fetch a URL, refresh GitHub, install a Skill, or write a formal Akashic layer.

Output format:
Return JSON with page_purpose, content_units, comparison, action_cards, uncertainties, and evidence_gaps. Each action card needs recommendation, reason, same_as_existing, new_vs_existing, matched_context_ids, matched_repo_ids, evidence_refs, freshness_state, and user_decision_required.

Success criteria:
Every substantive output has evidence references; unsupported facts remain unknown; context use follows its allowed-use fields; each action card gives the user a concrete next-action decision.
```
