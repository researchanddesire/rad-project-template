"""Check the editable harness map against the current full native netlist."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
import yaml
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'hardware/cables/interboard-r29';S=ROOT/'hardware/pcb/flange-access-r28/candidate-s';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
y=P/'interboard-r29.yml';recipe=yaml.safe_load(y.read_text());native=S/'system-native.xml';tree=E.parse(native).getroot();net={(n.get('ref'),n.get('pin')):q.get('name')for q in tree.findall('nets/net')for n in q.findall('node')}
rows=[]
for pin in range(1,11):
 a=recipe['connectors']['J6']['pinlabels'][pin-1];b=recipe['connectors']['J7']['pinlabels'][pin-1];assert a==b==net['J6',str(pin)]==net['J7',str(pin)]
 rows.append({'pin':pin,'net':a,'native_J6':a,'native_J7':b})
assert recipe['connections']==[[{'J6':list(range(1,11))},{'W-INTERBOARD-R29':list(range(1,11))},{'J7':list(range(1,11))}]]
assert all(recipe['connectors'][r]['mpn']=='SHR-10V-S'for r in ['J6','J7']);assert recipe['additional_bom_items'][0]['qty']==20
c=recipe['cables']['W-INTERBOARD-R29'];assert c['wirecount']==10 and c['gauge']==28 and c['length']==.120
reference=json.loads((P/'reference-review.json').read_text());wireR=.244*.120;scenarios=[]
for I in [.3,.5,.8]:
 for label,contact in [('initial',.02),('after_environment_reference',.04)]:
  loopR=2*wireR+4*contact;scenarios.append({'current_A':I,'contact_reference':label,'assumed_each_wire_length_m':.120,'loop_resistance_ohm':loopR,'loop_drop_V':I*loopR,'loop_loss_W':I*I*loopR})
result={'date':'2026-11-01','reviewer_sha256':sha(Path(__file__)),'recipe_sha256':sha(y),'current_full_native_XML_sha256':sha(native),'reference_review_sha256':sha(P/'reference-review.json'),'human_BOM_sha256':sha(ROOT/'hardware/bom.csv'),'all_10_numbered_nets_equal':rows,'candidate_parts':{'housings':2,'crimp_contacts':20,'individual_starting_blanks':10,'each_blank_mm':120,'total_starting_wire_m':1.2},'resistance_scenarios':scenarios,'scope':'Numeric 1:1 map and illustrative power/return loop at 120mm per leg. Two mated interfaces per conductor are included. All currents are scenarios, not approved load or enclosed ratings; shared-ground current, supply minima, crimp spread, temperature rise, I2C/RF and produced wiring need bench review. Starting blanks are not finished lengths or retained service slack. No physical acceptance/purchase/human BOM edit.'}
(P/'logical-review.json').write_text(json.dumps(result,indent=2)+'\n');print('All ten nets match current native J6/J7; 2 housings/20 contacts/ten120mm starting blanks. No BOM or native circuit changed.')
