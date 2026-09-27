"""audit_skse: an SKSE DLL that only opens the AE Address Library is AE-only, whatever it exports."""

import audit_skse
from pm import pe
from pm.report import read_csv

AE = "Data/SKSE/Plugins/versionlib-{}.bin".encode("utf-16-le")
SE = b"Data\\SKSE\\Plugins\\version-{}.bin"
EXPORTS = ["SKSEPlugin_Load", "SKSEPlugin_Query", "SKSEPlugin_Version"]


def test_address_library_paths():
    assert pe.address_library(b"x" + AE) == "ae"
    assert pe.address_library(SE) == "se"
    assert pe.address_library(AE + SE) == "both"
    assert pe.address_library(b"nothing here") == ""


def test_query_export_does_not_hide_an_ae_only_address_library(tmp_path):
    ae = tmp_path / "KnockbackPlugin.dll"
    ae.write_bytes(pe.build_dll(EXPORTS) + AE)
    ng = tmp_path / "Multi.dll"
    ng.write_bytes(pe.build_dll(EXPORTS) + AE + SE)
    plain = tmp_path / "Plain.dll"
    plain.write_bytes(pe.build_dll(EXPORTS))
    assert pe.read_dll(ae).runtime_class == "ae_only"
    assert pe.read_dll(ng).runtime_class == "multi"
    assert pe.read_dll(plain).runtime_class == "multi"


def test_dll_mode_checks_single_files(tmp_path):
    ae = tmp_path / "Old.dll"
    ae.write_bytes(pe.build_dll(EXPORTS) + AE)
    se = tmp_path / "New.dll"
    se.write_bytes(pe.build_dll(["SKSEPlugin_Load", "SKSEPlugin_Query"]) + SE)
    out = tmp_path / "reports"
    assert audit_skse.main(["--dll", str(ae), "--dll", str(se), "--out", str(out)]) == 1
    rows = {r["dll"]: r for r in read_csv(out / "audit_skse-dll.csv")}
    assert rows["Old.dll"]["class"] == "ae_only" and rows["New.dll"]["class"] == "se"
    text = (out / "audit_skse-dll.txt").read_text(encoding="utf-8")
    assert "只找 AE 版" in text
