from app.services.expansion_service import MedicalExpansionService


def test_medical_expansion_disabled():
    service = MedicalExpansionService(enabled=False)
    expanded = service.expand_query("hypertension treatment")
    assert expanded == "hypertension treatment"


def test_medical_expansion_enabled():
    service = MedicalExpansionService(enabled=True)
    
    # Test single medical term
    expanded1 = service.expand_query("hypertension")
    assert "hypertension" in expanded1
    assert "high blood pressure" in expanded1

    # Test multi-word term
    expanded2 = service.expand_query("myocardial infarction")
    assert "heart attack" in expanded2

    # Query with non-medical terms
    expanded3 = service.expand_query("random ordinary query")
    assert expanded3 == "random ordinary query"
