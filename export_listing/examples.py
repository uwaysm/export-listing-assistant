"""Illustrative fixtures, not real supplier inventory or verified export offers."""
from .models import Product, Drafts

EXAMPLES = {
    "WA mangoes": Product(product_name="Mangoes", variety="Kensington Pride", grade="Class 1",
        volume="2,000 kg", packaging="5 kg cartons", origin="Kununurra, Western Australia",
        shipping_window="November–December 2026", target_market="Indonesia"),
    "WA avocados": Product(product_name="Avocados", variety="Hass", grade="Size 20",
        volume="5,000 kg", packaging="4 kg trays", origin="Manjimup, Western Australia",
        shipping_window="November 2026", target_market="Singapore"),
    "WA carrots": Product(product_name="Carrots", variety="Nantes", grade="Medium",
        volume="10,000 kg", packaging="10 kg cartons", origin="Gingin, Western Australia",
        shipping_window="December 2026", target_market="Malaysia"),
    "WA wildflowers": Product(product_name="Cut wildflowers", variety="Waxflower",
        volume="1,000 stems", packaging="Export cartons", origin="Perth, Western Australia",
        shipping_window="September 2027", target_market="China"),
    "WA truffles": Product(product_name="Black truffles", variety="Tuber melanosporum",
        volume="20 kg", packaging="Insulated boxes", origin="Manjimup, Western Australia",
        shipping_window="June–August 2027", target_market="Singapore"),
}

# Demo is deliberately fixed. It cannot masquerade as generation for edited input.
DEMO_PRODUCT = EXAMPLES["WA mangoes"]


def demo_drafts() -> Drafts:
    data = {}
    content = {
        "en": ("Kensington Pride mangoes · Western Australia",
               "Mangoes from Kununurra, Western Australia, with 2,000 kg available for a November–December 2026 shipping window.",
               ["Variety", "Grade", "Volume", "Packaging", "Origin", "Shipping window"],
               ["Kensington Pride variety", "Packed in 5 kg cartons"],
               "Kensington Pride mangoes — enquiry for Indonesia",
               "Dear Purchasing Team,\n\nWe would like to introduce our Kensington Pride mangoes from Kununurra, Western Australia. We have 2,000 kg of Class 1 fruit available in 5 kg cartons, with a shipping window of November–December 2026.\n\nWould this suit your sourcing plans for Indonesia? Please let us know your volume, documentation and delivery requirements so we can discuss pricing and terms.\n\nKind regards,\n[Your name]"),
        "id": ("Mangga Kensington Pride · Australia Barat",
               "Mangga dari Kununurra, Australia Barat, tersedia sebanyak 2,000 kg untuk periode pengiriman November–Desember 2026.",
               ["Varietas", "Kelas", "Volume", "Kemasan", "Asal", "Periode pengiriman"],
               ["Varietas Kensington Pride", "Dikemas dalam karton 5 kg"],
               "Penawaran mangga Kensington Pride untuk Indonesia",
               "Yth. Bapak/Ibu Tim Pengadaan,\n\nKami ingin memperkenalkan mangga Kensington Pride dari Kununurra, Australia Barat. Tersedia 2,000 kg buah Class 1 dalam karton 5 kg, dengan periode pengiriman November–Desember 2026.\n\nApakah produk ini sesuai dengan rencana pengadaan Bapak/Ibu di Indonesia? Mohon informasikan kebutuhan volume, dokumen, dan pengiriman agar kami dapat membahas harga serta ketentuan perdagangan.\n\nHormat kami,\n[Nama Anda]"),
        "zh": ("Kensington Pride 芒果 · 西澳大利亚",
               "产自西澳大利亚库努纳拉的芒果，可供数量为 2,000 kg，计划发货时间为2026年11月至12月。",
               ["品种", "等级", "可供数量", "包装", "产地", "发货时间"],
               ["Kensington Pride 品种", "每箱 5 kg 纸箱包装"],
               "Kensington Pride 芒果供应洽询 — 印度尼西亚市场",
               "尊敬的采购团队：\n\n您好！我们希望向贵司介绍产自西澳大利亚库努纳拉的 Kensington Pride 芒果。目前可供 2,000 kg，等级为 Class 1，采用每箱 5 kg 的纸箱包装，计划于2026年11月至12月发货。\n\n请问该产品是否符合贵司在印度尼西亚市场的采购计划？欢迎告知所需数量、文件及交货要求，以便进一步商讨价格和贸易条款。\n\n此致\n[您的姓名]"),
    }
    for lang, (title, desc, labels, points, subject, body) in content.items():
        values = ["Kensington Pride", "Class 1", "2,000 kg", "5 kg cartons",
                  "Kununurra, Western Australia", "November–December 2026"]
        if lang == "id":
            values[3:] = ["Karton 5 kg", "Kununurra, Australia Barat", "November–Desember 2026"]
        if lang == "zh":
            values[3:] = ["每箱 5 kg 纸箱", "西澳大利亚库努纳拉", "2026年11月至12月"]
        data[lang] = {"listing": {"title": title, "description": desc,
                     "specs": [{"label": k, "value": v} for k, v in zip(labels, values)],
                     "selling_points": points}, "email": {"subject": subject, "body": body}}
    return Drafts.model_validate(data)
