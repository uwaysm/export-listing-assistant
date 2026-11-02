"""Portable, Unicode-safe draft packs with the source facts and review checklist."""
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from .generator import listing_text, email_text
from .models import checklist


def export_pack(product, drafts, is_demo=False):
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        for language in ("en", "id", "zh"):
            draft = getattr(drafts, language)
            archive.writestr(f"{language}/listing.txt", listing_text(draft))
            archive.writestr(f"{language}/buyer-email.txt", email_text(draft))
        archive.writestr("review.html", review_document(product, drafts, is_demo))
        archive.writestr("product-details.json", product.model_dump_json(indent=2))
        archive.writestr("review-checklist.txt", "\n".join(
            f"{item.status.upper()} — {item.item}: {item.note}" for item in checklist(product)))
        archive.writestr("READ-ME.txt", (
            "PREWRITTEN DEMO — Fictional inventory.\n" if is_demo else "AI-GENERATED DRAFT — Review before use.\n"
        ) + "Verify facts, translations and destination requirements before sending.\n"
            "Supplied details are not independently verified. This is not export clearance or legal advice.\n")
    return buffer.getvalue()


def review_document(product, drafts, is_demo=False):
    """Escaped, self-contained HTML: no scripts, fonts, tracking or remote assets."""
    from html import escape
    marker = "Prewritten demo · Fictional inventory" if is_demo else "AI-generated draft · Review before use"
    sections = []
    for lang, label in (("en", "English"), ("id", "Bahasa Indonesia"), ("zh", "简体中文")):
        draft = getattr(drafts, lang)
        sections.append(f'<section lang="{lang}"><h2>{label}</h2><h3>Product listing</h3>'
                        f'<pre>{escape(listing_text(draft))}</pre><h3>Buyer email</h3>'
                        f'<pre>{escape(email_text(draft))}</pre></section>')
    checks = "".join(f'<li><strong>{escape(item.item)} — {item.status}</strong><p>{escape(item.note)}</p></li>'
                     for item in sorted(checklist(product), key=lambda item: item.status != "missing"))
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Export draft review</title><style>'
            'body{font-family:system-ui,sans-serif;max-width:850px;margin:40px auto;padding:24px;color:#24392e}'
            'pre{font:inherit;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.65}'
            'section{border-top:1px solid #ccd6ce;margin-top:32px;padding-top:20px}'
            'p{line-height:1.6}@media print{section{break-before:page}body{margin:0}}'
            '</style><body><h1>Export draft review</h1>'
            f'<p>{marker}</p><p>{escape(product.product_name)} · {escape(product.target_market)}</p>'
            '<p>Verify all facts and translations before sending. Supplied details are not independently verified. '
            'This document is not legal advice or export clearance.</p>'
            + ''.join(sections) + f'<section><h2>Details to review</h2><ul>{checks}</ul></section></body></html>')
