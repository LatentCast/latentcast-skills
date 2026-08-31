"""Tests for build_canvas.py.

The load-bearing one is test_welcome_is_V_and_cta_is_W. Older templates put Welcome at S
and CTA at T; following those writes narrative copy into an image URL column with no error
raised, and you find out when the videos render.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
from openpyxl import load_workbook

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills" / "build-personalization-canvas" / "scripts" / "build_canvas.py"

spec = importlib.util.spec_from_file_location("build_canvas", SCRIPT)
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)


def a_row(**over):
    row = {
        "full_name": "Priya Raman",
        "email": "priya.raman@ostvale.example.com",
        "title": "VP Supply Chain",
        "company": "Ostvale Provisions",
        "industry": "Food distribution",
        "country": "Netherlands",
        "triggering_event": "Just opened a second distribution centre in Rotterdam.",
        "strategic_priorities": "Expanding beyond the Benelux into Germany and Denmark.",
        "relevance_signals": "Own fleet, in-house planners, no dynamic routing yet.",
        "welcome_message": "Priya, congrats on the Rotterdam site.",
        "cta_message": "Priya, worth 20 minutes? cal.example.com/haldenbrook/20min",
        "rep_email": "sam@haldenbrook.example",
        "rep_first_name": "Sam",
        "rep_last_name": "Rivera",
    }
    row.update(over)
    return row


def build_to(tmp_path, rows, **kw):
    out = tmp_path / "canvas.xlsx"
    n, warnings = bc.build(rows, out, **kw)
    return load_workbook(out), warnings


def run_cli(tmp_path, rows, *flags):
    rows_path = tmp_path / "rows.json"
    rows_path.write_text(json.dumps(rows), encoding="utf-8")
    out = tmp_path / "out.xlsx"
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(rows_path), str(out), *flags],
        capture_output=True, text=True,
    )


# --- format ---------------------------------------------------------------

def test_sheet_name_and_column_count(tmp_path):
    wb, _ = build_to(tmp_path, [a_row()])
    ws = wb["Personalization Canvas"]
    assert ws.max_column == 26
    assert [c.value for c in ws[2]][:3] == ["Recipient ID", "Full Name", "Email"]


def test_welcome_is_V_and_cta_is_W(tmp_path):
    """The v5/v6 letter trap. S is Closing Scene Image, T is VO Language."""
    wb, _ = build_to(tmp_path, [a_row(closing_scene_image="ostvale-closing.png")])
    ws = wb["Personalization Canvas"]
    assert ws["V2"].value == "Welcome Message"
    assert ws["W2"].value == "CTA Message"
    assert ws["S2"].value == "Closing Scene Image"
    assert ws["T2"].value == "VO Language / Locale"
    assert ws["V4"].value.startswith("Priya, congrats")
    assert ws["W4"].value.startswith("Priya, worth 20 minutes")
    assert ws["S4"].value == "ostvale-closing.png"
    assert ws["T2"].value == "VO Language / Locale"


def test_recipient_id_autogenerates(tmp_path):
    wb, _ = build_to(tmp_path, [a_row(), a_row()])
    ws = wb["Personalization Canvas"]
    assert ws["A4"].value == "R-0001"
    assert ws["A5"].value == "R-0002"


def test_spoken_fallbacks(tmp_path):
    wb, _ = build_to(tmp_path, [a_row()])
    ws = wb["Personalization Canvas"]
    assert ws["H4"].value == "Priya"
    assert ws["I4"].value == "Ostvale Provisions"


# --- rep gate -------------------------------------------------------------

def test_blank_rep_is_a_hard_failure(tmp_path):
    rows = [a_row(rep_email="", rep_first_name="", rep_last_name="")]
    result = run_cli(tmp_path, rows)
    assert result.returncode == 2
    assert "no rep on rows 4" in result.stderr
    assert not (tmp_path / "out.xlsx").exists()


def test_allow_blank_rep_lets_it_through(tmp_path):
    rows = [a_row(rep_email="", rep_first_name="", rep_last_name="")]
    result = run_cli(tmp_path, rows, "--allow-blank-rep")
    assert result.returncode == 0
    assert (tmp_path / "out.xlsx").exists()


# --- toggles --------------------------------------------------------------

def test_toggle_override_by_letter(tmp_path):
    wb, _ = build_to(tmp_path, [a_row()], toggles={"P": "OFF", "Q": "OFF"})
    ws = wb["Personalization Canvas"]
    assert ws["P3"].value == "OFF"
    assert ws["Q3"].value == "OFF"
    assert ws["R3"].value == "ON"
    assert ws["A3"].value == "USE FOR PERSONALIZATION →"


def test_toggle_override_by_numeric_string(tmp_path):
    wb, _ = build_to(tmp_path, [a_row()], toggles={"16": "OFF"})
    assert wb["Personalization Canvas"]["P3"].value == "OFF"


def test_toggle_outside_band_is_refused(tmp_path):
    with pytest.raises(bc.CanvasValidationError):
        build_to(tmp_path, [a_row()], toggles={1: "OFF"})


def test_out_of_vocabulary_toggle_is_refused(tmp_path):
    with pytest.raises(bc.CanvasValidationError):
        build_to(tmp_path, [a_row()], toggles={"P": "maybe"})


# --- hygiene and validation ----------------------------------------------

def test_control_characters_are_stripped_not_raised(tmp_path):
    dirty = "Opened a second\x07 distribution centre\x00 in Rotterdam."
    wb, _ = build_to(tmp_path, [a_row(triggering_event=dirty)])
    assert wb["Personalization Canvas"]["J4"].value == (
        "Opened a second distribution centre in Rotterdam.")


def test_html_entities_are_unescaped(tmp_path):
    wb, _ = build_to(tmp_path, [a_row(company="Ben &amp; Jerry&#39;s")])
    assert wb["Personalization Canvas"]["E4"].value == "Ben & Jerry's"


def test_unknown_row_key_warns(tmp_path):
    _, warnings = build_to(tmp_path, [a_row(ctaMessage="oops")])
    assert any("unrecognised row keys" in w and "ctaMessage" in w for w in warnings)


def test_formula_prefix_warns(tmp_path):
    _, warnings = build_to(tmp_path, [a_row(welcome_message="=SUM(A1:A2)")])
    assert any("formula character" in w for w in warnings)


def test_unfilled_placeholder_warns(tmp_path):
    _, warnings = build_to(tmp_path, [a_row(welcome_message="Congrats on [Company] news.")])
    assert any("placeholder" in w for w in warnings)


def test_blank_narrative_cell_names_the_row(tmp_path):
    _, warnings = build_to(tmp_path, [a_row(), a_row(cta_message="")])
    assert any("W cta_message is toggled ON but blank on rows 5" in w for w in warnings)


def test_empty_rows_is_an_error(tmp_path):
    with pytest.raises(bc.CanvasValidationError):
        build_to(tmp_path, [])


def test_blank_cell_warns_while_its_toggle_is_on(tmp_path):
    _, warnings = build_to(tmp_path, [a_row()])
    assert any("logo_image is toggled ON but blank" in w for w in warnings)


def test_blank_cell_is_silent_once_its_toggle_is_off(tmp_path):
    """Turning a dimension OFF is how a campaign says it is not using it."""
    _, warnings = build_to(tmp_path, [a_row()],
                           toggles={"P": "OFF", "Q": "OFF", "R": "OFF", "S": "OFF"})
    assert not any("image is toggled ON" in w for w in warnings)


def test_blank_cell_is_silent_under_deduct_from_context(tmp_path):
    """Deduct from Context means LatentCast picks the value, so blank is correct."""
    _, warnings = build_to(tmp_path, [a_row()], toggles={"N": "Deduct from Context"})
    assert not any("attire_color" in w for w in warnings)


# --- identity columns A-G -------------------------------------------------

def test_blank_email_is_a_hard_failure(tmp_path):
    """Column C is required and the platform does not accept a blank one."""
    result = run_cli(tmp_path, [a_row(email="")])
    assert result.returncode == 2
    assert "identity columns A to G are required" in result.stderr
    assert "email" in result.stderr
    assert not (tmp_path / "out.xlsx").exists()


def test_allow_incomplete_downgrades_identity_to_a_warning(tmp_path):
    result = run_cli(tmp_path, [a_row(email="")], "--allow-incomplete")
    assert result.returncode == 0
    assert (tmp_path / "out.xlsx").exists()


def test_every_identity_column_is_checked(tmp_path):
    for key in ("full_name", "email", "title", "company", "industry", "country"):
        with pytest.raises(bc.CanvasValidationError) as exc:
            build_to(tmp_path, [a_row(**{key: ""})])
        assert key in str(exc.value)


# --- per-column toggle vocabularies ---------------------------------------

def test_deduct_from_context_is_rejected_where_it_is_not_offered(tmp_path):
    """Only N, O, V and W offer it. P is imagery, ON/OFF only."""
    with pytest.raises(bc.CanvasValidationError) as exc:
        build_to(tmp_path, [a_row()], toggles={"P": "Deduct from Context"})
    assert "not valid" in str(exc.value)


def test_language_is_accepted_only_on_subtitles(tmp_path):
    wb, _ = build_to(tmp_path, [a_row(subtitles="en-GB")], toggles={"U": "LANGUAGE"})
    assert wb["Personalization Canvas"]["U3"].value == "LANGUAGE"
    assert wb["Personalization Canvas"]["U4"].value == "en-GB"
    with pytest.raises(bc.CanvasValidationError):
        build_to(tmp_path, [a_row()], toggles={"T": "LANGUAGE"})


def test_a_cell_value_in_a_toggle_is_refused(tmp_path):
    """The category error the spec warns about: N takes a state, not a colour."""
    with pytest.raises(bc.CanvasValidationError) as exc:
        build_to(tmp_path, [a_row()], toggles={"N": "Navy"})
    assert "not valid for attire_color" in str(exc.value)


def test_template_default_toggles_are_all_on(tmp_path):
    """The distributed template ships every dimension ON."""
    wb, _ = build_to(tmp_path, [a_row()])
    ws = wb["Personalization Canvas"]
    assert {ws.cell(row=3, column=c).value for c in range(8, 27)} == {"ON"}


# --- imagery is a library filename, not a URL -----------------------------

def test_url_in_an_imagery_cell_warns(tmp_path):
    _, warnings = build_to(tmp_path, [a_row(logo_image="https://x.example/logo.png")])
    assert any("looks like a URL" in w for w in warnings)


def test_a_library_filename_is_accepted_quietly(tmp_path):
    _, warnings = build_to(tmp_path, [a_row(logo_image="ostvale-logo.png")])
    assert not any("logo_image" in w for w in warnings)


# --- cli ------------------------------------------------------------------

def test_strict_promotes_warnings_to_exit_1(tmp_path):
    result = run_cli(tmp_path, [a_row(ctaMessage="oops")], "--strict")
    assert result.returncode == 1
    assert (tmp_path / "out.xlsx").exists()


def test_clean_run_exits_0_and_reports_versions(tmp_path):
    rows = [a_row(logo_image="ostvale-logo.png",
                  opening_scene_image="ostvale-opening.png",
                  context_scene_image="ostvale-context.png",
                  closing_scene_image="ostvale-closing.png",
                  attire_color="Navy", subtitles="en-GB",
                  clothing_style="Business smart (blazer, no tie)",
                  vo_language="English (UK)",
                  relationship_context="Cold prospect, no prior contact")]
    result = run_cli(tmp_path, rows)
    assert result.returncode == 0, result.stderr
    assert "canvas template v6" in result.stdout
    assert result.stderr == ""


def test_missing_file_exits_2(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path / "nope.json"), str(tmp_path / "o.xlsx")],
        capture_output=True, text=True)
    assert result.returncode == 2


# --- --omit-unused -----------------------------------------------------------------

OFF_IMAGERY = "P=OFF,Q=OFF,R=OFF,S=OFF,U=OFF,N=Deduct from Context"


def test_omit_unused_is_off_by_default(tmp_path):
    """The default must stay a full 26-column canvas."""
    wb, _w = build_to(tmp_path, [a_row()], toggles=bc.parse_toggle_arg(OFF_IMAGERY))
    ws = wb["Personalization Canvas"]
    assert ws.max_column == 26


def test_omit_unused_drops_only_off_and_empty_columns(tmp_path):
    wb, _w = build_to(tmp_path, [a_row()], toggles=bc.parse_toggle_arg(OFF_IMAGERY),
                      omit_unused=True)
    ws = wb["Personalization Canvas"]
    headers = [ws.cell(row=2, column=i).value for i in range(1, ws.max_column + 1)]
    for gone in ("Logo Image", "Opening Scene Image", "Context Scene Image",
                 "Closing Scene Image", "Subtitles"):
        assert gone not in headers, gone
    # "Deduct from Context" is blank because the platform fills it, so it must survive
    assert "Attire Color" in headers
    assert ws.max_column == 21


def test_omit_unused_never_drops_identity_or_rep(tmp_path):
    """Even toggled OFF and empty, these must ship: A-G are required, X-Z are the casting key."""
    every_off = ",".join(f"{c}=OFF" for c in "HIJKLMNOPQRSTUVWXYZ")
    wb, _w = build_to(tmp_path, [a_row()], toggles=bc.parse_toggle_arg(every_off),
                      omit_unused=True)
    ws = wb["Personalization Canvas"]
    headers = [ws.cell(row=2, column=i).value for i in range(1, ws.max_column + 1)]
    for required in ("Recipient ID", "Full Name", "Email", "Title / Role", "Company",
                     "Industry", "Country", "Rep Email", "Rep First Name", "Rep Last Name"):
        assert required in headers, required


def test_omit_unused_keeps_a_column_that_has_data(tmp_path):
    """OFF but populated is a contradiction the caller should see, not something to delete."""
    wb, _w = build_to(tmp_path, [a_row(logo_image="northwind-logo.png")],
                      toggles=bc.parse_toggle_arg(OFF_IMAGERY), omit_unused=True)
    ws = wb["Personalization Canvas"]
    headers = [ws.cell(row=2, column=i).value for i in range(1, ws.max_column + 1)]
    assert "Logo Image" in headers


def test_omit_unused_renumbers_without_gaps(tmp_path):
    wb, _w = build_to(tmp_path, [a_row()], toggles=bc.parse_toggle_arg(OFF_IMAGERY),
                      omit_unused=True)
    ws = wb["Personalization Canvas"]
    for i in range(1, ws.max_column + 1):
        assert ws.cell(row=2, column=i).value, f"gap at column {i}"
    assert ws.cell(row=4, column=1).value  # data still starts at row 4


def test_omit_unused_warns_about_what_it_dropped(tmp_path):
    out = tmp_path / "c.xlsx"
    _n, warnings = bc.build([a_row()], out, toggles=bc.parse_toggle_arg(OFF_IMAGERY),
                            omit_unused=True)
    assert any("omitted 5 column(s)" in w for w in warnings)
    assert any("fewer than 26 columns" in w for w in warnings)
