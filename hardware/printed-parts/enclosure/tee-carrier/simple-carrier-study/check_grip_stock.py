"""Native stock consequences of the broad grip-corner and cup-rim reliefs."""
import json
from pathlib import Path
import cadquery as cq
from build_concept import build,box,sha,bounds,close_cups,relieve_rim,relieve_entry_corner
HERE=Path(__file__).resolve().parent


def main():
    M,I,plain,blank,L,R,*_=build()
    closed,_=close_cups(plain,I)
    rimmed,rim_removed=relieve_rim(closed,I)
    _,entry_removed=relieve_entry_corner(rimmed,I,M)
    regions={
      'complete aft backing':box((91,94),I['grip_back_y'],I['printed_grip_back_z']),
      'full 6 mm web connection':box((91,94),(I['web_fore_y'],I['web_aft_y']),I['printed_grip_back_z']),
      'outside bar guide faces':box((104.5,107.5),I['guide_body_y'],I['printed_guide_body_z']),
      'moving spring floor and aft wall':box((91,104.5),(109.39,114.29),(205,218))}
    rows=[]
    for name,probe in regions.items():
        stock=plain.intersect(probe)
        rows.append({'region':name,'reference_volume_mm3':stock.Volume(),'lost_mm3':stock.cut(R).Volume()})
    b=entry_removed.BoundingBox();x,z=I['spring_stations'][1]['x'],I['spring_stations'][1]['z']
    bore=cq.Solid.makeCylinder(I['spring_bore_d']/2,I['spring_bore_depth'],
        cq.Vector(x,I['spring_bore_mouth_y'],z),cq.Vector(0,1,0))
    # The relief lies below the round bore, so its top corner is also the
    # nearest point to the full teardrop void; the roof is farther above.
    wall=bore.distance(entry_removed)
    report={'generator_sha256':sha(HERE/'build_concept.py'),'script_sha256':sha(__file__),
       'scope':'Native stock only; no material stiffness or permitted grip load inferred.',
       'broad_entry_relief':{'removed_mm3_per_side':entry_removed.Volume(),'bounds':bounds(entry_removed),
          'remaining_grip_bar_width_x_mm':I['grip_outer_x']-b.xmax,
          'minimum_distance_to_round_spring_bore_mm':wall,
          'web_connection_thickness_y_mm':I['web_aft_y']-I['web_fore_y'],
          'relief_to_web_fore_y_air_mm':I['web_fore_y']-b.ymax,
          'spring_floor_y_preserved':True},
       'cup_rim_notch':{'removed_mm3_per_side':rim_removed.Volume(),'bounds':bounds(rim_removed),
         'remaining_rim_y_length_at_notch_mm':I['grip_rim_y'][1]-I['spring_bore_mouth_y']},
       'native_preserved_regions':rows,
       'all_declared_regions_preserved':all(r['lost_mm3']<1e-5 for r in rows),
       'acceptance':'The relieved corner sacrifices fore/inboard grip stock. Preserve full-width bending and loaded-grip trials; native stock is not a strength rating.'}
    (HERE/'grip-stock-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
