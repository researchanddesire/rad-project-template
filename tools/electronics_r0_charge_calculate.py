"""Bound the independent pack-NTC window using published Rmin/Rmax, not beta extrapolation."""
from pathlib import Path
from itertools import product
import json
ROOT=Path(__file__).resolve().parents[1]
TABLE=[(-10,42636,41549,43723),(-5,34038,33254,34822),(0,27348,26783,27913),(5,22108,21702,22515),(10,17979,17689,18270),(15,14706,14499,14912),(20,12094,11949,12239),(25,10000,9900,10100),(30,8310.8,8211.7,8409.8),(35,6941.1,6845.5,7036.7),(40,5824.9,5734.1,5915.6),(45,4910.6,4825.6,4995.7),(50,4158.3,4079.2,4237.3),(55,3536.2,3463.2,3609.2),(60,3019.7,2952.5,3086.8)]
R=(10000.,715000.,110000.,200000.)
def volts(v,ntc,r,ia=0.,ib=0.):
    # Exact DC nodal solution. Positive input leakage is current INTO IC.
    bias,a,b,c=r
    # Eliminate cold tap, then hot tap, to solve source node.
    gc=c/(b+c)
    hscale=1+a/(b+c)
    hoff=a*(ia+gc*ib)
    h=(v/bias-hoff*(1/bias+1/ntc)-ia-gc*ib)/(hscale*(1/bias+1/ntc)+1/(b+c))
    source=hscale*h+hoff
    cold=gc*(h-b*ib)
    return source,h,cold
rows=[]
for t,nom,lo,hi in TABLE:
    corners=[]
    for v,rn,ss,ia,ib in product((3.,3.6),(lo,hi),product((-.005,.005),repeat=4),(-25e-9,25e-9),(-15e-9,15e-9)):
        corners.append(volts(v,rn,tuple(x*(1+s) for x,s in zip(R,ss)),ia,ib))
    rows.append({'temperature_C':t,'ntc_ohm':{'nominal':nom,'min':lo,'max':hi},'nominal_V':volts(3.296,nom,R), 'corner_V':{n:[min(x[i] for x in corners),max(x[i] for x in corners)] for i,n in enumerate(('PACK_GUARD','TEMP_HOT_IN','TEMP_COLD_IN'))},'corners':len(corners)})
zero=next(x for x in rows if x['temperature_C']==0)
hot=next(x for x in rows if x['temperature_C']==45)
assert zero['corner_V']['TEMP_COLD_IN'][0]>.404
assert hot['corner_V']['TEMP_HOT_IN'][1]<.387
# Opening the NTC is Rntc=infinity; setting extremely large value conservatively approaches it.
open_min=min(volts(v,1e99,tuple(x*(1+s) for x,s in zip(R,ss)),ia,ib)[2] for v,ss,ia,ib in product((3.,3.6),product((-.005,.005),repeat=4),(-25e-9,25e-9),(-15e-9,15e-9)))
assert open_min>.404
out={'status':'Electrical candidate calculation; no physical battery thermal qualification','sources':{'NTC':'https://www.vishay.com/docs/29078/ntcle413.pdf','detector':'https://www.ti.com/lit/ds/symlink/tps3700.pdf','supervisor':'https://www.ti.com/lit/ds/symlink/tps3808.pdf'},'NTC_MPN':'NTCLE413E2103F524A','NTC_curve':'Published Table3 nominal/min/max values, Rev31-Jul-2026; no beta extrapolation','resistors_ohm':dict(zip(('R42','R43','R44','R45'),R)),'resistor_total_budget_fraction':.005,'resistor_budget':'0.1% initial +25ppm/K*100K +0.1% drift=0.45%, rounded to0.5%; this is a prototype engineering budget, not unlimited life qualification','rail_bound_V':[3.,3.6],'input_leakage_bound_A':{'INA':[-25e-9,25e-9],'INB':[-15e-9,15e-9]},'thresholds_V':{'hot_trip':[.387,.400],'hot_release':[.396,.404],'cold_trip':[.396,.404],'cold_release':[.387,.400]},'endpoint_proof':{'at_0C_cold_input_min_V':zero['corner_V']['TEMP_COLD_IN'][0],'cold_fault_assert_max_threshold_V':.404,'at_45C_hot_input_max_V':hot['corner_V']['TEMP_HOT_IN'][1],'hot_fault_assert_min_threshold_V':.387,'open_ntc_cold_input_min_V':open_min,'short_ntc':'PACK_GUARD=0; both taps below hot threshold even with bounded input leakage; verify actual wiring bench'},'permission_output':{'R46_ohm':11000,'R46_pullup_net':'VBUS_CHG','R47_gate_series_ohm':1000,'R48_gate_pulldown_ohm':100000,'resistor_tolerance_fraction':.01,'normal_dock_proposed_V':[4.35,5.25],'fault_output_sink_current_max_A':5.25/(11000*.99),'gate_high_min_before_leakage_V':4.35*(100000*.99)/(11000*1.01+1000*1.01+100000*.99),'gate_high_min_with_2uA_budget_V':(4.35*(100000*.99)/(11000*1.01+1000*1.01+100000*.99))-2e-6*(11000*1.01+1000*1.01),'qualification':'AO3400A RDSon test at2.5V/25C; nonzero low-gate off current over board temperature and all power ramps still require bench acceptance. Normal dock bounds are proposed, not measured.'},'limitations':['Endpoint proof applies to thermistor temperature, not cell core, case, tissue or tip sensor.','Table values at5C spacing support direct endpoint proof; between-row temperature interpolation is not a manufacturer guarantee.','No self-heating, bond gradient/lag, humidity leakage, arbitrary IC internal fault or detached-head qualification.','A 3V3 rail above3.6V is not covered by this window analysis; supply overvoltage is a separate fault.'],'rows':rows}
p=ROOT/'hardware/design/charge-cutoff-r0.json';p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out['endpoint_proof'],indent=2))
print('Nominal permit sampled table rows:',[x['temperature_C'] for x in rows if .404<x['nominal_V'][1] and x['nominal_V'][2]<.387])
