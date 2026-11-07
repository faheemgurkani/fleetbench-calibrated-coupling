# Official report template

Downloaded 2026-11-05 from the Google Doc linked on the Guidelines tab ([make-a-copy link](https://docs.google.com/document/d/1_1_27EyZriMlc8n8EBE2YScaeyMjm-8xjR097nmHXAE/copy?usp=sharing)).

- `apart_report_template.docx`: editable Word export, **with the required "Limitations and Dual-Use / Ethical Considerations" appendix added** (just before "LLM Usage Statement")
- `apart_report_template.md`: Markdown export, with the same appendix added
- `apart_report_template.original.docx` / `.original.pdf`: unmodified Google Docs exports, for reference

> A fresh copy of the Google Doc **won't** include the required appendix. Add a Heading 2 "Appendix: Limitations and Dual-Use / Ethical Considerations" before "LLM Usage Statement".

**Workflow:** draft each section as a `.md` file, paste the drafts into your own copy of the Google Doc (make-a-copy link above), then export to PDF.

## Template structure

1. Title block: PROJECT TITLE (footnote: "Research conducted at the Swarm Alignment Hackathon, November 2026"), up to 6 authors with affiliations, "With Apart Research", **Abstract (150–250 words)**
2. Info box (delete before submitting)
3. **1. Introduction**: problem, why it matters, threat model, and a **"Our main contributions are:"** numbered list
4. **2. Related Work**: the closest work and the gap; when someone would use your method; what new insight it gives
5. **3. Methods**: enough detail to replicate; justify design choices (cite prior work); say what didn't work
6. **4. Results**: at least one figure strongly encouraged; separate observations from interpretations; show significance and robustness. Number figures and tables, give them self-contained captions, and keep text legible.
7. **5. Discussion and Limitations**, with subsections **Limitations** (state assumptions and how conclusions change if they fail) and **Future Work**
8. **6. Conclusion** (1–2 paragraphs)
9. **Code and Data** (repo, data, other artifacts; note any info hazards)
10. **Author Contributions** (optional)
11. **References** (consistent format: authors, year, title, venue, URL/DOI)
12. **Appendix** (optional), then **Appendix: Limitations and Dual-Use / Ethical Considerations** (required, added here)
13. **LLM Usage Statement**

## Where the template disagrees with the Guidelines tab
| Topic | Template info box | Guidelines tab (follow this) |
|---|---|---|
| Length | "Recommended length: 4 pages excluding references and appendix" | **Max 8 pages** excluding references and appendices; "most strong projects are 4 to 8 pages" |
| Required appendix | Not in the template | **"Limitations and Dual-Use / Ethical Considerations" appendix is required** |
| Rubric link | Notion "sprint-evaluation-rubric" | Three 1–5 dimensions on the Guidelines tab (see `../03_guidelines_and_rubric.md`) |
| Abstract | 150–250 words | 150–250 words (they agree) |
