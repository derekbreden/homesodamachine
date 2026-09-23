#!/usr/bin/env python3
"""Read gas-chain fit dimensions and the stored placement-derived Box without building CAD."""
from pathlib import Path
import ast
import hashlib
import json
import operator

ROOT = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware').parent
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def constants(path):
    values = {}
    operations = {ast.Add: operator.add, ast.Sub: operator.sub,
                  ast.Mult: operator.mul, ast.Div: operator.truediv}
    def read(node):
        if isinstance(node, ast.Name):
            return values[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in operations:
            return operations[type(node.op)](read(node.left), read(node.right))
        return ast.literal_eval(node)
    def bind(target, value):
        if isinstance(target, ast.Name):
            values[target.id] = value
        elif isinstance(target, (ast.Tuple, ast.List)):
            for member, item in zip(target.elts, value, strict=True):
                bind(member, item)
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign):
            try:
                value = read(node.value)
            except (ValueError, TypeError, KeyError):
                continue
            for target in node.targets:
                bind(target, value)
    return values


def main():
    paths = {
        'gas_chain': ROOT/'hardware/manifold-layout/_gas_chain.py',
        'gas_routes': ROOT/'hardware/manifold-layout/_lines.py',
        'assembly': ROOT/'hardware/manifold-layout/enclosure_assembly.py',
        'scorecard': ROOT/'hardware/manifold-layout/_scorecard.py',
        'enclosure': ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure.py',
        'fits': ROOT/'hardware/printed-parts/cadlib/fits.py',
        'check': ROOT/'hardware/reference/gasher-check-valve/gasher_check_valve.py',
        'regulator': ROOT/'hardware/reference/wr1110-regulator/wr1110_regulator.py',
        'measurement': ROOT/'hardware/reference/wr1110-regulator/scan-measurements.json',
        'scan_check': ROOT/'hardware/reference/wr1110-regulator/scan-model-check.json',
        'male_adapter': ROOT/'hardware/reference/jg-pp010822e/jg_pp010822e.py',
        'female_adapter': ROOT/'hardware/reference/seaflo-discharge-chain/seaflo_discharge_chain.py',
        'box': ROOT/'hardware/manifold-layout/enclosure-box.json',
    }
    c = {k: constants(p) for k,p in paths.items() if p.suffix == '.py'}
    reg, check, female = c['regulator'], c['check'], c['female_adapter']
    slip = c['fits']['slip']
    rib = c['enclosure']['tie_w'] + c['enclosure']['tie_cav_buffer'] + 2*c['enclosure']['tie_cav_wall']
    male_reach = c['male_adapter']['HEX_LENGTH'] + c['male_adapter']['COLLET_LENGTH']
    female_length = female['JG_SOCKET_L'] + female['JG_HEX_L'] + female['JG_COLLET_L']
    reg_engagement = min(female['NPT_ENGAGE'], reg['STUB_LENGTH'])
    box = json.loads(paths['box'].read_text())['box']['pack']
    pack = dict(zip(box['fields'], box['values']))
    gas_names = ['wr1110', 'gasher-co2', 'co2-inlet', 'co2-adapter-regulator-in',
                 'co2-adapter-regulator-out', 'co2-adapter-check-in', 'co2-adapter-check-out']
    def seat(diameter, length, evidence):
        return {'owner':'enclosure-back-top', 'evidence':evidence,
                'model_diameter_mm':diameter, 'printed_bore_diameter_mm':diameter+2*slip,
                'usable_round_length_mm':length, 'printed_anchor_length_mm':rib,
                'axial_margin_each_end_mm':(length-rib)/2}
    report = {
        'scope':'Source dimensions and stored Box; physical assembly fit is unverified.',
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in (*paths.values(), Path(__file__))},
        'gas_fit_scorecard':{'kind':'goal', 'status':'warn',
                            'reason':'WR1110 scanned; GASHER and made-up adapter reaches remain nominal.'},
        'seat_geometry':{
            'wr1110':seat(reg['BODY_D'],reg['BODY_LENGTH'],'Two coated MINI 2 scans at native scale.'),
            'gasher_co2':seat(check['SOCKET_D'],check['SOCKET_LENGTH'],'Nominal reference, unmeasured received part.')},
        'nominal_made_up_envelopes':{
            'male_adapter_external_reach_mm':male_reach,
            'female_adapter_body_length_mm':female_length,
            'regulator_assumed_insertion_mm':reg_engagement,
            'regulator_female_adapter_reach_from_stub_tip_mm':female_length-reg_engagement,
            'regulator_collet_to_collet_mm':reg['OVERALL_LENGTH']+male_reach+female_length-reg_engagement,
            'check_assumed_insertion_mm':female['NPT_ENGAGE'],
            'check_collet_to_collet_mm':check['TOTAL_LENGTH']+male_reach+female_length-female['NPT_ENGAGE'],
            'qualification':'WR1110 shoulder seating bounds the model. Actual makeup and adapter envelopes are not measured.'},
        'ceiling_pockets':{
            'owner':'enclosure-back-top', 'plan_air_mm':c['assembly']['CEILING_RELIEF_PLAN_SLIP'],
            'crown_air_mm':c['assembly']['CEILING_RELIEF_Z_CLEAR'],
            'box_sha256':sha(paths['box']),
            'rows':[row for row in pack['ceiling_reliefs'] if row[0] in gas_names]},
        'remaining_observations':[
            'GASHER inlet boss diameter and usable axial length.',
            'Made-up fitting external diameters, step positions and collet reaches from each body datum.',
            'Printed tie threading, seating and retention; hose bends, insertion and wrench access.',
            'Thread sealing, part ratings and operating performance during commissioning.'],
        'assessment':{
            'received_part_back_top_fit_qualified':False,
            'additional_wr1110_scan_required':False,
            'unpowered_enclosure_assembly_trial_held_for_gas_commissioning':False,
            'scope':'Gas fit concerns the back-top. Front-top mechanisms and lower quadrants have no direct gas-cradle or pocket dependency.'},
    }
    (OUT/'source-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['seat_geometry','nominal_made_up_envelopes']},indent=2))


if __name__ == '__main__':
    main()
