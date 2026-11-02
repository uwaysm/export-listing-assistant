from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from pydantic import ValidationError
from export_listing.examples import EXAMPLES, demo_drafts
from export_listing.generator import GenerationError, generate, listing_text, email_text
from export_listing.models import Drafts, Product, checklist


@pytest.mark.parametrize("product", EXAMPLES.values(), ids=EXAMPLES.keys())
def test_examples_flag_unknown_export_details(product):
    checks = {item.item: item for item in checklist(product)}
    for item in ["Phytosanitary certificate", "Shelf life", "Minimum order quantity", "Incoterms", "Certifications"]:
        assert checks[item].status == "missing"
    assert checks["Available volume"].status == "provided"


def test_supplied_does_not_mean_verified_or_ready():
    product = Product(product_name="Mangoes", target_market="Indonesia", phytosanitary="Not obtained")
    check = next(c for c in checklist(product) if c.item == "Phytosanitary certificate")
    assert check.status == "provided"
    assert check.note == "Supplied, not verified: Not obtained"


def test_whitespace_and_required_fields():
    with pytest.raises(ValidationError):
        Product(product_name="   ", target_market="Indonesia")
    product = Product(product_name="Mangoes", target_market="Indonesia", shelf_life="   ")
    assert next(c for c in checklist(product) if c.item == "Shelf life").status == "missing"


def test_drafts_require_all_languages():
    data = demo_drafts().model_dump()
    del data["zh"]
    with pytest.raises(ValidationError):
        Drafts.model_validate(data)


def test_generated_request_uses_schema_and_disables_storage():
    client = Mock()
    client.responses.parse.return_value = SimpleNamespace(status="completed", output_parsed=demo_drafts())
    result = generate(EXAMPLES["WA mangoes"], "test-key", client=client)
    assert result.zh.email.body
    kwargs = client.responses.parse.call_args.kwargs
    assert kwargs["text_format"] is Drafts
    assert kwargs["store"] is False
    assert '"volume":"2,000 kg"' in kwargs["input"]


def test_invalid_response_retries_once():
    client = Mock()
    client.responses.parse.side_effect = [
        SimpleNamespace(status="completed", output_parsed={}),
        SimpleNamespace(status="completed", output_parsed=demo_drafts()),
    ]
    assert generate(EXAMPLES["WA mangoes"], "test-key", client=client).en.listing.title
    assert client.responses.parse.call_count == 2


def test_two_invalid_responses_stop():
    client = Mock()
    client.responses.parse.return_value = SimpleNamespace(status="completed", output_parsed={})
    with pytest.raises(GenerationError):
        generate(EXAMPLES["WA mangoes"], "test-key", client=client)
    assert client.responses.parse.call_count == 2


@pytest.mark.parametrize("status,parsed", [("incomplete", None), ("completed", None)])
def test_refusal_or_incomplete_does_not_render(status, parsed):
    client = Mock()
    client.responses.parse.return_value = SimpleNamespace(status=status, output_parsed=parsed)
    with pytest.raises(GenerationError):
        generate(EXAMPLES["WA mangoes"], "test-key", client=client)
    assert client.responses.parse.call_count == 1


def test_plain_text_exports_include_specs_and_email():
    for lang in ["en", "id", "zh"]:
        draft = getattr(demo_drafts(), lang)
        assert "2,000 kg" in listing_text(draft)
        assert draft.email.subject in email_text(draft)
        assert draft.email.body in email_text(draft)


def test_complete_pack_preserves_chinese_and_source_facts():
    from io import BytesIO
    from zipfile import ZipFile
    from export_listing.exports import export_pack
    product = EXAMPLES["WA mangoes"]
    with ZipFile(BytesIO(export_pack(product, demo_drafts(), True))) as archive:
        assert len(archive.namelist()) == 10
        assert "尊敬" in archive.read("zh/buyer-email.txt").decode("utf-8")
        assert "PREWRITTEN DEMO" in archive.read("READ-ME.txt").decode()
        assert Product.model_validate_json(archive.read("product-details.json")) == product
        assert "MISSING" in archive.read("review-checklist.txt").decode()


def test_review_document_escapes_untrusted_input():
    from export_listing.exports import review_document
    product = Product(product_name="<script>alert(1)</script>", target_market="Indonesia")
    html = review_document(product, demo_drafts(), True)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert 'lang="zh"' in html
    assert "Fictional inventory" in html


def test_missing_fields_have_specific_actions():
    product = Product(product_name="Mangoes", target_market="Indonesia")
    notes = {c.item: c.note for c in checklist(product)}
    assert "storage temperature" in notes["Shelf life"]
    assert "named place or port" in notes["Incoterms"]
