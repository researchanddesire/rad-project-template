"""Read-only exact-BRep local-control proposal; never saves or edits main CAD.

Run with FreeCAD's bundled Python. The report contains nominal packaging probes,
not released threads, membrane mechanics, electrical overtravel or seal proof.
"""
from pathlib import Path
import argparse, hashlib, json, sys, zipfile, xml.etree.ElementTree as ET
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import Part
ROOT = Path(__file__).resolve().parents[1]

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def box(x0,y0,z0,x1,y1,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,App.Vector(x0,y0,z0))
def cyl(x,y,z0,z1,r): return Part.makeCylinder(r,z1-z0,App.Vector(x,y,z0))
def overlap(a,b):
    return a.common(b).Volume if a.BoundBox.intersect(b.BoundBox) else 0.0

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native',type=Path,default=ROOT/'hardware/cad/prototype-r2/ButtplugPrototypeR2.FCStd')
    parser.add_argument('--report',type=Path,default=ROOT/'hardware/design/local-controls-mechanical-r2.json')
    parser.add_argument('--expected-native-sha')
    a=parser.parse_args(); native=a.native.resolve(); native_sha=sha(native)
    if a.expected_native_sha and native_sha!=a.expected_native_sha: raise SystemExit('Native source hash differs; use the current explicitly reviewed snapshot.')
    archive=zipfile.ZipFile(native); xml=ET.fromstring(archive.read('Document.xml'))
    objects={o.attrib['name']:o for o in xml.findall('.//ObjectData/Object')}; cache={}
    def shape(name):
        if name not in cache:
            p=objects[name].find("./Properties/Property[@name='Shape']/Part")
            s=Part.Shape();s.importBrepFromString(archive.read(p.attrib['file']).decode());cache[name]=s
        return cache[name]
    def intervals(s,x,y):
        common=s.common(Part.makeLine(App.Vector(x,y,-25),App.Vector(x,y,25)))
        return [[e.BoundBox.ZMin,e.BoundBox.ZMax] for e in common.Edges]
    placement_path=ROOT/'hardware/pcb/prototype-r2/routed-placement-report-r2.json'
    interface_path=ROOT/'hardware/design/local-controls-interface-r2.json'
    board_path=ROOT/'hardware/pcb/prototype-r2/buttplug-r2.kicad_pcb'
    placement=json.loads(placement_path.read_text()); interface=json.loads(interface_path.read_text())
    if sha(board_path)!=placement['board_sha256']: raise SystemExit('Routed placement report is stale for current board.')
    core=shape('PolymerCaptureBridge'); lower=shape('PolymerFlangeCore'); crown=shape('CoreFlangeCrown')
    skin=shape('ElastomerFlangeCoverUpper')
    components={c['ref']:box(c['xy_bounds_mm'][0],c['xy_bounds_mm'][1],c['z_bounds_mm'][0],c['xy_bounds_mm'][2],c['xy_bounds_mm'][3],c['z_bounds_mm'][1]) for c in placement['component_boxes'] if c['z_bounds_mm'][1]-c['z_bounds_mm'][0]>.001}
    geometry_path=native.with_name('geometry-report.json')
    geometry=json.loads(geometry_path.read_text())
    if geometry.get('native_sha256')!=native_sha: raise SystemExit('Geometry report does not describe this native snapshot.')
    exclusions={'PolymerCaptureBridge','PolymerFlangeCore','ElastomerFlangeCoverUpper','TBoardReservation','PlacedComponentReservations'}
    fixed_names=[n for n in geometry['parts'] if n in objects and n not in exclusions]
    # Explicit owner-supplied in-development wire envelope, checked even when its
    # final compound has a different name. Four-wire 2.2mm circular bundle space.
    wire=Part.makeCylinder(1.1,21.5,App.Vector(-24,-15.5,11),App.Vector(1,0,0))
    out={'revision':'local-controls-mechanical-r2-01','date':'2026-10-31',
      'state':'Concrete nominal cartridge/support proposal; no live CAD or PCB edits; not an accepted actuation/sealing design',
      'sources':{'native_path':str(native.relative_to(ROOT)),'native_sha256':native_sha,'routed_board_sha256':sha(board_path),'placement_report_sha256':sha(placement_path),'interface_sha256':sha(interface_path),'probe_source_sha256':sha(__file__),'geometry_report_sha256':sha(geometry_path)},
      'primary_reference':interface['source'],
      'architecture':{
        'actuation':'Each existing +Z switch receives an axial captive stepped plunger in a two-piece serviceable cartridge under a continuous local silicone diaphragm.',
        'cartridge_installation':'Upper barrel enters a real6.1mm core opening from +Z. Its recessed7x15mm conformal flange is retained by two nominalM1.6 screw interfaces atY±5.5mm into dedicated underside core bosses. The screws prevent rotation; the silicone carries no retention load. A separate removable lower guide captures the plunger collar and spring before upper-core closure.',
        'thread_boundary':'The two nominalM1.6 fastener interfaces and removable lower-guide joint are geometric reservations, not selected screws, inserts or released polymer threads. The RAM probe includes1.8mm flange clearance holes,1.3mm receiving-pilot envelopes and4mm underside bosses, but no helical thread or catalog screw. Actual head/recess, controlled pilot, insert or direct-thread process, engagement, locking, creep and strength require selection and a fresh check.',
        'retention':'Collar diameter3.6mm cannot pass the upper3.2mm opening or lower2.0mm guide. The screw-retained lower guide captures collar, spring and stop shims independently of the silicone cover.',
        'membrane':'Keep the original exterior envelope and continuous upper-cover material at each button. Provide a local annular diaphragm by a0.5mm upward underside relief inside an8mm diameter perimeter, retaining the full original skin thickness in a central3.2mm boss over the conformal plunger head. No through-hole in the silicone is proposed. The surrounding1mm skin is retained as a wide integral web; its split-cover perimeter still needs an independent continuous dry-cavity seal.',
        'membrane_boundary':'The report measures the actual unchanged skin footprint only. Thin-web/corrugation radii, boss coupling, material, hardness, bonded/overmolded process, return force, fatigue, cleanability and leakage are unqualified; a final deformed membrane solid is not claimed.',
        'return':'Reserve a captive coaxial compression spring independently returning the plunger outward. Spring supplier/material/rate/preload are OPEN. Nominal occupied envelope OD3.0/ID1.9mm, installed length1.8mm at home and1.0mm at maximum study stroke; no real coil or force acceptance is implied.',
        'back_support':'Lower-core pedestals widen only below the B-component layer; narrow insulating shoes support bare board regions directly under the switch load. A removable nonconductive top shim is adjusted to contact without PCB preload. Soldermask wear, electrical insulation, flatness and press-load capacity require review.'},
      'travel':{'tip_home_z_mm':2.35,'unpressed_switch_top_z_mm':[2.0,2.25],'nominal_free_gap_mm':0.25,'height_only_free_gap_range_mm':[0.10,0.35],'switch_pretravel_range_mm':[0.05,0.35],'total_motion_to_switch_range_using_independent_extremes_mm':[0.15,0.70],'maximum_cartridge_study_stroke_mm':0.8,'stop_shim_range_mm':[0,0.8],'initial_blocking_shim_mm':0.8,'approved_operating_stroke_mm':None,'allowable_switch_overtravel_mm':None,'default':'Install the full blocking spacer for handling and assembly. No enabled operational stop setting is accepted. Choose a shorter stop only after obtaining controlled allowable total travel/overtravel and validating the full assembled tolerance stack; do not infer it from pretravel.','tolerance_boundary':'Gap range above includes switch height only. PCB seating, reflow, guide clearance, tip length, membrane boss and core/stop tolerances remain additive; proposed0.8mm motion is packaging capacity, not approved switch motion.'},
      'coverage':{'fixed_native_roles':fixed_names,'excluded_native_roles':sorted(exclusions),'component_refs':len(placement['component_boxes']),'positive_height_component_boxes':len(components),'extra_owner_wire_envelope':{'path_xyz_mm':[[-24,-15.5,11],[-2.5,-15.5,11]],'radius_mm':1.1,'scope':'Owner-specified full-02 tip high-crossing reservation; not actual routed wires'}},'candidate_geometry':[],'intersections':[],'bounds':{'exterior_changed':False,'PCB_changed':False,'live_native_saved':False,'physical_tested':False,'seal_qualified':False,'force_or_overtravel_qualified':False},
      'scope':'Exact native BRep nominal packaging and explicit guide/spring/thread interface envelopes. No assembled functional proof or deformable membrane simulation.'}
    tools=[]; core_bosses=[]; pilot_tools=[]; additions=[]; plunger_samples=[]
    for ref,x in [('SW1',-30),('SW2',-20)]:
        y=-12; roof=intervals(core,x,y)[-1]; skin_iv=intervals(skin,x,y)[-1]
        # Flange seats into a conformal counterseat cut0.6mm below the saved
        # exterior core surface. Shaft bores remain axial to fixed PCB Z.
        seat_outer=crown.copy();seat_outer.translate(App.Vector(0,0,-.6))
        opening=cyl(x,y,12,25,3.05)
        counterseat=box(x-3.65,y-7.65,12,x+3.65,y+7.65,25).cut(seat_outer)
        tool=opening.fuse(counterseat); tools.append(tool)
        patch=skin.common(cyl(x,y,0,25,4.0)); shifted=skin.copy();shifted.translate(App.Vector(0,0,.5))
        membrane=patch.common(shifted).fuse(patch.common(cyl(x,y,0,25,1.6)))
        upper=cyl(x,y,12.8,25,3.0).common(crown)
        flange=box(x-3.5,y-7.5,12,x+3.5,y+7.5,25).common(crown).cut(seat_outer)
        upper=upper.fuse(flange)
        mounts=[]
        for my in [y-5.5,y+5.5]:
            upper=upper.cut(cyl(x,my,12,26,.9))
            boss=cyl(x,my,13.5,25,2.0).common(crown); core_bosses.append(boss)
            pilot_tools.append(cyl(x,my,14.1,26,.65))
            mounts.append({'center_xy_mm':[x,my],'boss_diameter_mm':4.0,'boss_bottom_z_mm':13.5,'flange_clearance_diameter_mm':1.8,'receiving_pilot_envelope_diameter_mm':1.3,'blind_pilot_bottom_z_mm':14.1,'nominal_fastener_interface':'M1.6; actual part/head/insert or thread process OPEN'})
        # Axial stop cavity, narrow upper opening, and lower threaded-guide bore.
        upper=upper.cut(cyl(x,y,13.7,15.0,1.9)).cut(cyl(x,y,15.0,26,1.6)).cut(cyl(x,y,12,13.8,2.2))
        # Lower bearing/stop component; smooth outside bounds stand in for the
        # unselected fastening thread, not a modeled functional screw joint.
        guide=cyl(x,y,3.3,12.8,1.7).fuse(cyl(x,y,12.8,13.8,2.2))
        guide=guide.cut(cyl(x,y,3.2,12.8,1.0)).cut(cyl(x,y,12.8,13.9,1.6))
        # Outer stop landR1.6..2.2 at13.8; spring sits insideR1.6.
        neck=cyl(x,y,15,25,1.5).common(crown);neck.translate(App.Vector(0,0,-.05))
        plunger=cyl(x,y,2.35,14.6,.9).fuse(cyl(x,y,14.6,15,1.8)).fuse(neck)
        # A0.8mm diameter foot provides a centered flat contact, not a whole
        # 1.8mm shaft end overhanging the switch's1.5mm actuator.
        plunger=plunger.cut(cyl(x,y,2.349,3.15,.901)).fuse(cyl(x,y,2.35,3.2,.4))
        if ref=='SW1':
            shoe=box(x-1,-12.8,-2.2,x+1,-12.1,-.7)
            pedestal=box(x-2,-13.9,-17,x+2,-10.9,-2.2)
        else:
            shoe=box(x-1.1,-12.7,-2.2,x+1.1,-11.3,-.7)
            pedestal=box(x-1,-12.8,-18.5,x+2,-10.2,-2.2)
        shim=shoe.common(box(-60,-40,-.9,60,0,-.7));shim.translate(App.Vector(0,0,.2))
        support=pedestal.fuse(shoe).common(crown)
        additions.extend([(ref+'_UpperCartridge',upper),(ref+'_LowerGuide',guide),(ref+'_BoardSupport',support),(ref+'_InsulatingShim',shim)])
        record={'ref':ref,'center_xy_mm':[x,y],'core_z_intervals_mm':intervals(core,x,y),'skin_z_intervals_mm':intervals(skin,x,y),
          'guide':{'lower_outer_diameter_mm':3.4,'lower_z_mm':[3.3,12.8],'bore_diameter_mm':2.0,'shaft_diameter_mm':1.8,'upper_barrel_maximum_diameter_mm':6.0,'mounts':mounts,'flange_xy_mm':[7.0,15.0],'core_through_opening_diameter_mm':6.1,'counterseat_xy_mm':[7.3,15.3],'counterseat_vertical_depth_mm':.6},
          'plunger':{'contact_foot_diameter_mm':.8,'collar_diameter_mm':3.6,'collar_z_home_mm':[14.6,15.0],'lower_stop_z_mm':13.8,'upper_retention_opening_diameter_mm':3.2,'upper_contact_head_diameter_mm':3.0,'membrane_inner_gap_mm':.05,'tip_home_z_mm':2.35},
          'membrane':{'nominal_relief_diameter_mm':8.0,'annular_underside_vertical_relief_mm':.5,'central_full_thickness_boss_diameter_mm':3.2,'original_skin_center_thickness_mm':skin_iv[1]-skin_iv[0],'annulus_centerline_remaining_vertical_thickness_mm':skin_iv[1]-skin_iv[0]-.5,'original_exterior_retained':True},
          'back_support':{'shoe_bbox_xyz_mm':[shoe.BoundBox.XMin,shoe.BoundBox.YMin,shoe.BoundBox.ZMin,shoe.BoundBox.XMax,shoe.BoundBox.YMax,shoe.BoundBox.ZMax],'shim_nominal_mm':.2,'shim_top_z_mm':-.5,'solid_count':len(support.Solids)},
          'undeformed_membrane_patch_volume_mm3':membrane.Volume,'source_skin_patch_volume_mm3':patch.Volume,'source_core_removed_mm3':overlap(core,tool),'source_lower_core_attachment_mm3':overlap(lower,support),
          'solid_counts':{'upper':len(upper.Solids),'lower_guide':len(guide.Solids),'plunger':len(plunger.Solids),'support':len(support.Solids),'membrane':len(membrane.Solids)},'valid_shapes':{'upper':upper.isValid(),'lower_guide':guide.isValid(),'plunger':plunger.isValid(),'support':support.isValid(),'undeformed_membrane_patch':membrane.isValid()},
          'plunger_sampled_stroke_mm':[0,.2,.4,.6,.8],'wire_crossing_clearances_mm':{'upper':upper.distToShape(wire)[0],'lower_guide':guide.distToShape(wire)[0]},'component_clearances_mm':{},'cartridge_to_core_nominal_radial_clearance_mm':.05}
        for n,s in [(ref+'_UpperCartridge',upper),(ref+'_LowerGuide',guide),(ref+'_BoardSupport',support),(ref+'_InsulatingShim',shim)]:
            for f,other in components.items():
                v=overlap(s,other)
                if v>1e-6:out['intersections'].append({'candidate':n,'fixed_component':f,'volume_mm3':v})
            for f in fixed_names:
                v=overlap(s,shape(f))
                if v>1e-6:out['intersections'].append({'candidate':n,'fixed_part':f,'volume_mm3':v})
            v=overlap(s,wire)
            if v>1e-6:out['intersections'].append({'candidate':n,'fixed_part':'OwnerHighTipCrossingEnvelope','volume_mm3':v})
        for other in ['R3','R35','C1','R4']:
            record['component_clearances_mm'][other+'_to_support']=support.distToShape(components[other])[0]
        for travel in [0,.2,.4,.6,.8]:
            moved=plunger.copy();moved.translate(App.Vector(0,0,-travel))
            plunger_samples.append((ref,travel,moved))
            for n,s in [('UpperCartridge',upper),('LowerGuide',guide)]:
                v=overlap(moved,s)
                if v>1e-6:out['intersections'].append({'candidate':ref+'_Plunger','sampled_stroke_mm':travel,'fixed_part':n,'volume_mm3':v})
            for f,other in components.items():
                v=overlap(moved,other)
                if v>1e-6 and f!=ref:out['intersections'].append({'candidate':ref+'_Plunger','sampled_stroke_mm':travel,'fixed_component':f,'volume_mm3':v})
        out['candidate_geometry'].append(record)
    modified_core=core
    for b in core_bosses:modified_core=modified_core.fuse(b)
    for t in tools+pilot_tools:modified_core=modified_core.cut(t)
    for i,b in enumerate(core_bosses):
        for f,other in components.items():
            v=overlap(b,other)
            if v>1e-6:out['intersections'].append({'candidate':'MountingBoss'+str(i),'fixed_component':f,'volume_mm3':v})
        for f in fixed_names:
            v=overlap(b,shape(f))
            if v>1e-6:out['intersections'].append({'candidate':'MountingBoss'+str(i),'fixed_part':f,'volume_mm3':v})
        v=overlap(b,wire)
        if v>1e-6:out['intersections'].append({'candidate':'MountingBoss'+str(i),'fixed_part':'OwnerHighTipCrossingEnvelope','volume_mm3':v})
    for ref,travel,s in plunger_samples:
        v=overlap(s,modified_core)
        if v>1e-6:out['intersections'].append({'candidate':ref+'_Plunger','sampled_stroke_mm':travel,'fixed_part':'ProposedBoredUpperCore','volume_mm3':v})
    out['proposed_core']={'valid':modified_core.isValid(),'solid_count':len(modified_core.Solids),'volume_mm3':modified_core.Volume,'original_volume_mm3':core.Volume,'added_receiving_boss_count':len(core_bosses),'receiving_thread_geometry_modeled':False,'openings_real_in_RAM':True,'not_written_to_main_native':True}
    out['nominal_packaging_clear_excluding_intended_core_attachment_and_switch_contact']=not out['intersections']
    out['assembly_sequence']=[
      'With electronics and silicone removed, machine/mold the through-openings, conformal seats and underside receiving bosses in the upper core; deburr toward the dry cavity. These remain proposed RAM changes only.',
      'Insert each collar plunger and an actual qualified return spring into its upper barrel; fit the full blocking stop spacer, then attach and positively lock the removable lower guide. Verify that the collar cannot leave either end.',
      'Install each completed guide cartridge from +Z into its core seat and fit both positively locked flange screws into the selected receiving thread/insert interfaces; assemble before high-crossing wires. No silicone adhesive is relied on for cartridge or plunger retention.',
      'Fit lower-core support pedestals and nonconductive shims before dropping the PCB. Check all B-side body and solder clearances and set support contact without preloading the PCB.',
      'Close the upper core with blocked plungers; fit the continuous local silicone cover and engage each molded inner boss with its plunger head. Retain the separate cover perimeter/seam seal by its final qualified method.',
      'Keep zero stroke until current controlled switch travel/overtravel and full stack are accepted. Then select tip/stop shims, verify power/mode switching and release throughout temperature/tolerance, and test leakage, cleaning, repeated presses and accidental activation.'
    ]
    out['remaining_gates']=['Controlled current B3U drawing, allowable overtravel/total travel and axial load; do not enable0.8mm study stroke as a switch setting.','Full dimensional stack including PCB seating/reflow, guides, coaxiality, tip and membrane.0.8mm contact tip vs nominal1.5mm actuator needs reviewed radial registration margin.','Cartridge flange screws/receiving bosses and removable lower-guide joint, support strength/creep and all actual fasteners; smooth thread envelopes are not functional native threads.','Actual spring selection, coil bind, force, return, friction and fatigue; no force or press-cycle validation.','Membrane grade/hardness, minimum web, strain/boss retention, cover perimeter and continuous dry-cavity sealing, cleaning and body-contact process acceptance.','Full assembly motion, solder/via/soldermask contact, insulation/wear, actual parts and tolerance validation.']
    if sha(native)!=native_sha: raise SystemExit('Native changed during read-only probe; report not written.')
    a.report.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'native_sha256':native_sha,'candidate_packaging_clear':out['nominal_packaging_clear_excluding_intended_core_attachment_and_switch_contact'],'intersections':out['intersections'],'candidate_parts_valid':all(all(c['valid_shapes'].values())for c in out['candidate_geometry']),'report':str(a.report)},indent=2))
if __name__=='__main__': main()
