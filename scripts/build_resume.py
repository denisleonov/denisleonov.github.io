#!/usr/bin/env python3
"""Build a bilingual static resume and two PDFs from resume.json.

Usage: python3 scripts/build_resume.py [--html-only] [--output-dir PATH]
HTML uses only the Python standard library. PDF export requires reportlab.
"""
from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF_NAMES = {lang: f"Denis_Leonov_Resume_{lang.upper()}.pdf" for lang in ("en", "ru")}
PALETTE = {
    "ink": "#16183a",
    "deep": "#151b52",
    "accent": "#2e3a9e",
    "electric": "#2a4bc4",
    "copper": "#b5553a",
    "peach": "#ffb48a",
    "frost": "#cfe0ff",
    "muted": "#63617b",
    "line": "#deddea",
    "paper": "#ffffff",
    "wash": "#f1f0f5",
    "impact-bg": "#151b52",
    "impact-text": "#f7f8ff",
    "impact-muted": "#c6cbed",
    "impact-line": "#394175",
    "cool": "#eef4ff",
}


def employment_months(periods):
    months = set()
    for start, end in periods:
        sy, sm = map(int, start.split("-"))
        ey, em = map(int, end.split("-"))
        months.update(range(sy * 12 + sm - 1, ey * 12 + em))
    return len(months)


def e(value):
    return escape(str(value), quote=True)


def bullets(items):
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def section(lang, key, title, content, note="", css=""):
    names = {
        "expertise": ("01 / Expertise", "01 / Компетенции"),
        "experience": ("02 / Experience", "02 / Опыт"),
        "multimodal": ("03 / Modalities", "03 / Модальности"),
        "agents": ("04 / Agent systems", "04 / Агентные системы"),
        "projects": ("05 / Independent work", "05 / Собственные продукты"),
        "recognition": ("06 / Selected campaign", "06 / Международный проект"),
        "earlier": ("07 / Background", "07 / Другой опыт"),
        "stack": ("08 / Engineering", "08 / Технологии"),
        "education": ("09 / Education", "09 / Образование"),
    }
    kicker = names[key][lang == "ru"]
    return (
        f'<section id="{lang}-{key}" class="section section-{key} {css}">'
        f'<div class="section-heading"><p class="section-kicker">{e(kicker)}</p><h2>{e(title)}</h2>'
        + (f'<p class="section-note">{e(note)}</p>' if note else "")
        + f'</div><div class="section-content">{content}</div></section>'
    )


def render_resume(lang, d, contact):
    metrics = "".join(
        f'<div class="metric"><p class="metric-value">{e(m["value"])}</p>'
        f'<h3>{e(m["label"])}</h3><p>{e(m["note"])}</p></div>'
        for m in d["metrics"]
    )
    competencies = '<div class="competencies">' + "".join(
        f'<article class="competency"><h3>{e(c["title"])}</h3><p>{e(c["text"])}</p></article>'
        for c in d["competencies"]
    ) + "</div>"
    details_label = "View contribution & implementation" if lang == "en" else "Подробнее о вкладе и реализации"
    details_close = "Hide details" if lang == "en" else "Свернуть подробности"
    roles = "".join(
        '<article class="role"><div class="role-meta">'
        f'<h3>{e(r["company"])}</h3><p class="role-title">{e(r["role"])}</p>'
        f'<p class="role-date">{e(r["date"])}</p><p class="role-context">{e(r["context"])}</p></div>'
        f'<div class="role-main"><p class="role-outcome">{e(r["outcome"])}</p>'
        f'<p class="role-lead">{r["bullets"][0]}</p>'
        f'<details class="role-details"><summary><span class="details-collapsed">{details_label}</span><span class="details-expanded">{details_close}</span></summary>'
        + bullets(r["bullets"][1:])
        + f'<p class="role-stack">{e(r["stack"])}</p></details></div></article>'
        for r in d["roles"]
    )
    modalities = f'<p class="section-intro">{e(d["multimodal_intro"])}</p><div class="modalities">' + "".join(
        f'<article class="modality"><div class="modality-top"><h3>{e(m["name"])}</h3>'
        f'<span class="stage">{e(m["stage"])}</span></div><p>{e(m["text"])}</p></article>'
        for m in d["modalities"]
    ) + "</div>"
    agents = f'<p class="section-intro">{e(d["agents_intro"])}</p>' + bullets(d["agents_bullets"])
    projects = "".join(
        f'<article class="project"><h3>{e(p["title"])}</h3><p>{e(p["text"])}</p></article>'
        for p in d["projects"]
    )
    campaign_links = "".join(f'<a href="{e(url)}">{e(label)} <span aria-hidden="true">↗</span></a>' for label, url in d["campaign_links"])
    recognition = (
        f'<article class="campaign"><h3>{e(d["campaign_title"])}</h3>'
        f'<p class="campaign-role">{e(d["campaign_role"])}</p><p>{e(d["campaign_text"])}</p>'
        f'<p>{d["campaign_result"]}</p><div class="evidence-links">{campaign_links}</div></article>'
        f'<p class="talks">{d["talks"]}</p>'
    )
    other_roles = '<div class="earlier-roles">' + "".join(
        '<article class="earlier-role">'
        f'<div class="earlier-top"><h3>{e(r["company"])} <span>· {e(r["role"])}</span></h3>'
        f'<p class="role-date">{e(r["date"])}</p></div><p>{e(r["text"])}</p></article>'
        for r in d["other_roles"]
    ) + f'</div><p class="research">{d["research"]}</p>'
    education = '<div class="degrees">' + "".join(
        f'<div class="degree"><h3>{e(item["title"])}</h3><p>{e(item["text"])}</p></div>'
        for item in d["education"]
    ) + f'</div><p class="languages">{e(d["languages"])}</p>'
    summary_main, summary_context = d["summary"].split("<strong>8+", 1)
    summary_context = "<strong>8+" + summary_context
    modality_tags = "".join(f'<span>{e(label.strip())}</span>' for label in d["modalities_line"].split("·"))
    stack_groups = '<div class="technical-stack">' + "".join(f'<p>{e(group.strip())}</p>' for group in d["stack"].split("·")) + '</div>'
    cta_title = "Let’s talk" if lang == "en" else "Обсудим сотрудничество"
    cta_note = "AI product & technical leadership" if lang == "en" else "Продуктовое и техническое руководство в AI"
    return (
        f'<article class="resume" id="resume-{lang}" lang="{lang}"'
        + (" hidden" if lang != "en" else "") + ">"
        f'<a class="skip-link" href="#{lang}-experience">{e(d["skip"])}</a>'
        '<header class="hero">'
        f'<p class="eyebrow">{e(d["eyebrow"])}</p><div class="hero-grid"><div class="hero-main">'
        f'<div class="identity"><h1>{e(d["name"])}</h1><p class="headline">{e(d["headline"])}</p></div>'
        f'<p class="summary">{summary_main.strip()}</p>'
        '<address class="contacts">'
        f'<a href="mailto:{e(contact["email"])}">{e(contact["email"])}</a>'
        f'<a href="{e(contact["telegram"])}">Telegram @den_is_lion</a>'
        f'<a href="{e(contact["github"])}">GitHub <span aria-hidden="true">↗</span></a></address></div>'
        f'<aside class="profile"><div class="portrait-wrap"><img class="portrait" src="photo.png" alt="{e(d["name"])}" width="200" height="200"></div>'
        f'<p class="location">{e(d["location"])}</p><p class="contract">{e(d["contract"])}</p></aside></div>'
        f'</header><section class="impact" id="{lang}-impact" aria-label="{e(d["impact_title"])}">'
        f'<p class="impact-heading">{e(d["impact_title"])}</p><div class="impact-grid">{metrics}</div></section>'
        f'<p class="career-note">{summary_context}</p><div class="modality-line"><strong>{e(d["modalities_line_label"])}</strong><div class="modality-tags">{modality_tags}</div></div>'
        + section(lang, "expertise", d["expertise_title"], competencies)
        + section(lang, "experience", d["experience_title"], roles, d["experience_note"])
        + section(lang, "multimodal", d["multimodal_title"], modalities)
        + section(lang, "agents", d["agents_title"], agents)
        + section(lang, "projects", d["projects_title"], '<div class="projects">' + projects + '</div>', d["projects_note"])
        + section(lang, "recognition", d["recognition_title"], recognition)
        + section(lang, "earlier", d["other_title"], other_roles)
        + section(lang, "stack", d["stack_title"], stack_groups)
        + section(lang, "education", d["education_title"], education)
        + f'<section class="contact-cta" aria-labelledby="{lang}-contact-title"><div><p>{cta_note}</p><h2 id="{lang}-contact-title">{cta_title}</h2></div>'
        f'<a href="mailto:{e(contact["email"])}">{e(contact["email"])}<span aria-hidden="true">↗</span></a></section>'
        + f'<footer class="footer"><p>{e(d["updated_label"])}</p><p>{e(d["footer"])}</p></footer></article>'
    )



