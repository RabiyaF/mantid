from __future__ import print_function

import mantid.simpleapi as mantid

from Muon.GUI.ElementalAnalysis.LoadWidget import load_utils as lutils


class LoadModel(lutils.LModel):
    def __init__(self):
        super(LoadModel, self).__init__()

    def execute(self):
        if self.run not in self.loaded_runs:
            self.load_run()


class CoLoadModel(lutils.LModel):
    def __init__(self):
        super(CoLoadModel, self).__init__()
        self.workspace = None
        self.co_runs = []

    def wipe_co_runs(self):
        self.co_runs = []
        self.workspace = None

    def execute(self):
        if self.run not in self.loaded_runs:
            current_ws = self.load_run()
            if current_ws is None:
                return
            self.loaded_runs[self.run] = current_ws
        if self.run not in self.co_runs:
            self.co_runs.append(self.run)
            if self.workspace:
                self.co_load_run(self.loaded_runs[self.run])
            else:
                self.workspace = self.loaded_runs[self.run]

    def add_runs(self, l, r):
        out = "{}_co_add".format(l)
        mantid.Plus(l, r, OutputWorkspace=out)
        return out

    def co_load_run(self, workspace):
        to_add = [self.add_runs(l, r) for l, r in zip(*lutils.flatten_run_data(
            self.workspace, workspace))]
        print(lutils.hyphenise(self.co_runs), self.co_runs)
        self.workspace = lutils.group_by_detector(
            lutils.hyphenise(self.co_runs), to_add)
