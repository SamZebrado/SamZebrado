"""Fast structural checks; audit_two_banks handles acoustic roundtrip."""
import unittest,json
from pathlib import Path
import numpy as np
from two_bank_model import geometry,crossing_events,trajectory
P=Path(__file__).resolve().parent

class TwoBankTests(unittest.TestCase):
    def test_all_four_geometries(self):
        for orientation in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            g=geometry(orientation);self.assertEqual(len(g),42);self.assertEqual([s['coordinate'] for s in g],list(range(21))+list(range(26,47)))
            for bank,ori in zip(['B','A'],orientation):
                ss=[s for s in g if s['bank']==bank];self.assertEqual([s['string_index'] for s in ss],list(range(21)) if ori==1 else list(range(20,-1,-1)))
    def test_selected_route_crossings(self):
        model=json.loads((P/'shared_parameters.json').read_text());route=model['route'];knots=np.array(route['endpoint_times']);L,R=route['endpoints'];events=crossing_events(route,model['metadata']['active_intervals']);pos,v,_=trajectory(route,np.array([e['time'] for e in events]))
        np.testing.assert_allclose(pos,[e['coordinate'] for e in events],rtol=0,atol=2e-10)
        self.assertTrue(np.all(v*np.array([e['direction'] for e in events])>0));self.assertTrue(all(not 20<e['coordinate']<26 for e in events))
        self.assertGreaterEqual(knots[-1],model['metadata']['duration']);self.assertEqual(knots[0],0)
        self.assertLessEqual(float(np.max(1.875*(R-L)/np.diff(knots))),50+1e-10)
        x,v,a=trajectory(route,knots);np.testing.assert_allclose(v,0,atol=1e-12);np.testing.assert_allclose(a,0,atol=1e-12)
    def test_all_six_candidate_routes(self):
        names=['full_Bup_Aup','full_Bup_Adown','full_Bdown_Aup','full_Bdown_Adown','partial_B1_A6','partial_B2_A6']
        for name in names:
            model=json.loads((P/name/'parameters.json').read_text());r=model['route'];h=np.diff(r['endpoint_times']);L,R=r['endpoints'];self.assertLessEqual(float(np.max(1.875*(R-L)/h)),50+1e-10)
            self.assertLessEqual(float(h.max()),2+1e-10);self.assertEqual(len(r['string_geometry']),42)
            self.assertEqual(set(g['bank'] for g in model['groups']),{'B','A'})
            expected={(s['bank'],s['string_index']):s['coordinate'] for s in r['string_geometry']}
            for g in model['groups']:self.assertEqual(g['coordinate'],expected[(g['bank'],g['string_index'])])
    def test_independent_physical_string_groups(self):
        model=json.loads((P/'shared_parameters.json').read_text());groups=model['groups'];keys=[(g['bank'],g['string_index']) for g in groups];self.assertEqual(len(keys),len(set(keys)));self.assertEqual(set(g['bank'] for g in groups),{'B','A'})
        self.assertEqual(len(model['initial_states']),6)
        for g in groups:
            self.assertEqual(len(g['events']),len(g['strengths']));self.assertEqual(len(set(e['half_cycle'] for e in g['events'])),len(g['events']))
            self.assertTrue(all(e['bank']==g['bank'] and e['string_index']==g['string_index'] for e in g['events']))
        for j in range(6):
            pair=[g for g in groups if g['note_index']==j]
            if len(pair)==2:self.assertFalse(np.array_equal(pair[0]['response_real'],pair[1]['response_real']))

if __name__=='__main__':unittest.main()
