from __future__ import (absolute_import, division, print_function)

import os.path
from mantid.kernel import Direction, StringContainsValidator, PropertyManagerProperty
from mantid.api import AlgorithmFactory, AlgorithmManager, MultipleFileProperty, \
    WorkspaceProperty, PythonAlgorithm, FileLoaderRegistry
from mantid.simpleapi import MergeRuns, RenameWorkspace, DeleteWorkspace, GroupWorkspaces, mtd


class LoadMergeRuns(PythonAlgorithm):

    _loader = None
    _version = None
    _loader_options = None

    def name(self):
        return "LoadMergeRuns"

    def category(self):
        return "DataHandling"

    def summary(self):
        return 'Loads and merges multiple runs. Similar to Load, but uses MergeRuns instead of Plus for summing.'

    def validateInputs(self):
        issues = dict()
        loader = self.getPropertyValue('LoaderName')
        version = self.getProperty('LoaderVersion').value
        try:
            AlgorithmManager.createUnmanaged(loader, version)
        except RuntimeError:
            message = loader + '-v' + str(version) + ' is not registered with Mantid.'
            issues['LoaderName'] = message
            issues['LoaderVersion'] = message
        return issues

    def PyInit(self):
        self.declareProperty(MultipleFileProperty('Filename'), doc='List of input files')
        self.declareProperty('LoaderName', defaultValue='Load', validator=StringContainsValidator(['Load']),
                             direction=Direction.InOut,
                             doc='The name of the specific loader. Generic Load by default.')
        self.declareProperty('LoaderVersion', defaultValue=-1, direction=Direction.InOut,
                             doc='The version of the specific loader')
        self.declareProperty(PropertyManagerProperty('LoaderOptions',dict()),
                             doc='Options for the specific loader')
        self.declareProperty(PropertyManagerProperty('MergeRunsOptions',dict()),
                             doc='Options for merging the metadata')
        self.declareProperty(WorkspaceProperty('OutputWorkspace', '', direction=Direction.Output),
                             doc='Output workspace or workspace group.')

    def _load(self, run, runnumber):
        """
            Loads the single run using the specific loader
            @param run : the full file path
            @param runnumber : the run number
        """
        alg = self._create_fresh_loader()
        alg.setPropertyValue('Filename', run)
        alg.setPropertyValue('OutputWorkspace', runnumber)
        alg.execute()

    def _create_fresh_loader(self):
        """
            Creates a fresh instance of the specific loader. It is needed for safety,
            since there might be loaders, that do not reset their private members.
            So running on the same instance can potentially cause problems
            Also the output will always be on ADS, since this algorithm relies on
            MergeRuns, which does not work outside ADS
            @return : initialized and configured loader
        """
        alg = self.createChildAlgorithm(self._loader, version=self._version)
        alg.setAlwaysStoreInADS(True)
        alg.initialize()
        for key in self._loader_options.keys():
            alg.setPropertyValue(key, self._loader_options.getPropertyValue(key))
        return alg

    def PyExec(self):
        runs = self.getProperty('Filename').value
        self._loader = self.getPropertyValue('LoaderName')
        self._version = self.getProperty('LoaderVersion').value
        self._loader_options = self.getProperty('LoaderOptions').value
        merge_options = self.getProperty('MergeRunsOptions').value
        output = self.getPropertyValue('OutputWorkspace')

        # get the first run
        to_group = []
        first_run = runs[0]
        if isinstance(first_run, list):
            first_run = first_run[0]

        if self._loader == 'Load':
            # figure out the winning loader
            winning_loader = FileLoaderRegistry.Instance().chooseLoader(first_run)
            self._loader = winning_loader.name()
            self._version = winning_loader.version()
            self.setPropertyValue('LoaderName', self._loader)
            self.setProperty('LoaderVersion', self._version)

        for runs_to_sum in runs:
            if not isinstance(runs_to_sum, list):
                run = runs_to_sum
                runnumber = os.path.basename(run).split('.')[0]
                self._load(run, runnumber)
                to_group.append(runnumber)
            else:
                runnumbers = ''
                first = ''
                for i, run in enumerate(runs_to_sum):
                    runnumber = os.path.basename(run).split('.')[0]
                    runnumbers = runnumbers + '_' + runnumber
                    self._load(run, runnumber)
                    if i == 0:
                        first = runnumber
                    else:
                        MergeRuns(InputWorkspaces=[first, runnumber], OutputWorkspace=first, **merge_options)
                        DeleteWorkspace(Workspace=runnumber)
                runnumbers = runnumbers[1:]
                RenameWorkspace(InputWorkspace=first, OutputWorkspace=runnumbers)
                to_group.append(runnumbers)

        if len(to_group) != 1:
            GroupWorkspaces(InputWorkspaces=to_group, OutputWorkspace=output)
        else:
            RenameWorkspace(InputWorkspace=to_group[0], OutputWorkspace=output)

        self.setProperty('OutputWorkspace', mtd[output])

AlgorithmFactory.subscribe(LoadMergeRuns)
