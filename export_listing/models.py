from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Product(StrictModel):
    product_name: str = Field(min_length=1, max_length=120)
    target_market: str = Field(min_length=1, max_length=120)
    variety: str = Field(default="", max_length=200)
    grade: str = Field(default="", max_length=200)
    volume: str = Field(default="", max_length=200)
    packaging: str = Field(default="", max_length=200)
    origin: str = Field(default="", max_length=200)
    certifications: str = Field(default="", max_length=300)
    shipping_window: str = Field(default="", max_length=200)
    price: str = Field(default="", max_length=200)
    phytosanitary: str = Field(default="", max_length=200)
    shelf_life: str = Field(default="", max_length=200)
    moq: str = Field(default="", max_length=200)
    incoterms: str = Field(default="", max_length=200)


class Spec(StrictModel):
    label: str = Field(min_length=1)
    value: str = Field(min_length=1)


class Listing(StrictModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    specs: list[Spec] = Field(min_length=1)
    selling_points: list[str] = Field(min_length=1, max_length=5)


class Email(StrictModel):
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)


class LanguageDraft(StrictModel):
    listing: Listing
    email: Email


class Drafts(StrictModel):
    en: LanguageDraft
    id: LanguageDraft
    zh: LanguageDraft


class CheckItem(StrictModel):
    item: str
    status: Literal["missing", "provided"]
    note: str


LABELS = {
    "variety": "Variety", "grade": "Grade / size", "volume": "Available volume",
    "packaging": "Packaging", "origin": "Origin", "certifications": "Certifications",
    "shipping_window": "Shipping window", "price": "Price guide (optional)",
    "phytosanitary": "Phytosanitary certificate", "shelf_life": "Shelf life",
    "moq": "Minimum order quantity", "incoterms": "Incoterms",
}


FIELD_GUIDANCE = {
    "variety": "Add the cultivar or botanical variety used on your product documentation.",
    "grade": "Specify the grading standard and size or count, where applicable.",
    "volume": "Give the available quantity and unit, and clarify whether it is per shipment or total supply.",
    "packaging": "Describe the pack type, net weight per pack and packs per pallet if known.",
    "origin": "Specify the growing region and country of origin.",
    "certifications": "List only current certifications you can document; state none if you have none.",
    "shipping_window": "Provide the earliest and latest expected dispatch dates, including the year.",
    "price": "If sharing a price, specify currency, unit and the terms it covers.",
    "phytosanitary": "Confirm documentation requirements with the importer and relevant authority, then record the certificate status.",
    "shelf_life": "Provide a supported shelf-life estimate with storage temperature and the date it is measured from.",
    "moq": "State the smallest order you can supply, with its unit or number of cartons.",
    "incoterms": "Confirm the proposed trade term, named place or port, and version with the buyer.",
}


def checklist(product: Product) -> list[CheckItem]:
    """Completeness is deterministic; supplied details are never verified claims."""
    return [CheckItem(item=label, status="provided" if value else "missing",
                      note=f"Supplied, not verified: {value}" if value else
                      "Not supplied. " + FIELD_GUIDANCE[field])
            for field, label in LABELS.items() if (value := getattr(product, field)) or field != "price"]