CSS = ":root{color-scheme:light;" + ";".join(f"--{key}:{value}" for key, value in PALETTE.items()) + ";}\n" + """
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:104px}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;-webkit-font-smoothing:antialiased}
::selection{background:var(--frost);color:var(--deep)}
a{color:var(--accent);text-underline-offset:5px;text-decoration-thickness:1px}
a:hover{color:var(--electric)}
button,a,summary{-webkit-tap-highlight-color:transparent}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid var(--electric);outline-offset:5px;border-radius:3px}
[hidden]{display:none!important}
.toolbar{position:sticky;top:0;z-index:5;max-width:1184px;margin:0 auto;padding:19px 32px;display:flex;align-items:center;gap:28px;min-height:80px;background:rgba(255,255,255,.95);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}
.wordmark{display:flex;align-items:baseline;color:var(--deep);font-weight:800;letter-spacing:-.055em;font-size:25px;text-decoration:none;white-space:nowrap}
.wordmark span{color:var(--muted);font-weight:450;margin-left:9px;font-size:11px;letter-spacing:.03em}
.nav-links{display:flex;gap:22px;align-items:center;flex:1}
.nav-links a{font-size:13px;font-weight:550;color:var(--muted);text-decoration:none;white-space:nowrap;transition:color .15s}
.nav-links a:hover,.nav-links a[aria-current]{color:var(--deep)}
.nav-links a[aria-current]{text-decoration:underline;text-decoration-color:var(--copper);text-underline-offset:10px}
.controls{margin-left:auto;display:flex;gap:14px;align-items:center}
.language-switch{display:flex;padding:3px;gap:2px;background:var(--wash);border-radius:8px}
.language-switch button{font-family:inherit;font-size:12px;line-height:1.2;font-weight:600;border:0;padding:9px 10px;border-radius:5px;color:var(--muted);background:transparent;cursor:pointer}
.language-switch button[aria-pressed=true]{background:var(--deep);color:white}
.download{font-size:13px;font-weight:650;padding:12px 17px;background:var(--deep);color:white;text-decoration:none;border-radius:8px;white-space:nowrap;transition:background .15s}
.download:hover{background:var(--electric);color:white}
.resume{max-width:1184px;margin:0 auto;padding:0 32px}
.skip-link{position:absolute;left:-9999px;top:0}
.skip-link:focus{position:fixed;top:10px;left:15px;z-index:20;background:white;padding:10px}
.hero{padding:56px 0 36px}
.eyebrow{display:flex;align-items:center;gap:12px;margin:0 0 30px;font-size:13px;font-weight:650;line-height:1.6;letter-spacing:.075em;text-transform:uppercase;color:var(--copper)}
.eyebrow::before{content:"";width:26px;height:2px;flex:0 0 26px;background:var(--copper)}
.hero-grid{display:grid;grid-template-columns:minmax(0,1fr) 220px;gap:76px;align-items:start}
.identity h1{font-size:clamp(48px,5.7vw,72px);line-height:1.02;letter-spacing:-.055em;margin:0 0 15px;font-weight:750;color:var(--deep)}
.headline{font-size:34px;line-height:1.2;letter-spacing:-.035em;margin:0;font-weight:600;color:var(--deep);max-width:730px;text-wrap:balance}
.summary{font-size:18px;line-height:1.75;margin:25px 0 22px;max-width:760px;color:#414159}
strong{font-weight:650}
.summary strong{color:var(--deep)}
.profile{padding-top:5px}
.portrait-wrap{padding:4px;margin:0 0 20px;background:var(--deep);border-radius:30px}

.portrait{display:block;width:100%;height:auto;aspect-ratio:1;border-radius:26px;object-fit:cover}
.location,.contract{font-size:13px;line-height:1.8;color:var(--muted);margin:0}
.contract{margin-top:10px;padding-top:10px;border-top:1px solid var(--line)}
.contacts{font-style:normal;display:flex;gap:10px 20px;align-items:center;flex-wrap:wrap;font-size:13px;line-height:1.5;margin:0}
.contacts a{color:var(--deep);text-decoration:none;overflow-wrap:anywhere}
.contacts a:first-child{display:inline-flex;align-items:center;gap:12px;border-bottom:1px solid var(--copper);padding:9px 0;font-weight:600}
.contacts a:first-child::after{content:"↗";color:var(--copper);font-size:18px}
.contacts a:hover{color:var(--electric)}
.impact{background:var(--deep);color:var(--impact-text);border-radius:16px;padding:24px 30px 30px;overflow:hidden}
.impact-heading{font-size:11px;font-weight:600;letter-spacing:.13em;line-height:1.5;text-transform:uppercase;margin:0 0 24px;color:var(--impact-muted)}
.impact-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr))}
.metric{padding:0 26px;border-left:1px solid var(--impact-line);min-width:0}
.metric:first-child{padding-left:0;border:0}
.metric:last-child{padding-right:0}
.metric-value{font-size:52px;font-weight:650;letter-spacing:-.05em;line-height:1;margin:0 0 16px;color:var(--peach);font-variant-numeric:tabular-nums}
.metric h3{font-size:15px;line-height:1.45;margin:0 0 8px;font-weight:600}
.metric>p:last-child{font-size:12px;line-height:1.6;color:var(--impact-muted);margin:0}
.career-note{font-size:14px;line-height:1.85;color:var(--muted);margin:21px 0 0;max-width:960px}.career-note strong{color:var(--deep)}
.modality-line{display:flex;align-items:center;flex-wrap:wrap;gap:14px 28px;margin:0;padding:24px 0 34px}
.modality-line strong{font-size:12px;font-weight:550;color:var(--muted)}
.modality-tags{display:flex;gap:10px 22px;flex-wrap:wrap}
.modality-tags span{font-size:13px;color:var(--deep);font-weight:550}
.section{padding:60px 0;border-top:1px solid var(--line);scroll-margin-top:0}
.section-heading{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,390px);gap:20px 60px;align-items:end;margin-bottom:34px}
.section-kicker{grid-column:1/-1;font-size:11px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--copper);margin:0 0 -10px}
.section-heading h2{color:var(--deep);font-size:34px;letter-spacing:-.04em;line-height:1.18;margin:0;font-weight:650;max-width:680px;text-wrap:balance}
.section-note{font-size:12px;line-height:1.7;color:var(--muted);margin:0;max-width:390px;justify-self:end}
.section-content{min-width:0}
.section-content>p:first-child{margin-top:0}
.section-content>p:last-child{margin-bottom:0}
.competencies{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:30px 36px;counter-reset:competency}
.competency{padding-top:18px;border-top:1px solid var(--line);counter-increment:competency}
.competency::before{content:counter(competency,decimal-leading-zero);display:block;font-size:11px;letter-spacing:.04em;color:var(--copper);margin-bottom:11px;font-variant-numeric:tabular-nums}
.competency h3{font-size:18px;line-height:1.35;font-weight:650;letter-spacing:-.015em;margin:0 0 11px;color:var(--deep)}
.competency p{font-size:14px;line-height:1.8;color:var(--muted);margin:0}
.role{display:grid;grid-template-columns:250px minmax(0,1fr);gap:54px;padding:36px 0;border-top:1px solid var(--line)}
.role:first-child{border-top:0;padding-top:0}
.role:last-child{padding-bottom:0}
.role h3{font-size:25px;line-height:1.2;margin:0 0 10px;letter-spacing:-.035em;font-weight:650;color:var(--deep);text-wrap:balance}
.role-title{font-size:15px;line-height:1.5;margin:0 0 14px;font-weight:600;color:var(--ink)}
.role-date{font-size:12px;line-height:1.65;color:var(--muted);margin:0}
.role-context{font-size:13px;line-height:1.7;color:var(--muted);margin:15px 0 0;max-width:235px}
.role-outcome{font-size:20px;letter-spacing:-.02em;line-height:1.5;font-weight:600;color:var(--deep);margin:0 0 20px;padding:0 0 0 18px;border-left:3px solid var(--peach);text-wrap:pretty}
.role-lead{font-size:16px;line-height:1.8;margin:0;color:#414159}
.role-lead strong{color:var(--deep)}
.role-details{margin-top:21px}
.role-details summary{display:flex;align-items:center;justify-content:space-between;gap:18px;cursor:pointer;font-size:14px;line-height:1.5;color:var(--accent);font-weight:600;list-style:none;padding:14px 18px;min-height:52px;background:var(--cool);border:1px solid #d8def0;border-radius:8px;transition:background .15s,border-color .15s}.role-details summary:hover{background:#e2e9ff;border-color:#9ba8df}.role-details[open] summary{border-color:#9ba8df}.details-expanded{display:none}.role-details[open] .details-expanded{display:inline}.role-details[open] .details-collapsed{display:none}
.role-details summary::-webkit-details-marker{display:none}
.role-details summary::after{content:"";width:9px;height:9px;flex:0 0 9px;border-right:2px solid var(--accent);border-bottom:2px solid var(--accent);transform:rotate(45deg);margin:0 2px 4px 0}
.role-details[open] summary::after{transform:rotate(225deg);margin-top:5px;margin-bottom:0}
ul{padding-left:19px;margin:18px 0 0}
li{padding-left:3px;margin:0 0 12px;font-size:15px;line-height:1.8;color:#414159}
li strong{color:var(--deep)}
li::marker{color:var(--copper)}
li:last-child{margin-bottom:0}
.role-stack{font-size:12px;line-height:1.8;color:var(--muted);margin:20px 0 0}
.section-intro{font-size:17px;line-height:1.75;margin:0 0 28px;color:var(--muted);max-width:780px}
.section-multimodal{background:var(--cool);border:0;border-radius:20px;padding:38px;margin:10px 0 20px}
.modalities{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px 32px}
.modality{border-top:1px solid #d8def0;padding-top:18px}
.modality-top{display:flex;align-items:start;justify-content:space-between;gap:8px;flex-wrap:wrap}
.modality h3{font-size:18px;font-weight:650;line-height:1.35;letter-spacing:-.015em;margin:0;color:var(--deep)}
.stage{font-size:10px;font-weight:550;color:var(--accent);background:white;padding:3px 7px;border-radius:4px;white-space:nowrap}
.modality p{font-size:14px;line-height:1.8;color:var(--muted);margin:12px 0 0}
.section-agents{background:var(--deep);color:var(--impact-text);border:0;border-radius:20px;padding:38px;margin:24px 0}
.section-agents .section-kicker{color:var(--peach)}
.section-agents h2{color:var(--impact-text)}
.section-agents .section-intro{color:var(--impact-muted);font-size:18px}
.section-agents ul{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:30px;list-style:none;padding:0;margin:30px 0 0;counter-reset:agent}
.section-agents li{font-size:14px;line-height:1.8;color:var(--impact-muted);padding:20px 0 0;margin:0;border-top:1px solid var(--impact-line);counter-increment:agent}
.section-agents li::before{content:counter(agent,decimal-leading-zero);display:block;font-size:11px;color:var(--peach);margin-bottom:15px}
.section-agents li strong{font-size:18px;line-height:1.35;color:var(--impact-text);display:block;font-weight:600;margin:0 0 12px}
.projects{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.project{min-width:0;padding:30px;background:var(--wash);border-radius:14px;border-top:3px solid var(--frost)}
.project h3{overflow-wrap:anywhere;font-size:23px;font-weight:650;line-height:1.25;letter-spacing:-.025em;color:var(--deep);margin:0 0 17px;text-wrap:balance}
.project p{font-size:15px;line-height:1.85;color:#535169;margin:0}
.section-recognition{border:0;background:#fff4ec;padding:38px;border-radius:20px;margin-bottom:20px}
.campaign{max-width:860px}
.campaign h3{font-size:27px;font-weight:650;line-height:1.25;letter-spacing:-.035em;margin:0 0 14px;color:var(--deep);text-wrap:balance}
.campaign>p{font-size:16px;line-height:1.8;margin:14px 0 0;color:#535169}
.campaign-role{color:var(--muted)!important;font-size:13px!important;margin:0 0 22px!important}
.campaign>p strong{color:var(--copper);font-weight:650}
.evidence-links{display:flex;gap:24px;flex-wrap:wrap;margin-top:22px}
.evidence-links a{font-size:13px;font-weight:550;color:var(--deep)}
.talks{border-top:1px solid #ebd9d0;padding-top:22px;margin:28px 0 0;font-size:15px;line-height:1.8;color:#535169}
.talks strong{color:var(--copper)}
.earlier-roles{display:grid;grid-template-columns:1fr 1fr;gap:26px 40px}
.earlier-role{padding-top:18px;border-top:1px solid var(--line)}
.earlier-top{display:flex;flex-direction:column-reverse;gap:8px}
.earlier-top h3{font-size:16px;line-height:1.5;margin:0;font-weight:650;color:var(--deep)}
.earlier-top h3 span{font-weight:450}
.earlier-role>p{font-size:14px;line-height:1.8;margin:8px 0 0;color:var(--muted)}
.research{font-size:14px;line-height:1.8;border-top:1px solid var(--line);padding-top:24px;margin:32px 0 0;color:var(--muted)}
.technical-stack{display:grid;grid-template-columns:1fr 1fr;gap:12px 32px}
.technical-stack p{font-size:14px;line-height:1.85;color:var(--muted);margin:0;padding:15px 0;border-top:1px solid var(--line)}
.degrees{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:32px}
.degree{border-top:1px solid var(--line);padding-top:18px}
.degree h3{font-size:16px;line-height:1.5;margin:0;font-weight:600;color:var(--deep)}
.degree p{font-size:14px;line-height:1.8;color:var(--muted);margin:10px 0 0}
.languages{font-size:14px;line-height:1.8;margin:30px 0 0;padding-top:22px;border-top:1px solid var(--line);color:var(--muted)}
.contact-cta{border-top:1px solid var(--line);padding:44px 0 48px;display:flex;justify-content:space-between;align-items:center;gap:30px}
.contact-cta p{font-size:12px;color:var(--muted);margin:0 0 10px}
.contact-cta h2{font-size:40px;letter-spacing:-.04em;line-height:1.15;font-weight:650;color:var(--deep);margin:0}
.contact-cta a{font-size:20px;letter-spacing:-.02em;color:var(--deep);text-decoration:none;border-bottom:1px solid var(--copper);padding-bottom:7px;overflow-wrap:anywhere}
.contact-cta a span{color:var(--copper);margin-left:16px}
.footer{border-top:1px solid var(--line);padding:22px 0 30px;display:flex;justify-content:space-between;gap:20px;color:var(--muted);font-size:11px}
.footer p{margin:0}
@media(max-width:1100px){.toolbar{gap:20px;padding:16px 28px}.nav-links{gap:15px}.nav-links a{font-size:12px}.wordmark span{display:none}.resume{padding:0 28px}.hero-grid{grid-template-columns:minmax(0,1fr) 190px;gap:40px}.headline{font-size:30px}.identity h1{font-size:60px}.metric{padding:0 20px}.metric-value{font-size:46px}.role{grid-template-columns:220px minmax(0,1fr);gap:35px}.section-heading h2{font-size:31px}.section-heading{gap:20px 40px}.competencies,.modalities{gap:28px}.section-agents ul{gap:24px}}
@media(max-width:850px){.nav-links{display:none}.hero{padding-top:36px}.hero-grid{grid-template-columns:minmax(0,1fr) 160px;gap:28px}.identity h1{font-size:52px}.headline{font-size:28px}.summary{font-size:17px;line-height:1.75}.profile{padding-top:1px}.portrait{border-radius:22px}.portrait-wrap{border-radius:26px}.location,.contract{font-size:12px}.eyebrow{font-size:12px;margin-bottom:26px}.impact{padding:23px}.impact-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.metric{padding:20px 22px}.metric:nth-child(2n+1){border-left:0;padding-left:0}.metric:nth-child(2n){border-left:1px solid var(--impact-line);padding-right:0}.metric:nth-child(n+3){border-top:1px solid var(--impact-line)}.metric-value{font-size:40px}.metric h3{font-size:14px}.metric>p:last-child{font-size:11px}.section{padding:42px 0}.section-heading{display:block;margin-bottom:28px}.section-kicker{margin:0 0 13px}.section-heading h2{font-size:30px}.section-note{margin-top:16px;max-width:none}.competencies,.modalities{grid-template-columns:1fr 1fr}.role{grid-template-columns:190px minmax(0,1fr);gap:26px;padding:30px 0}.role h3{font-size:23px}.role-outcome{font-size:18px}.role-lead,li{font-size:15px}.section-agents,.section-multimodal,.section-recognition{padding:30px}.section-agents ul{grid-template-columns:1fr}.section-agents li{display:block;padding-top:18px}.section-agents li::before{float:left;width:36px;margin:0}.section-agents li strong{padding-left:36px;font-size:18px}.projects{gap:20px}.project{padding:24px}.project h3{font-size:22px}.degrees{grid-template-columns:1fr;gap:24px}.contact-cta h2{font-size:34px}.contact-cta a{font-size:17px}}
@media(max-width:600px){html{scroll-padding-top:88px}.toolbar{min-height:70px;padding:12px 20px;gap:16px}.wordmark{font-size:24px}.controls{gap:10px}.download{font-size:12px;padding:11px 13px}.language-switch button{padding:8px}.resume{padding:0 22px}.hero{padding:32px 0 27px}.eyebrow{font-size:11px;letter-spacing:.055em;margin-bottom:24px;gap:10px}.eyebrow::before{width:18px;flex-basis:18px}.hero-grid{grid-template-columns:1fr;gap:24px}.hero-main{display:contents}.identity{grid-row:1}.identity h1{font-size:clamp(42px,9vw,56px);line-height:1.04;margin-bottom:13px}.headline{font-size:27px;max-width:450px;line-height:1.18;text-wrap:initial}.summary{grid-row:3;font-size:16px;line-height:1.8;margin:0}.contacts{grid-row:4;font-size:12px;gap:9px 19px}.contacts a:first-child{flex-basis:100%;width:fit-content;max-width:fit-content;padding:5px 0}.profile{grid-row:2;display:grid;grid-template-columns:76px minmax(0,1fr);gap:0 20px;align-items:center;padding:0}.portrait-wrap{grid-row:1/3;margin:0;padding:3px;border-radius:18px;width:76px}.portrait{border-radius:15px}.location,.contract{font-size:11px;line-height:1.7}.contract{margin:3px 0 0;padding:0;border:0;align-self:start}.location{align-self:end}.impact{padding:22px 21px 5px;border-radius:13px}.impact-heading{font-size:10px;margin-bottom:8px;letter-spacing:.1em}.impact-grid{grid-template-columns:1fr 1fr}.metric{padding:20px 15px 22px 0;border:0}.metric:nth-child(2n){padding-left:19px;padding-right:0;border-left:1px solid var(--impact-line)}.metric:nth-child(n+3){border-top:1px solid var(--impact-line)}.metric-value{font-size:41px;line-height:1;margin-bottom:13px}.metric h3{font-size:13px;line-height:1.45}.metric>p:last-child{font-size:11px;line-height:1.6}.modality-line{padding:22px 0 28px;gap:10px}.modality-line strong{flex-basis:100%;font-size:11px}.modality-tags{gap:9px 18px}.modality-tags span{font-size:12px}.section{padding:36px 0}.section-kicker{font-size:10px;margin-bottom:12px}.section-heading h2{font-size:29px;line-height:1.2;max-width:480px}.section-note{font-size:11px;margin-top:14px}.section-heading{margin-bottom:26px}.competencies{grid-template-columns:1fr 1fr;gap:25px 20px}.competency{padding-top:14px}.competency::before{margin-bottom:9px}.competency h3{font-size:16px;line-height:1.35}.competency p{font-size:13px;line-height:1.8}.role{display:block;padding:28px 0}.role h3{font-size:25px;max-width:380px}.role-title{font-size:15px;margin-bottom:8px}.role-date{font-size:12px}.role-context{max-width:none;font-size:12px;margin-top:9px}.role-main{margin-top:21px}.role-outcome{font-size:18px;line-height:1.5;padding-left:15px;margin-bottom:18px}.role-lead,li{font-size:15px;line-height:1.85}.role-details{margin-top:18px}.role-details summary{font-size:13px;padding:14px 15px}.role-stack{font-size:11px}.section-multimodal,.section-agents,.section-recognition{margin:12px -6px 20px;padding:26px 22px;border-radius:15px}.section-intro{font-size:15px;line-height:1.8}.modalities{grid-template-columns:1fr;gap:23px}.modality h3{font-size:18px}.modality p{font-size:14px;line-height:1.8}.stage{font-size:10px}.section-agents .section-intro{font-size:16px}.section-agents ul{gap:24px;margin-top:25px}.section-agents li{font-size:14px}.section-agents li strong{font-size:18px;line-height:1.4;margin-bottom:12px}.projects{grid-template-columns:1fr;gap:18px}.project{padding:24px;border-radius:12px}.project h3{font-size:24px}.project p{font-size:14px;line-height:1.85}.campaign h3{font-size:25px}.campaign>p{font-size:15px}.campaign-role{font-size:12px!important}.evidence-links{gap:18px}.talks{font-size:14px}.earlier-roles{grid-template-columns:1fr;gap:24px}.earlier-top h3{font-size:16px}.earlier-role>p{font-size:14px}.research{font-size:13px}.technical-stack{grid-template-columns:1fr;gap:0}.technical-stack p{font-size:13px}.degree h3{font-size:16px}.degree p,.languages{font-size:13px}.contact-cta{display:block;padding:32px 0 36px}.contact-cta h2{font-size:36px;margin-bottom:26px}.contact-cta a{font-size:18px}.contact-cta a span{margin-left:9px}.footer{display:block;padding:22px 0;font-size:10px}.footer p+p{margin-top:8px}}
@media(max-width:480px){.competencies{grid-template-columns:1fr}.career-note{font-size:13px;line-height:1.8}}
@media(max-width:360px){.toolbar{padding-left:16px;padding-right:16px}.resume{padding-left:18px;padding-right:18px}.controls{gap:7px}.download{padding:11px 10px;font-size:11px}.language-switch button{padding:8px 7px}.identity h1{font-size:41px}.headline{font-size:25px}.competencies{grid-template-columns:1fr}.impact{padding-left:17px;padding-right:17px}.metric-value{font-size:37px}.metric:nth-child(2n){padding-left:14px}.metric h3{font-size:12px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}

.section-expertise{background:var(--deep);color:var(--impact-text);border:0;border-radius:20px;padding:38px;margin:0 0 24px}
.section-expertise .section-kicker,.section-experience .section-kicker{color:var(--peach)}
.section-expertise h2,.section-expertise .competency h3,.section-experience .section-heading h2{color:var(--impact-text)}
.section-expertise .competency{border-color:var(--impact-line)}
.section-expertise .competency::before{color:var(--peach)}
.section-expertise .competency p{color:var(--impact-muted)}
.section-experience{border:1px solid var(--line);border-radius:20px;padding:0;margin:24px 0 38px;overflow:hidden}
.section-experience>.section-heading{background:var(--deep);padding:32px 38px 36px;margin:0}
.section-experience .section-note{color:var(--impact-muted)}
.section-experience>.section-content{padding:36px 38px 38px}
@media(max-width:850px){.section-expertise{padding:30px}.section-experience>.section-heading{padding:30px}.section-experience>.section-content{padding:30px}}
@media(max-width:600px){.section-expertise{padding:26px 22px;margin:12px -6px 20px;border-radius:15px}.section-experience{margin:12px -6px 24px;border-radius:15px}.section-experience>.section-heading{padding:26px 22px}.section-experience>.section-content{padding:28px 22px}}

@media print{@page{size:A4;margin:14mm}html,body{background:white;font-size:10pt}.toolbar,.skip-link,.profile,.contact-cta{display:none!important}.resume{margin:0;padding:0;max-width:none}.hero{padding-top:0;break-inside:avoid}.hero-grid{display:block}.identity h1{font-size:25pt}.headline{font-size:17pt}.eyebrow{font-size:9pt}.summary{font-size:10pt}.impact{print-color-adjust:exact;-webkit-print-color-adjust:exact;border-radius:0;padding:10pt}.impact-heading{margin-bottom:8pt}.metric-value{font-size:22pt}.metric h3{font-size:9pt}.metric>p:last-child{font-size:8pt}.section{display:block;padding:12pt 0}.section-heading{display:block;margin-bottom:8pt}.section-kicker{display:none}.section-heading h2{font-size:13pt}.section-note{font-size:8pt}.competencies,.modalities,.degrees{grid-template-columns:1fr 1fr;gap:8pt 15pt}.competency h3,.modality h3{font-size:11pt}.competency p,.modality p,li,.project p,.campaign>p{font-size:9pt;line-height:1.5}.role{display:block;padding:12pt 0;break-inside:avoid}.role h3{font-size:12pt}.role-title,.role-outcome{font-size:10pt}.role-main{margin-top:8pt}.role-lead{font-size:9pt}.section-agents,.section-multimodal,.section-recognition{margin:0;background:white;padding:12pt 0;color:var(--ink);border-radius:0}.section-agents h2,.section-agents li strong{color:var(--deep)}.section-agents li,.section-agents .section-intro{color:var(--muted)}.section-agents ul{grid-template-columns:1fr}.project,.modality,.competency{break-inside:avoid}.projects{display:block}.project{background:white;padding:12pt 0}.project h3,.campaign h3{font-size:12pt}.footer{font-size:8pt}.contacts{margin-bottom:10pt}.section-expertise,.section-experience{background:white;color:var(--ink);border:0;border-radius:0;margin:0;padding:12pt 0;overflow:visible}.section-experience>.section-heading{background:white;padding:0;margin-bottom:8pt}.section-experience>.section-content{padding:0}.section-expertise h2,.section-expertise .competency h3,.section-experience .section-heading h2{color:var(--deep)}.section-expertise .competency p,.section-experience .section-note{color:var(--muted)}a{color:inherit}}
"""

