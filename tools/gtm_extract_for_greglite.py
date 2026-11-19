#!/usr/bin/env python3
"""Read-only parse of GregTech-Modern 1.20.1 Java sources for GregTech parity codegen."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

GTM_ROOT = Path(__file__).resolve().parents[1] / "reference" / "GregTech-Modern"
OUT_DIR = Path(__file__).resolve().parents[1] / "mods" / "gtceu" / "tracker" / "gtm_extract"

TIER_NAMES = (
    "ULV",
    "LV",
    "MV",
    "HV",
    "EV",
    "IV",
    "LuV",
    "ZPM",
    "UV",
    "UHV",
    "UEV",
    "UIV",
    "UXV",
    "OpV",
    "MAX",
)

MULTIBLOCK_ROLES: dict[str, str] = {
    "large_boiler_bronze": "Large steam boiler (bronze)",
    "large_boiler_steel": "Large steam boiler (steel)",
    "large_boiler_titanium": "Large steam boiler (titanium)",
    "large_boiler_tungstensteel": "Large steam boiler (tungstensteel)",
    "coke_oven": "Coke oven (primitive charcoal)",
    "primitive_blast_furnace": "Primitive blast furnace",
    "electric_blast_furnace": "Electric blast furnace (coil)",
    "large_chemical_reactor": "Large chemical reactor",
    "implosion_compressor": "Implosion compressor",
    "pyrolyse_oven": "Pyrolyse oven",
    "multi_smelter": "Multi smelter (parallel smelt)",
    "cracker": "Oil cracker",
    "distillation_tower": "Distillation tower",
    "vacuum_freezer": "Vacuum freezer",
    "assembly_line": "Assembly line",
    "primitive_pump": "Primitive water pump",
    "steam_grinder": "High-pressure steam macerator",
    "steam_oven": "High-pressure steam furnace",
    "fusion_reactor": "Fusion reactor (tiered MK)",
    "fluid_drilling_rig": "Fluid bedrock drilling rig",
    "large_miner": "Large area miner",
    "cleanroom": "Cleanroom (circuit assembly)",
    "large_combustion_engine": "Large combustion generator",
    "extreme_combustion_engine": "Extreme combustion generator",
    "steam_large_turbine": "Large steam turbine",
    "gas_large_turbine": "Large gas turbine",
    "plasma_large_turbine": "Large plasma turbine",
    "active_transformer": "Active transformer (EU routing)",
    "power_substation": "Power substation (EU storage)",
    "charcoal_pile_igniter": "Charcoal pile igniter",
    "bedrock_ore_miner": "Bedrock ore miner",
    "wooden_multiblock_tank": "Wooden multiblock fluid tank",
    "bronze_multiblock_tank": "Bronze multiblock fluid tank",
    "steel_multiblock_tank": "Steel multiblock fluid tank",
    "central_monitor": "Central monitor display",
}

# Early-mid game priority (GregTech Electric / MV-HV focus); extras filled from parsed materials.
MATERIAL_PRIORITY: tuple[str, ...] = (
    "Iron",
    "Copper",
    "Tin",
    "Gold",
    "Silver",
    "Lead",
    "Nickel",
    "Zinc",
    "Bronze",
    "Brass",
    "Steel",
    "WroughtIron",
    "Invar",
    "StainlessSteel",
    "Aluminium",
    "Titanium",
    "Chromium",
    "Manganese",
    "Cobalt",
    "Antimony",
    "Bismuth",
    "Electrum",
    "Cupronickel",
    "BatteryAlloy",
    "SolderingAlloy",
    "Rubber",
    "Polyethylene",
    "PolyvinylChloride",
    "Epoxy",
    "SiliconeRubber",
    "StyreneButadieneRubber",
    "Glass",
    "Wood",
    "Charcoal",
    "Coal",
    "Diamond",
    "Emerald",
    "Redstone",
    "Lapis",
    "Quartz",
    "Sulfur",
    "Salt",
    "Saltpeter",
    "Phosphate",
    "Water",
    "Oxygen",
    "Hydrogen",
    "Nitrogen",
    "Carbon",
    "Silicon",
    "Calcium",
    "Sodium",
    "Magnesium",
    "Aluminium",
    "Phosphorus",
    "Chlorine",
    "SulfuricAcid",
    "HydrochloricAcid",
    "NitricAcid",
    "DistilledWater",
    "Steam",
    "Oil",
    "RawOil",
    "LightFuel",
    "Diesel",
    "Gasoline",
    "Lubricant",
    "Glue",
    "Polydimethylsiloxane",
    "Galena",
    "Chalcopyrite",
    "Hematite",
    "Magnetite",
    "Cassiterite",
    "Bauxite",
    "Spodumene",
    "Pyrite",
    "Cinnabar",
    "Scheelite",
    "Coal",
    "Lignite",
    "Obsidian",
    "Andesite",
    "Granite",
    "Marble",
    "Concrete",
    "Plascrete",
    "AnnealedCopper",
    "Magnalium",
    "Kanthal",
    "Nichrome",
    "Tungsten",
    "TungstenSteel",
    "Vanadium",
    "Molybdenum",
    "Platinum",
    "Palladium",
    "Iridium",
    "Osmium",
    "Neodymium",
    "Yttrium",
    "Lithium",
    "Sodium",
    "Potassium",
    "TinAlloy",
    "BlueAlloy",
    "RedAlloy",
    "FineCopper",
    "Indium",
    "Gallium",
    "Arsenic",
    "Boron",
    "Carbon",
    "Fluorine",
    "Argon",
    "Helium",
    "Methane",
    "Ethylene",
    "Propene",
    "Benzene",
    "Phenol",
    "AceticAcid",
    "Ethanol",
    "Methanol",
    "Acetone",
    "Ammonia",
    "HydrogenPeroxide",
    "SodiumPersulfate",
    "PrintedCircuitBoard",
    "AdvancedCircuit",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_gt_values() -> list[dict]:
    text = read_text(GTM_ROOT / "src/main/java/com/gregtechceu/gtceu/api/GTValues.java")
    v_match = re.search(
        r"public static final long\[\] V = \{([^}]+)\};", text, re.DOTALL
    )
    if not v_match:
        raise RuntimeError("GTValues.V not found")
    voltages = [int(x.strip().rstrip("L")) for x in v_match.group(1).split(",") if x.strip()]

    names_match = re.search(
        r'public static final String\[\] VOLTAGE_NAMES = new String\[\] \{([^}]+)\};',
        text,
        re.DOTALL,
    )
    long_names = []
    if names_match:
        long_names = re.findall(r'"([^"]+)"', names_match.group(1))

    tiers = []
    for i, short in enumerate(TIER_NAMES):
        entry = {
            "index": i,
            "name": long_names[i] if i < len(long_names) else short,
            "short": short,
            "voltage": voltages[i] if i < len(voltages) else None,
        }
        tiers.append(entry)
    return tiers


def parse_recipe_types() -> tuple[dict[str, int], dict[str, str]]:
    text = read_text(
        GTM_ROOT / "src/main/java/com/gregtechceu/gtceu/common/data/GTRecipeTypes.java"
    )
    inputs: dict[str, int] = {}
    reg_names: dict[str, str] = {}
    for m in re.finditer(
        r"public final static GTRecipeType (\w+) = register\(\"([^\"]+)\"",
        text,
    ):
        const, reg_name = m.group(1), m.group(2)
        reg_names[const] = reg_name
    for m in re.finditer(
        r"public final static GTRecipeType (\w+) = register\(\"[^\"]+\"[^;]*?\.setMaxIOSize\((\d+)",
        text,
        re.DOTALL,
    ):
        const, item_in = m.group(1), int(m.group(2))
        inputs[const] = item_in
        if const in reg_names:
            inputs[reg_names[const]] = item_in
    return inputs, reg_names


def parse_simple_electric_machines(
    inputs_map: dict[str, int], reg_names: dict[str, str]
) -> list[dict]:
    text = read_text(
        GTM_ROOT / "src/main/java/com/gregtechceu/gtceu/common/data/GTMachines.java"
    )
    pattern = re.compile(
        r"new SimpleMachineBuilder\(REGISTRATE,\s*\"([^\"]+)\"(?:,\s*\n\s*)?,?\s*GTRecipeTypes\.(\w+)"
    )
    machines = []
    notes_hints = {
        "circuit_assembler": "Cleanroom-oriented; pollution debuff",
        "chemical_reactor": "16B fluid tank per tier",
        "laser_engraver": "Pollution debuff",
        "gas_collector": "Pollution debuff; large fluid tank",
        "assembler": "HV-capped fluid tank; pollution debuff",
        "lathe": "Custom LatheRecipeLogic",
    }
    for m in pattern.finditer(text):
        mid, recipe_const = m.group(1), m.group(2)
        recipe_hint = reg_names.get(
            recipe_const, recipe_const.removesuffix("_RECIPES").lower()
        )
        typical = inputs_map.get(recipe_const, inputs_map.get(recipe_hint, 1))
        if typical > 2:
            typical = 2 if typical >= 2 else 1
        machines.append(
            {
                "id": mid,
                "recipe_type": recipe_hint,
                "typical_inputs": typical,
                "notes": notes_hints.get(mid, ""),
            }
        )
    return machines


def parse_generators(reg_names: dict[str, str]) -> list[dict]:
    text = read_text(
        GTM_ROOT / "src/main/java/com/gregtechceu/gtceu/common/data/GTMachines.java"
    )
    tier_map = {"LV": "lv", "MV": "mv", "HV": "hv"}

    def gen_entry(var_name: str, id_hint: str, recipe: str) -> dict | None:
        pat = rf"public static final MachineDefinition\[\] {var_name} = registerSimpleGenerator\(REGISTRATE, \"{id_hint}\",\s*GTRecipeTypes\.(\w+)[^;]+?(GTValues\.(?:LV|MV|HV)(?:,\s*GTValues\.(?:LV|MV|HV))*)\);"
        m = re.search(pat, text, re.DOTALL)
        if not m:
            return None
        tiers = re.findall(r"GTValues\.(LV|MV|HV)", m.group(2))
        fuel_const = m.group(1)
        return {
            "id": id_hint,
            "recipe_type": reg_names.get(
                fuel_const, fuel_const.removesuffix("_FUELS").lower()
            ),
            "tiers": [tier_map[t] for t in tiers],
        }

    out = []
    for var, rid in (
        ("STEAM_TURBINE", "steam_turbine"),
        ("COMBUSTION", "combustion"),
        ("GAS_TURBINE", "gas_turbine"),
    ):
        entry = gen_entry(var, rid, "")
        if entry:
            out.append(entry)
    return out


def parse_multiblocks() -> list[dict]:
    text = read_text(
        GTM_ROOT
        / "src/main/java/com/gregtechceu/gtceu/common/data/machines/GTMultiMachines.java"
    )
    ids: list[str] = []

    for m in re.finditer(r'\.multiblock\("([^"]+)"', text):
        ids.append(m.group(1))

    for m in re.finditer(
        r"registerLargeBoiler\(REGISTRATE,\s*\"([^\"]+)\"", text
    ):
        ids.append(f"large_boiler_{m.group(1)}")

    for m in re.finditer(
        r"registerLargeCombustionEngine\(REGISTRATE,\s*\"([^\"]+)\"", text
    ):
        ids.append(m.group(1))

    for m in re.finditer(r"registerLargeTurbine\(REGISTRATE,\s*\"([^\"]+)\"", text):
        ids.append(m.group(1))

    for m in re.finditer(
        r'registerMultiblockTank\(REGISTRATE,\s*"([^\"]+)"', text
    ):
        ids.append(m.group(1))

    for name in ("fusion_reactor", "fluid_drilling_rig", "large_miner", "bedrock_ore_miner"):
        if name not in ids:
            ids.append(name)

    seen: set[str] = set()
    unique: list[str] = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            unique.append(i)

    return [
        {"id": i, "role": MULTIBLOCK_ROLES.get(i, i.replace("_", " ").title())}
        for i in sorted(unique)
    ]


ELEMENT_SYMBOLS: dict[str, str] = {
    "Hydrogen": "H",
    "Helium": "He",
    "Lithium": "Li",
    "Carbon": "C",
    "Nitrogen": "N",
    "Oxygen": "O",
    "Fluorine": "F",
    "Neon": "Ne",
    "Sodium": "Na",
    "Magnesium": "Mg",
    "Aluminium": "Al",
    "Silicon": "Si",
    "Phosphorus": "P",
    "Sulfur": "S",
    "Chlorine": "Cl",
    "Argon": "Ar",
    "Potassium": "K",
    "Calcium": "Ca",
    "Iron": "Fe",
    "Copper": "Cu",
    "Zinc": "Zn",
    "Tin": "Sn",
    "Silver": "Ag",
    "Gold": "Au",
    "Lead": "Pb",
    "Nickel": "Ni",
    "Chromium": "Cr",
    "Manganese": "Mn",
    "Cobalt": "Co",
    "Titanium": "Ti",
    "Tungsten": "W",
    "Platinum": "Pt",
    "Palladium": "Pd",
    "Iridium": "Ir",
    "Osmium": "Os",
    "Antimony": "Sb",
    "Bismuth": "Bi",
    "Arsenic": "As",
    "Boron": "B",
    "Indium": "In",
    "Gallium": "Ga",
    "Vanadium": "V",
    "Molybdenum": "Mo",
    "Neodymium": "Nd",
    "Yttrium": "Y",
    "Rubidium": "Rb",
    "Caesium": "Cs",
    "Barium": "Ba",
    "Lanthanum": "La",
    "Cerium": "Ce",
    "Uranium238": "U",
    "Uranium235": "U",
    "Thorium": "Th",
    "Plutonium239": "Pu",
    "Deuterium": "D",
    "Tritium": "T",
}


def parse_materials_core() -> list[dict]:
    mat_dir = GTM_ROOT / "src/main/java/com/gregtechceu/gtceu/common/data/materials"
    files = [
        "ElementMaterials.java",
        "FirstDegreeMaterials.java",
        "OrganicChemistryMaterials.java",
        "UnknownCompositionMaterials.java",
        "SecondDegreeMaterials.java",
    ]
    by_java_name: dict[str, dict] = {}

    block_re = re.compile(
        r"(\w+)\s*=\s*new Material\.Builder\(GTCEu\.id\(\"([^\"]+)\"\)\)(.*?)\.buildAndRegister\(\);",
        re.DOTALL,
    )

    for fname in files:
        text = read_text(mat_dir / fname)
        for m in block_re.finditer(text):
            java_name, mat_id, body = m.group(1), m.group(2), m.group(3)
            flags: list[str] = []
            if re.search(r"\.ingot\(", body):
                flags.append("ingot")
            if re.search(r"\.dust\(\)", body) or re.search(r"\.dust\(", body):
                flags.append("dust")
            if ".ore()" in body:
                flags.append("ore")
            if re.search(r"GENERATE_PLATE", body) or ".plate()" in body:
                flags.append("plate")
            if re.search(r"GENERATE_FINE_WIRE", body):
                flags.append("wire")
            if re.search(r"\.liquid\(", body) or re.search(r"\.gas\(", body):
                flags.append("fluid")

            formula: str | None = None
            elem = re.search(r"\.element\(GTElements\.(\w+)\)", body)
            if elem:
                sym = elem.group(1)
                formula = sym if len(sym) <= 3 else ELEMENT_SYMBOLS.get(java_name)
            comp = re.search(r"\.components\(([^)]+)\)", body, re.DOTALL)
            if comp and not formula:
                parts = re.findall(r"(\w+),\s*(\d+)", comp.group(1))
                if parts and len(parts) <= 6:
                    chunks = []
                    for name, count in parts:
                        sym = ELEMENT_SYMBOLS.get(name, name[:2])
                        chunks.append(f"{sym}{count if count != '1' else ''}")
                    formula = "".join(chunks)

            by_java_name[java_name] = {
                "id": mat_id,
                "java_name": java_name,
                "chemical_formula": formula,
                "flags_hint": flags,
                "source_file": fname.replace(".java", ""),
            }

    ordered: list[dict] = []
    used: set[str] = set()
    for java_name in MATERIAL_PRIORITY:
        if java_name in by_java_name and java_name not in used:
            ordered.append(by_java_name[java_name])
            used.add(java_name)
        if len(ordered) >= 120:
            break

    if len(ordered) < 120:
        for java_name in sorted(by_java_name.keys()):
            if java_name in used:
                continue
            src = by_java_name[java_name]["source_file"]
            if src in ("ElementMaterials", "FirstDegreeMaterials", "OrganicChemistryMaterials"):
                ordered.append(by_java_name[java_name])
                used.add(java_name)
            if len(ordered) >= 120:
                break

    for entry in ordered:
        entry.pop("java_name", None)
        entry.pop("source_file", None)
    return ordered[:120]


def parse_cable_materials() -> list[dict]:
    mat_dir = GTM_ROOT / "src/main/java/com/gregtechceu/gtceu/common/data/materials"
    tier_short = TIER_NAMES
    cables: list[dict] = []

    block_re = re.compile(
        r"(\w+)\s*=\s*new Material\.Builder\(GTCEu\.id\(\"([^\"]+)\"\)\)(.*?)\.buildAndRegister\(\);",
        re.DOTALL,
    )
    cable_re = re.compile(
        r"\.cableProperties\(V\[(\w+)\],\s*(\d+)(?:,\s*(\d+))?",
    )

    for path in sorted(mat_dir.glob("*.java")):
        text = read_text(path)
        for m in block_re.finditer(text):
            java_name, mat_id, body = m.group(1), m.group(2), m.group(3)
            cm = cable_re.search(body)
            if not cm:
                continue
            tier_ref = cm.group(1)
            amps = int(cm.group(2))
            loss = int(cm.group(3)) if cm.group(3) else None
            tier_idx = tier_short.index(tier_ref) if tier_ref in tier_short else None
            entry = {
                "id": mat_id,
                "material": java_name,
                "voltage_tier": tier_ref.lower() if tier_ref in tier_short else tier_ref,
                "voltage_tier_index": tier_idx,
                "max_amperage": amps,
            }
            if loss is not None:
                entry["voltage_loss_per_block"] = loss
            cables.append(entry)

    cables.sort(key=lambda c: (c.get("voltage_tier_index") or 99, c["id"]))
    return cables


def coverage_weights() -> dict:
    categories = [
        {"id": "singleblock_types", "weight": 18, "description": "Simple electric processor coverage vs GTM machine ids"},
        {"id": "singleblock_tiers", "weight": 10, "description": "Per-type tier band (LV–IV) registration parity"},
        {"id": "generators", "weight": 8, "description": "Steam/combustion/gas turbine tiers and fuels"},
        {"id": "cables", "weight": 10, "description": "Cable materials, amp tiers, loss model"},
        {"id": "materials_forms", "weight": 15, "description": "Core materials and prefix forms (ingot/dust/plate/ore)"},
        {"id": "recipes_depth", "weight": 17, "description": "Recipe maps per type vs GTM recipe JSON"},
        {"id": "multiblocks", "weight": 7, "description": "Controller multiblocks (steam→HV slice first)"},
        {"id": "eu_net_fidelity", "weight": 8, "description": "EU/t, amps, transformers, loss"},
        {"id": "steam_age", "weight": 5, "description": "LP/HP steam machines and boilers"},
        {"id": "gui_assets", "weight": 2, "description": "Processor UI panels and overlays"},
    ]
    total = sum(c["weight"] for c in categories)
    return {
        "schema": 1,
        "source": "gtceu_proposal",
        "gtm_branch": "1.20.1",
        "weight_total": total,
        "categories": categories,
    }


def write_json(name: str, data) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> int:
    if not GTM_ROOT.is_dir():
        print(f"ERROR: GTM reference not found at {GTM_ROOT}", file=sys.stderr)
        return 1

    tiers = parse_gt_values()
    inputs_map, reg_names = parse_recipe_types()
    machines = parse_simple_electric_machines(inputs_map, reg_names)
    generators = parse_generators(reg_names)
    multiblocks = parse_multiblocks()
    materials = parse_materials_core()
    cables = parse_cable_materials()
    weights = coverage_weights()

    files_written = [
        write_json("tiers.json", {"schema": 1, "source": "GTValues.java", "tiers": tiers}),
        write_json(
            "electric_machine_types.json",
            {"schema": 1, "source": "GTMachines.java SimpleMachineBuilder", "machines": machines},
        ),
        write_json(
            "generators.json",
            {"schema": 1, "source": "GTMachines.java registerSimpleGenerator", "generators": generators},
        ),
        write_json(
            "multiblocks.json",
            {"schema": 1, "source": "GTMultiMachines.java", "controllers": multiblocks},
        ),
        write_json(
            "materials_core.json",
            {"schema": 1, "source": "materials/*.java", "count_target": 120, "materials": materials},
        ),
        write_json(
            "cable_materials.json",
            {"schema": 1, "source": "materials/*.java cableProperties", "cables": cables},
        ),
        write_json("coverage_weights.json", weights),
    ]

    counts = {
        "tiers": len(tiers),
        "electric_machine_types": len(machines),
        "generators": len(generators),
        "multiblocks": len(multiblocks),
        "materials_core": len(materials),
        "cable_materials": len(cables),
        "coverage_weight_categories": len(weights["categories"]),
        "coverage_weight_total": weights["weight_total"],
    }

    print("GTM extract ->", OUT_DIR)
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print("  output_files:", len(files_written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())