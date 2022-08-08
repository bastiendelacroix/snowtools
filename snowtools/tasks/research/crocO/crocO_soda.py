# -*- coding: utf-8 -*-
'''
Created on 27 mars 2019

@author: cluzetb
Vortex task performing up to 40 offline runs in parallel on a single node

'''
import os

from vortex import toolbox
from snowtools.tasks.research.crocO.crocO_common import _CrocO_Task


class Soda_Task(_CrocO_Task):
    '''
    Task for 1 assimilation cycle
    '''

    def process(self):
        t = self.ticket
        # ##### PREPARE common stuff with the offline task ###########

        firstloop, _, assDate, = self.prepare_common()
        # if 'early-fetch' in self.steps or 'fetch' in self.steps:
        if 'early-fetch' in self.steps:

            self.get_common_consts(firstloop, self.conf.members)  # soda gets ALL members, not only membersnode.

            # ################# FETCH EXECUTABLE ###############
            self.sh.title('Toolbox executable tb08_s= tbx4 (soda)')
            tb08_s = tbx4 = toolbox.executable(
                role           = 'Binary',
                kind           = 'soda',
                local          = 'SODA',
                model          = 'surfex',
                remote         = self.conf.exesurfex + "/SODA"
            )

            print(t.prompt, 'tb08_s =', tb08_s)
            print()

            # ############### FETCH OBSERVATIONS  ##########
            self.sh.title('Toolbox input tobs (obs)')
            nature = self.conf.sensor + "_" + self.conf.geometry.tag # to be changed later
            tobs = toolbox.input(
                geometry        = self.conf.geometry,
                nativefmt       = 'netcdf',
                datevalidity    = assDate,
                model           = 'obs',
                block           = self.conf.sensor,
                nature          = nature,
                kind            = 'SnowObservations',
                namespace       = 'vortex.multi.fr',
                namebuild       = 'flat@cen',
                experiment      = self.conf.obsxpid,
                local           = 'OBSERVATIONS_[datevalidity:ymdHh].nc',
                stage           = '1date',
                fatal           = True
            )
            print(t.prompt, 'tobs =', tobs)
            print()

        if 'fetch' in self.steps:

            self.get_common_fetch() # get the namelist

            # ################# FETCH PREP FILES ################
            # put it in a filetree(/mb0001 etc.) inside the soda task rep for backward comp.
            dmembers = {str(mb): mb for mb in self.conf.members}
            dlocal_names = {str(mb): 'mb{0:04d}'.format(mb) + '/PREP_[date:ymdh].nc'
                            for mb in self.conf.members}
            self.sh.title('Toolbox input tb03_SODA (background)')
            tb03_soda = toolbox.input(
                alternate      = 'SnowpackInit',
                realmember     = self.conf.members,
                member         = dict(realmember= dmembers),
                local          = dict(realmember= dlocal_names),
                experiment     = self.conf.xpid,
                geometry       = self.conf.geometry,
                date           = assDate,
                intent         = 'inout',
                nativefmt      = 'netcdf',
                kind           = 'PREP',
                model          = 'surfex',
                namespace      = 'vortex.cache.fr',  # get it on the cache from last loop
                namebuild      = 'flat@cen',
                block          = 'bg',          # get it on cache @mb****/bg
                stage          = '_bg',
                fatal          = True,
            ),
            print(t.prompt, 'tb03_SODA =', tb03_soda)
            print()
            # ############### FETCH conf file ? ################
            # TODO : get the actualized version of the conf file.

        if 'compute' in self.steps:
            # ################## SODA toolbox.algo
            # test of obs exists/successfully downloaded
            if os.path.exists('OBSERVATIONS_' + assDate.ymdHh + '.nc'):
                # soda
                self.sh.title('Toolbox algo tb11_s = SODA (soda)')

                tb11_s = tbalgo4s = toolbox.algo(
                    engine         = 'parallel',
                    binary         = 'SODA',
                    kind           = "s2m_soda",
                    dateassim      = assDate,
                    members        = self.conf.members,  # no need for mbids in SODA !
                )
                print(t.prompt, 'tb11_s =', tb11_s)
                print()
                self.component_runner(tbalgo4s, tbx4, mpiopts=dict(nnodes=1, nprocs=1, ntasks=1))

        if 'backup' in self.steps:

            if not self.conf.openloop and os.path.exists('OBSERVATIONS_' + assDate.ymdHh + '.nc'):

                self.sh.title('Toolbox output tb12_bk (analysis backup)')
                tb20 = toolbox.output(
                    local          = 'mb[member%04d]/PREP_[date:ymdh].nc',
                    role           = 'SnowpackInit',
                    experiment     = self.conf.xpid,
                    geometry       = self.conf.geometry,
                    date           = assDate,
                    period         = assDate,
                    member         = self.conf.members,  # BC 21/03/19 probably replace by mbids
                    nativefmt      = 'netcdf',
                    kind           = 'PREP',
                    model          = 'surfex',
                    namespace      = 'vortex.cache.fr',
                    namebuild      = 'flat@cen',
                    block          = 'an',
                    stage          = '_an',
                    fatal          = True
                ),
                print(t.prompt, 'tb20 =', tb20)
                print()

        if 'late-backup' in self.steps:
            # if fetchnig to sxcen, must be done file/file to prevent from having too many simultaneous transfers
            storage = ['hendrix.meteo.fr']
            enforcesync = dict(storage={'hendrix.meteo.fr': False, 'sxcen.cnrm.meteo.fr': True})
            if hasattr(self.conf, 'writesx'):
                if self.conf.writesx:
                    storage.append('sxcen.cnrm.meteo.fr')
            if os.path.exists('OBSERVATIONS_' + assDate.ymdHh + '.nc'):
                # if self.conf.pickleit == 'off':
                if True:
                    # ########### PUT PREP FILES HENDRIX ######################################
                    self.sh.title('Toolbox output tb12_ar (analysis archive)')
                    tb20 = toolbox.output(
                        local          = 'mb[member%04d]/PREP_[date:ymdh].nc',
                        role           = 'SnowpackInit',
                        experiment     = self.conf.xpid,
                        geometry       = self.conf.geometry,
                        date           = assDate,
                        period         = assDate,
                        member         = self.conf.members,  # BC 21/03/19 probably replace by mbids
                        nativefmt      = 'netcdf',
                        kind           = 'PREP',
                        model          = 'surfex',
                        namespace      = 'vortex.multi.fr',
                        storage        = storage,
                        enforcesync    = enforcesync,
                        namebuild      = 'flat@cen',
                        block          = 'an',
                        stage          = '_an',
                        fatal          = False  # doesn't exist if openloop
                    ),
                    print(t.prompt, 'tb20 =', tb20)
                    print()

                # ########## RESAMPLE FILES HENDRIX ########################################
                if not os.path.exists('PART_' + assDate.ymdh + '.txt'):
                    print('PART_' + assDate.ymdh + '.txt does not exist')
                else:
                    self.sh.title('Toolbox output tb24 (part archive)')
                    tb24 = toolbox.output(
                        kind           = 'PART',
                        model          = 'soda',
                        block          = 'soda',
                        namebuild       = 'flat@cen',
                        namespace      = 'vortex.multi.fr',
                        storage        = storage,
                        enforcesync    = enforcesync,
                        storetrack     = False,
                        fatal           = True,
                        dateassim       = assDate,
                        experiment      = self.conf.xpid,
                        filename        = 'PART_' + assDate.ymdh + '.txt',
                    )
                    print(t.prompt, 'tb24 =', tb24)
                    print()
                # ########## BG_CORR FILE ON HENDRIX (klocal case only) ########################################
                if os.path.exists('BG_CORR_' + assDate.ymdh + '.txt'):
                    self.sh.title('Toolbox output tb242 (bg_corr archive)')
                    tb242 = toolbox.output(
                        kind           = 'BG_CORR',
                        model          = 'soda',
                        block          = 'soda',
                        namebuild       = 'flat@cen',
                        namespace      = 'vortex.multi.fr',
                        storage        = storage,
                        enforcesync    = enforcesync,
                        fatal           = True,
                        dateassim       = assDate,
                        experiment      = self.conf.xpid,
                        filename        = 'BG_CORR_' + assDate.ymdh + '.txt',
                    )
                    print(t.prompt, 'tb242 =', tb242)
                    print()
                # ########## IMASK FILE ON HENDRIX (klocal case only) ########################################
                if os.path.exists('IMASK_' + assDate.ymdh + '.txt'):
                    self.sh.title('Toolbox output tb243 (imask archive)')
                    tb243 = toolbox.output(
                        kind           = 'IMASK',
                        model          = 'soda',
                        block          = 'soda',
                        namebuild       = 'flat@cen',
                        namespace      = 'vortex.multi.fr',
                        storage        = storage,
                        enforcesync    = enforcesync,
                        storetrack     = False,
                        fatal           = True,
                        dateassim       = assDate,
                        experiment      = self.conf.xpid,
                        filename        = 'IMASK_' + assDate.ymdh + '.txt',
                    )
                    print(t.prompt, 'tb243 =', tb243)
                    print()
                # ########## inflation FILE ON HENDRIX ########################################
                if os.path.exists('ALPHA_' + assDate.ymdh + '.txt'):
                    self.sh.title('Toolbox output tb244 (alpha archive)')
                    tb244 = toolbox.output(
                        kind           = 'ALPHA',
                        model          = 'soda',
                        block          = 'soda',
                        namebuild       = 'flat@cen',
                        namespace      = 'vortex.multi.fr',
                        storage        = storage,
                        enforcesync    = enforcesync,
                        fatal           = False,
                        dateassim       = assDate,
                        experiment = self.conf.xpid,
                        filename = 'ALPHA_' + assDate.ymdh + '.txt',
                    )
                    print(t.prompt, 'tb244 =', tb244)
                    print()