def build_html(data, out):
    labels = {
        lang: {key: d[key] for key in ("name", "headline", "download", "nav")}
        for lang, d in data.items() if lang in ("en", "ru")
    }
    for lang in ("en", "ru"):
        original = dict(labels[lang]["nav"])
        labels[lang]["nav"] = [
            ("experience", original["experience"]), ("expertise", original["expertise"]),
            ("multimodal", original["multimodal"]), ("agents", "Agents" if lang == "en" else "Агенты"),
            ("projects", original["projects"]),
        ]
    encoded = json.dumps(labels, ensure_ascii=False).replace("</", "<\\/")
    script = """
(() => {
 const labels = __LABELS__;
 const buttons = [...document.querySelectorAll('[data-language]')];
 const resumes = [...document.querySelectorAll('.resume')];
 const download = document.querySelector('.download');
 const navigation = [...document.querySelectorAll('[data-section]')];
 function switchLanguage(value, updateURL = true) {
   const lang = value === 'ru' ? 'ru' : 'en';
   resumes.forEach(node => { node.hidden = node.lang !== lang; });
   buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.language === lang)));
   document.documentElement.lang = lang;
   document.title = `${labels[lang].name} — ${labels[lang].headline}`;
   download.href = `output/pdf/Denis_Leonov_Resume_${lang.toUpperCase()}.pdf`;
   download.textContent = labels[lang].download + ' ↓';
   download.setAttribute('aria-label', lang === 'ru' ? 'Скачать резюме на русском в PDF' : 'Download English CV as PDF');
   navigation.forEach(link => {
     const match = labels[lang].nav.find(([id]) => id === link.dataset.section);
     link.textContent = match[1]; link.href = `#${lang}-${match[0]}`;
   });
   document.querySelector('.language-switch').setAttribute('aria-label', lang === 'ru' ? 'Язык резюме' : 'Resume language');
   navigation.forEach(link => link.removeAttribute('aria-current'));
   if (updateURL) {
     const url = new URL(location.href); url.searchParams.set('lang', lang); url.hash = '';
     history.replaceState(null, '', url);
   }
 }
 buttons.forEach(button => button.addEventListener('click', () => switchLanguage(button.dataset.language)));
 window.addEventListener('popstate', () => switchLanguage(new URLSearchParams(location.search).get('lang'), false));
 switchLanguage(new URLSearchParams(location.search).get('lang'), false);
 if ('IntersectionObserver' in window) {
   const observer = new IntersectionObserver(entries => {
     const visible = entries.filter(entry => entry.isIntersecting && !entry.target.closest('[hidden]'));
     if (!visible.length) return;
     const id = visible[0].target.id;
     navigation.forEach(link => {
       if (link.getAttribute('href') === '#' + id) link.setAttribute('aria-current', 'location');
       else link.removeAttribute('aria-current');
     });
   }, {rootMargin: '-15% 0px -60% 0px', threshold: 0});
   document.querySelectorAll('.section').forEach(section => observer.observe(section));
 }
})();
""".replace("__LABELS__", encoded)
    nav = "".join(f'<a data-section="{key}" href="#en-{key}">{label}</a>' for key, label in labels["en"]["nav"])
    html = (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Denis Leonov — AI Product &amp; Technical Lead</title>'
        '<meta name="description" content="AI product and technical leadership: product strategy, multimodal AI, teams up to 20, production ML, LLM agents and measurable product outcomes.">'
        f'<meta name="theme-color" content="{PALETTE["accent"]}"><link rel="icon" href="data:,">'
        f'<style>{CSS}</style></head><body>'
        '<nav class="toolbar" aria-label="Resume navigation"><a class="wordmark" href="#">DL<span>/ CV 2026</span></a>'
        f'<div class="nav-links">{nav}</div><div class="controls">'
        '<div class="language-switch" role="group" aria-label="Resume language">'
        '<button type="button" data-language="en" aria-pressed="true" lang="en">EN</button>'
        '<button type="button" data-language="ru" aria-pressed="false" lang="ru">RU</button></div>'
        '<a class="download" href="output/pdf/Denis_Leonov_Resume_EN.pdf" download>Download CV ↓</a></div></nav>'
        '<main>' + "".join(render_resume(lang, data[lang], data["contact"]) for lang in ("en", "ru"))
        + f'</main><script>{script}</script></body></html>\n'
    )
    (out / "index.html").write_text(html)


