import copy,json,math,sys,tempfile,time,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'host'))
from kinematics import split_target,aim_point,GEOMETRY_SHA,SOFT_LIMIT,WORKING_LEVER
from servo import fit,qualified,correction,observation
from trajectory import check,evaluate,fit as fit_trace,qualify as qualify_trace,period_for_speed,digest
J=np.array([[.001,0],[0,.001],[.001,.0002],[.0001,.001]])
def response_rows(levels=(2,8,32),offset=0):
 rows=[];stamp=offset
 for branch in ((1,1),(1,-1),(-1,1),(-1,-1)):
  for n in levels:
   for a,b in ((n,2*n),(2*n,n)):
    d=[a*branch[0],b*branch[1]];stamp+=1
    rows.append(dict(delta=d,direction=list(branch),change_mm=(J@d).tolist(),sigma_mm=[.001]*4,physical=True,after_ns=stamp,optics_config_sha256='0'*64))
 return rows
class HostTests(unittest.TestCase):
 def test_targets_are_bounded_and_exact(self):
  steps=list(split_target([12,-10],[1000,-700]));self.assertTrue(all(max(abs(x)for x in r)<=256 for r in steps));self.assertEqual(np.sum(steps,axis=0).tolist(),[988,-690])
  with self.assertRaises(ValueError):list(split_target([0,0],[SOFT_LIMIT+1,0]))
  self.assertAlmostEqual(np.linalg.norm(np.array(aim_point(1,0))-aim_point(0,0)),WORKING_LEVER*2*math.pi/640000,places=9)
 def test_real_branch_fit_and_independent_holdouts(self):
  model=fit(response_rows());self.assertFalse(model['qualified']);out=qualified(model,response_rows(offset=1000));self.assertTrue(out['qualified'])
  with self.assertRaises(ValueError):qualified(model,response_rows())
  delta,residual=correction(out,[.03,.02,.034,.023],[1,1]);self.assertLessEqual(max(abs(J@delta)),.010);self.assertLessEqual(np.linalg.norm(delta)*WORKING_LEVER*2*math.pi/640000,.010)
  with self.assertRaises(ValueError):correction(out,[0,0,1,0],[1,1])
 def test_cubic_bounds_speed_and_loop(self):
  n=64;p=dict(geometry_sha256=GEOMETRY_SHA,period_us=8_000_000,knots=[[round(100*math.sin(i*2*math.pi/n)),round(50*math.cos(i*2*math.pi/n))]for i in range(n)])
  check(p);np.testing.assert_allclose(evaluate(p,0),p['knots'][0]);np.testing.assert_allclose(evaluate(p,1),p['knots'][0]);self.assertLess(np.max(abs(evaluate(p,np.arange(10000)/10000))),101)
  p['knots'][1][0]=SOFT_LIMIT
  with self.assertRaises(ValueError):check(p)
 def test_dry_fit_then_independent_replay_evidence(self):
  period=period_for_speed(8);model=qualified(fit(response_rows()),response_rows(offset=1000));profile=dict(geometry_sha256=GEOMETRY_SHA,period_us=period,knots=[[0,0]]*256,qualified=False)
  goal=np.array([0.,0.,.1,.2]);target=dict(physical=True,values_mm=goal.tolist(),optics_config_sha256='0'*64)
  def capture(candidate,offset,baseline=False):
   rows=[]
   for i in range(1800):
    elapsed=(i+1)*period/1e6/600;phase=(i+1)/600%1;disturb=np.array([8*math.sin(phase*2*math.pi),5*math.cos(phase*2*math.pi)])
    values=goal+J@(disturb+evaluate(candidate,phase));rows.append(dict(physical=True,valid=True,phase=phase,elapsed_s=elapsed,sigma_mm=[.001]*4,clock_uncertainty_ms=1,values_mm=values.tolist(),sample_ns=offset+i,optics_config_sha256='0'*64))
   return dict(physical=True,profile=candidate,rows=rows,speed_mm_s=8,direction='cw',index_label='tube-zero',optics_config_sha256='0'*64)
  record=capture(profile,10000);candidate=fit_trace(record,model,target);self.assertFalse(candidate['qualified']);out=qualify_trace(candidate,[capture(candidate,20000),capture(candidate,30000)]);self.assertTrue(out['qualified']);self.assertLessEqual(out['holdout_max_mm'],.010)
  with self.assertRaises(ValueError):qualify_trace(candidate,[capture(candidate,20000),capture(candidate,20000)])
 def test_reversal_deadband_is_learned_and_checked(self):
  rows=response_rows((2,4,8,16,32,64));hold=response_rows((3,6,12,24,48),offset=1000)
  for batch in (rows,hold):
   for r in batch:
    d=np.asarray(r['delta']);r['change_mm']=(J@(np.sign(d)*np.maximum(abs(d)-[10,7],0))).tolist()
  model=fit(rows);out=qualified(model,hold);self.assertTrue(out['qualified'])
  for branch in model['branches'].values():self.assertEqual(branch['reversal_deadband_counts'],[10,7])
 def test_deadband_search_boundary_cannot_be_qualified(self):
  rows=response_rows((2,4,8,16,32,64))
  for r in rows:
   d=np.asarray(r['delta']);r['change_mm']=(J@(np.sign(d)*np.maximum(abs(d)-[32,7],0))).tolist()
  with self.assertRaisesRegex(ValueError,'search boundary'):fit(rows)
 def test_stale_camera_record_is_never_control_input(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'obs.json';p.write_text(json.dumps(dict(physical=True,valid=True,noise_qualified=True,sample_ns=time.monotonic_ns()-1_000_000_000,values_mm=[0]*4,sigma_mm=[.001]*4)))
   with self.assertRaises(TimeoutError):observation(p,timeout=.03)
   p.write_text(json.dumps(dict(physical=True,valid=False,sample_ns=time.monotonic_ns())))
   with self.assertRaises(ValueError):observation(p,timeout=.03)
if __name__=='__main__':unittest.main()
