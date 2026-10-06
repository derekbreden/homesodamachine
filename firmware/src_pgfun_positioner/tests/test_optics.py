import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'host'))
from noise import qualify
from observe import extract
from gpobs.features import FeatureResult

class OpticsTests(unittest.TestCase):
 def test_stationary_floor_requires_duration_and_rejects_drift(self):
  rows=[dict(physical=True,valid=True,sample_ns=i*100_000_000,values_mm=[.001*np.sin(i)]*4) for i in range(400)]
  cfg={'mm_per_pixel':[.003,.003]};out,receipt=qualify(rows,cfg)
  self.assertTrue(out['noise_qualified']);self.assertGreater(out['stationary_sigma_px'],.1)
  with self.assertRaises(ValueError):qualify(rows[:100],cfg)
  rows[-1]['values_mm']=[.05]*4
  with self.assertRaises(ValueError):qualify(rows,cfg)
 def test_seam_angle_error_is_in_the_endpoint_uncertainty(self):
  point=FeatureResult('dot','1',True,dict(u=1050.,v=50.),dict(u=.1,v=.1),1)
  seam=FeatureResult('seam','1',True,dict(theta_deg=90.,rho=0.),dict(theta_deg=1.,rho=.1),1)
  cfg=dict(dot={},wire={},seam={'roi':[0,0,100,100]},mm_per_pixel=[.001,.001],stationary_sigma_px=.1,noise_qualified=True)
  with patch('observe.AimingDot') as dot,patch('observe.WireTip') as wire,patch('observe.SeamLine') as line:
   dot.return_value.run.return_value=point;wire.return_value.run.return_value=point;line.return_value.run.return_value=seam
   result=extract(np.zeros((100,1100,3)),cfg)
  self.assertTrue(result['valid']);self.assertGreater(result['sigma_mm'][1],.017)

if __name__=='__main__':unittest.main()