def build_pdfs(data, out):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable

    candidates = [
        (Path("/System/Library/Fonts/Supplemental/Arial.ttf"), Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
    ]
    fonts = next(((regular, bold) for regular, bold in candidates if regular.is_file() and bold.is_file()), None)
    if not fonts:
        raise RuntimeError("A Cyrillic-capable font is required (Arial or DejaVu Sans).")
    pdfmetrics.registerFont(TTFont("CV", str(fonts[0])))
    pdfmetrics.registerFont(TTFont("CV-Bold", str(fonts[1])))
    pdfmetrics.registerFontFamily("CV", normal="CV", bold="CV-Bold", italic="CV", boldItalic="CV-Bold")
    ink, muted, accent, line, deep, copper, peach, impact_bg, impact_line, impact_text = [
        colors.HexColor(PALETTE[key])
        for key in ("ink", "muted", "accent", "line", "deep", "copper", "peach", "impact-bg", "impact-line", "impact-text")
    ]
    style = {
        "name": ParagraphStyle("name", fontName="CV-Bold", fontSize=23, leading=26, textColor=ink, spaceAfter=3),
        "headline": ParagraphStyle("headline", fontName="CV-Bold", fontSize=14, leading=17, textColor=deep, spaceAfter=7),
        "small": ParagraphStyle("small", fontName="CV", fontSize=8.0, leading=10.3, textColor=muted, spaceAfter=4),
        "eyebrow": ParagraphStyle("eyebrow", fontName="CV", fontSize=9.0, leading=11.5, textColor=copper, spaceAfter=4),
        "summary": ParagraphStyle("summary", fontName="CV", fontSize=9.7, leading=12.8, textColor=ink, spaceAfter=7),
        "body": ParagraphStyle("body", fontName="CV", fontSize=9.2, leading=11.9, textColor=ink, spaceAfter=4),
        "compact": ParagraphStyle("compact", fontName="CV", fontSize=8.8, leading=11.2, textColor=ink, spaceAfter=4),
        "bullet": ParagraphStyle("bullet", fontName="CV", fontSize=9.2, leading=11.9, textColor=ink, leftIndent=9, firstLineIndent=-7, spaceAfter=3),
        "section": ParagraphStyle("section", fontName="CV-Bold", fontSize=11.0, leading=13.5, textColor=deep, spaceBefore=10, spaceAfter=6, keepWithNext=True),
        "job": ParagraphStyle("job", fontName="CV-Bold", fontSize=9.8, leading=12.4, textColor=ink, spaceBefore=6, spaceAfter=2, keepWithNext=True),
        "metric": ParagraphStyle("metric", fontName="CV-Bold", fontSize=20, leading=23, textColor=peach, spaceAfter=4),
        "metric_label": ParagraphStyle("metric_label", fontName="CV-Bold", fontSize=8.3, leading=10.4, textColor=impact_text),
    }

    def p(text, which="body"):
        text = str(text).replace("&", "&amp;").replace("—", "-").replace("–", "-").replace("−", "-").replace("→", "->")
        return Paragraph(text, style[which])

    def sec(label):
        return p(label, "section")

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(deep)
        canvas.rect(36, A4[1] - 17, 76, 2.2, stroke=0, fill=1)
        canvas.setFillColor(copper)
        canvas.rect(112, A4[1] - 17, 24, 2.2, stroke=0, fill=1)
        canvas.setStrokeColor(line)
        canvas.setLineWidth(.4)
        canvas.line(36, 30, A4[0] - 36, 30)
        canvas.setFillColor(muted)
        canvas.setFont("CV", 7)
        canvas.drawString(36, 19, "Denis Leonov | AI Product & Technical Lead")
        canvas.drawRightString(A4[0] - 36, 19, str(doc.page))
        canvas.restoreState()

    width = A4[0] - 72
    pdf_dir = out / "output" / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    for lang in ("en", "ru"):
        d = data[lang]
        contact = data["contact"]
        story = [
            p(d["eyebrow"], "eyebrow"), p(d["name"], "name"), p(d["headline"], "headline"),
            p(f'<a href="mailto:{contact["email"]}">{contact["email"]}</a> · <a href="{contact["telegram"]}">Telegram @den_is_lion</a> · <a href="{contact["github"]}">github.com/denisleonov</a>', "small"),
            p(d["location"] + " · " + ("Employment / B2B" if lang == "en" else "Трудоустройство / B2B"), "small"),
            Spacer(1, 5), p(d["summary_pdf"], "summary")
        ]
        metric_labels = (["Watch time", "Artists’ workflow speed", "Localization time", "Peak team size"] if lang == "en" else ["Watch time", "Скорость работы художников", "Время локализации", "Команда на пике"])
        cells = [[p(m["value"], "metric"), p(label, "metric_label")] for m, label in zip(d["metrics"], metric_labels)]
        stats = Table([cells], colWidths=[width / 4] * 4, hAlign="LEFT")
        stats.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), impact_bg),
            ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7), ("LINEABOVE", (0, 0), (-1, -1), .5, peach),
            ("LINEBELOW", (0, 0), (-1, -1), .5, impact_line), ("LINEBEFORE", (1, 0), (-1, -1), .4, impact_line),
        ]))
        story += [stats, Spacer(1, 5), p(f'<b>{d["modalities_line_label"]}:</b> {d["modalities_line"]}', "small")]
        story.append(sec(d["expertise_pdf_title"]))
        for c in d["competencies"]:
            story.append(p(f'<b>{c["pdf_title"]}.</b> {c["pdf"]}', "compact"))
        story.append(sec(d["experience_title"]))
        for r in d["roles"]:
            block = [p(f'{r["company"]} | {r["role"]}', "job"), p(r["date"], "small")]
            block += [p("• " + item, "bullet") for item in r["pdf_bullets"]]
            story.append(KeepTogether(block))
        story.append(PageBreak())
        story += [p(d["name"] + " · " + d["headline"], "small")]
        story.append(sec(d["multimodal_title"]))
        if lang == "en":
            multi = "<b>Production:</b> text, images, video and behavioral data — LLM analytics, Stable Diffusion, 4K deepfake and RecSys. <b>Audio R&D:</b> voice cloning, voice aging, TTS; Whisper/Piper voice MVP. <b>3D R&D:</b> generation experiments and Unity simulation."
        else:
            multi = "<b>Production:</b> текст, изображения, видео, поведенческие данные — LLM-аналитика, Stable Diffusion, 4K deepfake и RecSys. <b>Аудио R&D:</b> клонирование/состаривание голоса и TTS; голосовой MVP Whisper/Piper. <b>3D R&D:</b> генерация и Unity-симуляция."
        story.append(p(multi))
        story += [sec(d["agents_title"]), p(d["agents_pdf"])]
        story.append(sec(d["projects_title"] + " · MVP · 2026"))
        for item in d["projects"]:
            story.append(p(f'<b>{item["title"]}.</b> {item["pdf"]}'))
        story += [sec(d["recognition_title"]), p(d["campaign_pdf"]), p(d["talks"], "compact")]
        story.append(sec(d["other_title"]))
        for item in d["other_roles"][:2]:
            story.append(p(f'<b>{item["company"]} | {item["role"]}</b> · {item["date"]}. {item["text"]}', "compact"))
        for item in d["other_roles"][2:]:
            story.append(p(f'<b>{item["company"]}</b> · {item["role"]} · {item["date"]}', "compact"))
        story.append(p(d["research"], "compact"))
        story += [sec(d["stack_title"]), p(d["stack"], "compact"), sec(d["education_title"])]
        for degree in d["education"]:
            story.append(p(f'<b>{degree["title"]}.</b> {degree["text"]}', "compact"))
        story.append(p(d["languages"], "compact"))
        document = SimpleDocTemplate(
            str(pdf_dir / PDF_NAMES[lang]), pagesize=A4, leftMargin=36, rightMargin=36,
            topMargin=29, bottomMargin=39, title=f'{d["name"]} - AI Product & Technical Lead',
            author="Denis Leonov", subject="AI product leadership, multimodal AI, technical leadership",
        )
        document.build(story, onFirstPage=footer, onLaterPages=footer)
        print(pdf_dir / PDF_NAMES[lang])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html-only", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    args = parser.parse_args()
    data = json.loads((ROOT / "resume.json").read_text())
    assert employment_months(data["employment_periods"]) == 97
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    build_html(data, out)
    if not args.html_only:
        build_pdfs(data, out)
    print(f"Built {out / 'index.html'}; audited employment: 97 distinct calendar months")


if __name__ == "__main__":
    main()
