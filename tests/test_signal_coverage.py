"""Coverage and fan-out.

Every case here is one that actually went wrong on a live campaign, not an invented
edge. The names are synthetic; the shapes are not.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "enrich-contacts" / "scripts" / "check_signal_coverage.py"

spec = importlib.util.spec_from_file_location("check_signal_coverage", SCRIPT)
csc = importlib.util.module_from_spec(spec)
sys.modules["check_signal_coverage"] = csc
spec.loader.exec_module(csc)


def person(rid, name, title="Architect"):
    return {"recipient_id": rid, "full_name": name, "title": title}


def signal(fact, for_person=csc.ALL, recipient_id="", **kw):
    s = {"fact": fact, "for_person": for_person, "date": "2026-05",
         "date_confidence": "month", "type": "milestone",
         "source_url": "https://example.com/news", "angle": "x"}
    if recipient_id:
        s["recipient_id"] = recipient_id
    s.update(kw)
    return s


# --------------------------------------------------------------- norm_person

def test_norm_person_drops_parentheticals():
    """The bug that scored a contact with four signals as having none."""
    assert (csc.norm_person("Dana Vell (person behind a shared inbox - see note)")
            == csc.norm_person("Dana Vell (Founder & Director, MCIAT)")
            == "danavell")


def test_norm_person_ignores_case_punctuation_and_spacing():
    assert csc.norm_person("anne-marie ostrow") == csc.norm_person("Anne Marie Ostrow")


def test_norm_person_still_separates_different_people():
    assert csc.norm_person("Mira Penvale") != csc.norm_person("Mira Penfold")


def test_norm_person_handles_missing_name():
    assert csc.norm_person(None) == ""
    assert csc.norm_person("") == ""


# --------------------------------------------------------------- scope

def test_scope_company_wide_when_source_names_only_the_firm():
    p = person("R-1", "Priya Raman")
    assert csc.signal_scope(signal("Opened a depot"), p) == "company-wide"


def test_blank_for_person_is_company_wide_not_person_specific():
    """A missing field must fail safe. Reading it as person-specific would licence
    copy that says the recipient personally did the thing."""
    p = person("R-1", "Priya Raman")
    assert csc.signal_scope(signal("Opened a depot", for_person=""), p) == "company-wide"


def test_scope_person_specific_when_source_names_them():
    p = person("R-1", "Priya Raman")
    assert csc.signal_scope(signal("Gave a talk", for_person="Priya Raman"), p) == "person-specific"


def test_scope_colleague_when_source_names_someone_else():
    p = person("R-1", "Priya Raman")
    assert csc.signal_scope(signal("Gave a talk", for_person="Jon Fell"), p) == "colleague"


# --------------------------------------------------------------- coverage

def test_company_signal_shared_by_three_is_one_fact_not_three():
    """The defect this whole module exists for."""
    records = [{
        "company": "Ostvale",
        "people": [person("R-1", "A One"), person("R-2", "B Two"), person("R-3", "C Three")],
        "signals": [signal("Opened a second depot")],
    }]
    contacts, firms, _ = csc.coverage(records)
    assert [c["verdict"] for c in contacts] == ["company only"] * 3
    assert firms[0] == {"company": "Ostvale", "contacts": 3, "touches": 1,
                        "facts_needed": 3, "distinct_facts": 1, "shortfall": 2}


def test_three_distinct_facts_for_three_people_is_no_shortfall():
    records = [{
        "company": "Ostvale",
        "people": [person("R-1", "A One"), person("R-2", "B Two"), person("R-3", "C Three")],
        "signals": [signal("Fact one", for_person="A One"),
                    signal("Fact two", for_person="B Two"),
                    signal("Fact three", for_person="C Three")],
    }]
    contacts, firms, _ = csc.coverage(records)
    assert [c["verdict"] for c in contacts] == ["about them"] * 3
    assert firms[0]["shortfall"] == 0


def test_repeating_one_fact_under_three_names_does_not_clear_the_shortfall():
    """Distinct facts, not signal rows. Filing the same sentence three times is the
    obvious way to make a shortfall disappear on paper without doing any research."""
    records = [{
        "company": "Ostvale",
        "people": [person("R-1", "A One"), person("R-2", "B Two"), person("R-3", "C Three")],
        "signals": [signal("Opened a second depot", for_person="A One"),
                    signal("Opened a second depot", for_person="B Two"),
                    signal("Opened a second depot", for_person="C Three")],
    }]
    _, firms, _ = csc.coverage(records)
    assert firms[0]["distinct_facts"] == 1
    assert firms[0]["shortfall"] == 2


def test_colleague_only_is_distinguished_from_nothing():
    """These need different follow-up: one firm published and missed a person, the
    other published nothing at all. Collapsing them hides which is which."""
    records = [{
        "company": "Ostvale",
        "people": [person("R-1", "A One"), person("R-2", "B Two")],
        "signals": [signal("Gave a talk", for_person="A One")],
    }, {
        "company": "Quernvale",
        "people": [person("R-3", "C Three")],
        "signals": [],
    }]
    contacts, _, _ = csc.coverage(records)
    verdicts = {c["full_name"]: c["verdict"] for c in contacts}
    assert verdicts == {"A One": "about them", "B Two": "colleague only", "C Three": "nothing"}


def test_recipient_id_scopes_a_signal_to_one_person():
    records = [{
        "company": "Ostvale",
        "people": [person("R-1", "A One"), person("R-2", "B Two")],
        "signals": [signal("Won a contract", recipient_id="R-1")],
    }]
    contacts, _, _ = csc.coverage(records)
    verdicts = {c["full_name"]: c["verdict"] for c in contacts}
    assert verdicts == {"A One": "company only", "B Two": "nothing"}


def test_signal_with_no_recipient_id_reaches_everyone_at_the_firm():
    records = [{
        "company": "Ostvale",
        "people": [person("R-1", "A One"), person("R-2", "B Two")],
        "signals": [signal("Won a contract")],
    }]
    contacts, _, _ = csc.coverage(records)
    assert all(c["verdict"] == "company only" for c in contacts)


def test_parenthetical_name_still_matches_its_signal_end_to_end():
    """Regression: the live failure, through the full path rather than the helper."""
    records = [{
        "company": "Ravensby Architecture",
        "people": [person("R-1", "Dana Vell (person behind a shared inbox - see note)")],
        "signals": [signal("Dana Vell spoke at a conference",
                           for_person="Dana Vell (Founder & Director, MCIAT)")],
    }]
    contacts, _, _ = csc.coverage(records)
    assert contacts[0]["verdict"] == "about them"
    assert contacts[0]["person_specific"] == 1


def test_firm_with_no_people_does_not_crash_or_report_a_shortfall():
    contacts, firms, _ = csc.coverage([{"company": "Ostvale", "people": [], "signals": []}])
    assert contacts == []
    assert firms[0]["shortfall"] == 0


def test_missing_people_and_signals_keys_are_tolerated():
    """Records arrive from a research agent, not a schema validator."""
    contacts, firms, _ = csc.coverage([{"company": "Ostvale"}])
    assert contacts == []
    assert firms[0]["distinct_facts"] == 0


def test_blank_facts_are_not_counted_as_distinct():
    records = [{
        "company": "Ostvale",
        "people": [person("R-1", "A One"), person("R-2", "B Two")],
        "signals": [signal("Real fact"), signal(""), signal("   ")],
    }]
    _, firms, _ = csc.coverage(records)
    assert firms[0]["distinct_facts"] == 1


# --------------------------------------------------------------- cli

def test_strict_exits_nonzero_on_a_shortfall(tmp_path, monkeypatch, capsys):
    p = tmp_path / "records.json"
    p.write_text(json.dumps([{
        "company": "Ostvale",
        "people": [person("R-1", "A One"), person("R-2", "B Two")],
        "signals": [signal("One fact for two people")],
    }]))
    monkeypatch.setattr(sys, "argv", ["x", str(p), "--strict"])
    assert csc.main() == 1
    assert "short of one fact per contact: 1" in capsys.readouterr().out


def test_strict_exits_zero_when_every_contact_has_a_fact(tmp_path, monkeypatch):
    p = tmp_path / "records.json"
    p.write_text(json.dumps([{
        "company": "Ostvale",
        "people": [person("R-1", "A One")],
        "signals": [signal("A fact", for_person="A One")],
    }]))
    monkeypatch.setattr(sys, "argv", ["x", str(p), "--strict"])
    assert csc.main() == 0


def test_csv_export_carries_every_coverage_column(tmp_path, monkeypatch):
    p = tmp_path / "records.json"
    out = tmp_path / "cov.csv"
    p.write_text(json.dumps([{
        "company": "Ostvale",
        "people": [person("R-1", "A One")],
        "signals": [signal("A fact", for_person="A One")],
    }]))
    monkeypatch.setattr(sys, "argv", ["x", str(p), "--csv", str(out)])
    csc.main()
    rows = list(__import__("csv").DictReader(open(out)))
    assert rows[0]["verdict"] == "about them"
    assert set(rows[0]) == {"company", "recipient_id", "full_name", "title",
                            "person_specific", "company_wide", "colleague", "verdict"}


def test_runs_against_the_shipped_example(tmp_path, monkeypatch, capsys):
    """The examples predate for_person, so every signal must read company-wide -
    which is the correct fail-safe, and proves the field is genuinely optional."""
    monkeypatch.setattr(sys, "argv", ["x", str(REPO / "examples" / "enriched.example.json")])
    assert csc.main() == 0
    out = capsys.readouterr().out
    assert "about them        : 0" in out
    assert "company only      : 3" in out


@pytest.mark.parametrize("wrapper", [
    lambda r: r,
    lambda r: {"records": r},
    lambda r: {"companies": r},
])
def test_accepts_a_bare_list_or_either_wrapper(tmp_path, monkeypatch, wrapper):
    p = tmp_path / "records.json"
    p.write_text(json.dumps(wrapper([{
        "company": "Ostvale",
        "people": [person("R-1", "A One")],
        "signals": [signal("A fact", for_person="A One")],
    }])))
    monkeypatch.setattr(sys, "argv", ["x", str(p)])
    assert csc.main() == 0


# --------------------------------------------------------------- duplicate records

def test_one_firm_split_across_two_records_is_pooled_not_double_penalised():
    """Live defect: Marrowby arrived as two records, four contacts each, two facts and
    three facts. Scored separately both halves reported a shortfall; pooled, the firm
    has five facts for four people and is fine. Scoring per record invented 37 such
    shortfalls on a single run."""
    records = [
        {"company": "Marrowby",
         "people": [person("R-1", "A One"), person("R-2", "B Two")],
         "signals": [signal("Fact one"), signal("Fact two")]},
        {"company": "Marrowby (Marrowby Design Partnership Limited)",
         "people": [person("R-1", "A One"), person("R-2", "B Two")],
         "signals": [signal("Fact three")]},
    ]
    _, firms, merged = csc.coverage(records)
    assert len(firms) == 1
    assert firms[0]["contacts"] == 2
    assert firms[0]["distinct_facts"] == 3
    assert firms[0]["shortfall"] == 0
    assert merged == [sorted(["Marrowby", "Marrowby (Marrowby Design Partnership Limited)"])]


def test_pooling_keeps_the_longer_company_name():
    records = [
        {"company": "Halbrook", "people": [person("R-1", "A One")], "signals": []},
        {"company": "Halbrook (Halbrook Design Limited)", "people": [person("R-1", "A One")],
         "signals": [signal("A fact")]},
    ]
    _, firms, _ = csc.coverage(records)
    assert firms[0]["company"] == "Halbrook (Halbrook Design Limited)"


def test_genuinely_different_firms_are_not_pooled():
    records = [
        {"company": "Penhale Architects Ltd", "people": [person("R-1", "A One")],
         "signals": [signal("A fact")]},
        {"company": "Ivelet Architects", "people": [person("R-2", "B Two")],
         "signals": [signal("Another fact")]},
    ]
    _, firms, merged = csc.coverage(records)
    assert len(firms) == 2
    assert merged == []


def test_norm_company_ignores_legal_suffixes_and_punctuation():
    assert (csc.norm_company("Trenmere Architects Ltd")
            == csc.norm_company("Trenmere Architects (Trenmere Ltd)")
            == csc.norm_company("trenmere-architects"))


def test_norm_company_is_deliberately_conservative_about_industry_words():
    """It strips legal suffixes, not trade words. Stripping "Architects" would merge
    "Ashkirk Architects" into "Dow Jones", and a false merge is worse than a missed
    one: it pools two firms' facts and hides a real shortfall behind a stranger's news.
    A missed merge only costs an unshown warning."""
    assert csc.norm_company("Ashkirk Architects") != csc.norm_company("Ashkirk Ltd")


def test_norm_company_does_not_collapse_two_real_firms():
    assert csc.norm_company("Ashkirk Architects") != csc.norm_company("Jones Architects")


def test_pooled_shortfall_counts_a_firm_with_no_facts_at_all():
    """A firm with one contact and nothing found is short by one. Reporting only the
    partially-covered firms hid 37 of the 48 real shortfalls on the live run."""
    _, firms, _ = csc.coverage([{"company": "Silent Ltd",
                                 "people": [person("R-1", "A One")], "signals": []}])
    assert firms[0]["shortfall"] == 1


def test_merged_firms_are_named_in_the_report(capsys):
    records = [
        {"company": "Marrowby", "people": [person("R-1", "A One")], "signals": [signal("f1")]},
        {"company": "Marrowby Limited", "people": [person("R-1", "A One")],
         "signals": [signal("f2")]},
    ]
    contacts, firms, merged = csc.coverage(records)
    csc.report(contacts, firms, merged)
    out = capsys.readouterr().out
    assert "pooled before scoring: 1" in out
    assert "Marrowby + Marrowby Limited" in out


# --------------------------------------------------------------- touches

def test_two_touches_double_what_a_firm_must_produce():
    """The second axis. One fact each is enough for one video and not for two, and a
    campaign that only checks the colleague axis finds out at assembly time - when the
    research is over."""
    records = [{
        "company": "Ostvale",
        "people": [person("R-1", "A One"), person("R-2", "B Two")],
        "signals": [signal("Fact one", for_person="A One"),
                    signal("Fact two", for_person="B Two")],
    }]
    _, one, _ = csc.coverage(records, touches=1)
    _, two, _ = csc.coverage(records, touches=2)
    assert one[0]["facts_needed"] == 2 and one[0]["shortfall"] == 0
    assert two[0]["facts_needed"] == 4 and two[0]["shortfall"] == 2


def test_touches_defaults_to_one_so_existing_callers_are_unchanged():
    records = [{"company": "Ostvale", "people": [person("R-1", "A One")],
                "signals": [signal("A fact", for_person="A One")]}]
    _, firms, _ = csc.coverage(records)
    assert firms[0]["touches"] == 1 and firms[0]["shortfall"] == 0


def test_enough_facts_for_two_touches_is_no_shortfall():
    records = [{
        "company": "Ostvale",
        "people": [person("R-1", "A One")],
        "signals": [signal("Fact one", for_person="A One"),
                    signal("Fact two", for_person="A One")],
    }]
    _, firms, _ = csc.coverage(records, touches=2)
    assert firms[0]["shortfall"] == 0


def test_the_shortfall_total_is_labelled_as_facts_not_people():
    """With touches > 1 one person can account for several missing facts, so calling
    the total 'contacts' overstates it."""
    records = [{"company": "Ostvale", "people": [person("R-1", "A One")],
                "signals": []}]
    contacts, firms, merged = csc.coverage(records, touches=3)
    import io
    buf = io.StringIO()
    csc.report(contacts, firms, merged, out=buf, touches=3)
    assert "distinct facts still needed: 3" in buf.getvalue()


def test_the_report_names_both_axes(capsys):
    records = [{"company": "Ostvale",
                "people": [person("R-1", "A One"), person("R-2", "B Two")],
                "signals": [signal("Only fact")]}]
    contacts, firms, merged = csc.coverage(records, touches=2)
    csc.report(contacts, firms, merged, touches=2)
    out = capsys.readouterr().out
    assert "2 facts per contact" in out
    assert "2 contacts x 2 touches = 4 needed / 1 found" in out


def test_cli_touches_flag_changes_the_verdict(tmp_path, monkeypatch):
    p = tmp_path / "records.json"
    p.write_text(json.dumps([{
        "company": "Ostvale",
        "people": [person("R-1", "A One")],
        "signals": [signal("A fact", for_person="A One")],
    }]))
    monkeypatch.setattr(sys, "argv", ["x", str(p), "--strict"])
    assert csc.main() == 0
    monkeypatch.setattr(sys, "argv", ["x", str(p), "--touches", "2", "--strict"])
    assert csc.main() == 1


def test_touches_below_one_is_rejected(tmp_path, monkeypatch):
    p = tmp_path / "records.json"
    p.write_text(json.dumps([{"company": "Ostvale", "people": [], "signals": []}]))
    monkeypatch.setattr(sys, "argv", ["x", str(p), "--touches", "0"])
    with pytest.raises(SystemExit):
        csc.main()


# --------------------------------------------------------------- reserved types

def test_direction_and_stack_rows_do_not_count_toward_fan_out():
    """They feed canvas L and M, not the triggering event. Counting them would say a
    firm can fill three videos when it has one event and two context rows."""
    records = [{
        "company": "Ostvale",
        "people": [person("R-1", "A One"), person("R-2", "B Two")],
        "signals": [signal("A real event", for_person="A One"),
                    signal("Stated goal to double the fleet", type="direction"),
                    signal("Runs SAP and a bespoke WMS", type="stack & market")],
    }]
    _, firms, _ = csc.coverage(records)
    assert firms[0]["distinct_facts"] == 1
    assert firms[0]["shortfall"] == 1


def test_relationship_rows_do_not_count_toward_fan_out():
    """They feed canvas K. A firm with one event and one customer relationship still
    has one event to spread across its people, not two."""
    records = [{
        "company": "Ostvale",
        "people": [person("R-1", "A One"), person("R-2", "B Two")],
        "signals": [signal("A real event", for_person="A One"),
                    signal("Customer since 2024, per the CRM export", type="relationship",
                           source_url="", supplied_by_customer="yes")],
    }]
    _, firms, _ = csc.coverage(records)
    assert firms[0]["distinct_facts"] == 1
    assert firms[0]["shortfall"] == 1


def test_is_event_is_case_and_space_tolerant():
    assert not csc.is_event({"type": " Direction "})
    assert not csc.is_event({"type": "STACK & MARKET"})
    assert not csc.is_event({"type": "Relationship"})
    assert csc.is_event({"type": "project milestone"})
    assert csc.is_event({})


def test_reserved_types_still_count_as_coverage_for_the_person():
    """Excluded from fan-out, but they are still signal about that person's firm and
    the coverage verdict should say so."""
    records = [{"company": "Ostvale", "people": [person("R-1", "A One")],
                "signals": [signal("Stated goal", type="direction")]}]
    contacts, _, _ = csc.coverage(records)
    assert contacts[0]["verdict"] == "company only"
