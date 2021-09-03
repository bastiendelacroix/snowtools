#!/usr/bin/env python
# -*- coding:Utf-8 -*-


__all__ = []

from bronx.stdtypes.date import Date
from bronx.stdtypes.date import Period
from cen.layout.nodes import S2MTaskMixIn
import footprints
import glob
import os
import tarfile
from vortex import toolbox
from vortex.layout.nodes import Driver, Task

logger = footprints.loggers.getLogger(__name__)


def setup(t, **kw):
    return Driver(
        tag    = 'pearp2safran',
        ticket = t,
        nodes  = [
            PrepSafran(tag='prepsaf', ticket=t, **kw),
        ],
        options = kw,
    )


class PrepSafran(Task, S2MTaskMixIn):

    filter_execution_error = S2MTaskMixIn.s2moper_filter_execution_error

    def refill(self):

        pass

    def process(self):
        """Preparation of SAFRAN input files"""

        t = self.ticket

        if 'early-fetch' in self.steps or 'fetch' in self.steps:

            tbarp   = list()
            interp = ' -i IDW'
            rundate = self.conf.datebegin
            while rundate <= self.conf.dateend:

                # 1. Check if guess file already exists
                self.sh.title('Toolbox input tb01')
                tb01 = toolbox.input(
                    role           = 'Ebauche',
                    local          = '[date::ymdh]/P[date::addcumul_yymdh]',
                    geometry       = self.conf.vconf,
                    vapp           = 's2m',
                    vconf          = '[geometry:area]',
                    experiment     = self.conf.xpid,
                    cutoff         = 'assimilation',
                    block          = self.conf.guess_block,
                    date           = ['{0:s}/-PT6H/-PT{1:s}H'.format(rundate.ymd6h, str(d)) for d in footprints.util.rangex(0, 24, self.conf.cumul)],
                    cumul          = self.conf.cumul,
                    nativefmt      = 'ascii',
                    kind           = 'guess',
                    model          = 'safran',
                    source_app     = self.conf.source_app,
                    source_conf    = self.conf.deterministic_conf,
                    namespace      = self.conf.namespace,
                    fatal          = False,
                ),
                print(t.prompt, 'tb01 =', tb01)
                print()

                if len(tb01[0]) < 5:

                    # 2. Get ARPEGE file 
                    # Recuperation de A6 du réseau H-6 pour H in [0, 6, 12, 18]

                    if rundate >= Date(2018, 7, 1) and rundate < Date(2019, 7, 1, 0):
                        # Sorties de la chaine ARPEGE oper en ksh, disponibles jusqu'ai 01/07/2018 à la date du 08/08/2020
                        # Date à revoir en fonction de la durée de rétention sur hendrix
                        self.sh.title('Toolbox input tb02')
                        tbarp.extend(toolbox.input(
                            role           = 'Gridpoint',
                            format         = 'grib',
                            geometry       = self.conf.cpl_geometry,
                            kind           = 'gridpoint',
                            local          = '[date::ymdh]/ARPEGE[date::ymdh]_[term::hour]',
                            date           = ['{0:s}/-PT6H/-PT{1:s}H'.format(rundate.ymd6h, str(d)) for d in footprints.util.rangex(0, 24, self.conf.cumul)],
                            term           = self.conf.cumul,
                            nativefmt      = '[format]',
                            #remote         = '/home/mrns/vernaym/extraction_bdap/[vconf]/arpege_[date::ymdh]_[term::hour].grib',
                            #hostname       = 'guppy.meteo.fr',
                            #tube           = 'ftp',
                            #origin         = 'arpege',
                            #fatal          = False,
                            suite          = 'oper',
                            cutoff         = 'assimilation',
                            # local          = 'mb035/ARPEGE[date::addterm_ymdh]',
                            namespace      = 'oper.multi.fr',
                            origin         = 'historic',
                            model          = '[vapp]',
                            vapp           = self.conf.source_app,
                            vconf          = self.conf.deterministic_conf,
                            fatal          = False,
                        ))
                        print(t.prompt, 'tb02 =', tbarp)
                        print()

                    elif rundate < Date(2018, 7, 1):
                        # Pour les dates les plus anciennes aucun archivage sur hendrix n'est disponible
                        # Il faut alors extraire les champs des guess depuis la BDPE avec le script 
                        # creation_fichiers_RST.py sur guppy

                        self.sh.title('Toolbox input tb02')
                        tbarp.extend(toolbox.input(
                            role           = 'Gridpoint',
                            format         = 'grib',
                            geometry       = self.conf.cpl_geometry,
                            kind           = 'gridpoint',
                            local          = '[date::ymdh]/ARPEGE[date::ymdh]_[term::hour]',
                            date           = ['{0:s}/-PT6H/-PT{1:s}H'.format(rundate.ymd6h, str(d)) for d in footprints.util.rangex(0, 24, self.conf.cumul)],
                            term           = self.conf.cumul,
                            nativefmt      = '[format]',
                            remote         = '/home/mrns/vernaym/extraction_bdap/[vconf]/arpege_[date::ymdh]_[term::hour].grib',
                            hostname       = 'guppy.meteo.fr',
                            tube           = 'ftp',
                            origin         = 'arpege',
                            fatal          = False,
                            #suite          = 'oper',
                            #cutoff         = 'assimilation',
                            # local          = 'mb035/ARPEGE[date::addterm_ymdh]',
                            #namespace      = 'oper.multi.fr',
                            #origin         = 'historic',
                            #model          = '[vapp]',
                            #vapp           = self.conf.source_app,
                            #vconf          = self.conf.deterministic_conf,
                            #fatal          = False,
                        ))
                        print(t.prompt, 'tb02 =', tbarp)
                        print()


                        self.sh.title('Toolbox input tb_ebauche')
                        tb_ebauche = toolbox.input(
                            role            = 'Nam_ebauche',
                            source          = 'namelist_ebauche_[geometry]',
                            geometry        = self.conf.vconf,
                            genv            = self.conf.cycle,
                            kind            = 'namelist',
                            model           = self.conf.model,
                            local           = 'EBAUCHE_[vconf]',
                        )
                        print(t.prompt, 'tb_tb_ebauche =', tb_ebauche)
                        print()
                        
                        interp = ''

                    else:
                        # Pour les dates les plus récentes les sorties de la chaine ARPEGE oper en vortex sont 
                        # normalement disponibles sur hendrix

                        self.sh.title('Toolbox input tb02')
                        tbarp.extend(toolbox.input(
                            role           = 'Gridpoint',
                            format         = 'grib',
                            geometry       = self.conf.cpl_geometry,
                            kind           = 'gridpoint',
                            #filtername     = 'concatenate',
                            suite          = 'oper',
                            local          = '[date::ymdh]/ARPEGE[date::ymdh]_[term::hour]',
                            date           = ['{0:s}/-PT6H/-PT{1:s}H'.format(rundate.ymd6h, str(d)) for d in footprints.util.rangex(0, 24, self.conf.cumul)],
                            # Utilisation d'une varibale de conf pour assurer la cohérence des cumuls de precip
                            term           = self.conf.cumul,
                            namespace      = 'vortex.multi.fr',
                            block          = 'forecast',
                            cutoff         = 'assimilation',
                            nativefmt      = '[format]',
                            origin         = 'historic',
                            model          = '[vapp]',
                            vapp           = self.conf.source_app,
                            vconf          = self.conf.deterministic_conf,
                            fatal          = False,
                        ))
                        print(t.prompt, 'tb02 =', tbarp)
                        print()

                rundate = rundate + Period(days=1)

            self.sh.title('Toolbox input tb03 = PRE-TRAITEMENT FORCAGE script')
            tb03 = script = toolbox.input(
                role        = 'pretraitement',
                local       = 'makeP.py',
                genv        = self.conf.cycle,
                kind        = 's2m_filtering_grib',
                language    = 'python',
                rawopts     = '{0:s} -a -d {1:s} -f '.format(interp, self.conf.vconf) + ' '.join(list([str(rh[1].container.basename) for rh in enumerate(tbarp)])),
            )
            print(t.prompt, 'tb03 =', tb03)
            print()


#             self.sh.title('Toolbox input tb04 = PRE-TRAITEMENT FORCAGE script')
#             tb03 = script = toolbox.input(
#                 role        = 'pretraitement',
#                 local       = 'makeP.py',
#                 genv        = 'uenv:s2m.01@vernaym',
#                 kind        = 's2m_filtering_grib',
#                 language    = 'python',
#                 # rawopts     = ' -o -f ' + ' '.join(list(set([str(rh[1].container.basename) for rh in enumerate(tbarp + tbpearp)]))),
#                 rawopts     = '-a -r -d {0:s} -f {1:s}'.format(self.conf.vconf, ' '.join(list(set([str(rh[1].container.basename) for rh in enumerate(tbarp + tbpearp)])))),
#             )
#             print t.prompt, 'tb03 =', tb03
#             print

        if 'fetch' in self.steps:
            pass

        if 'compute' in self.steps:


            self.sh.title('Toolbox algo tb04')
            expresso = toolbox.algo(
                vconf          = self.conf.vconf,
                engine         = 'exec',
                kind           = 'guess',
                interpreter    = 'current',
                # Need to extend pythonpath to be independant of the user environment
                # The vortex-build environment already set up the pythonpath (see jobassistant plugin) but the script is 
                # eventually launched in a 'user-defined' environment
                extendpypath   = [self.sh.path.join('/'.join(self.conf.iniconf.split('/')[:-2]), d) for d in ['vortex/src', 'vortex/site', 'epygram', 'epygram/site', 'epygram/eccodes_python']],
                ntasks         = self.conf.ntasks,
                terms          = footprints.util.rangex(self.conf.ana_terms),
            )
            print(t.prompt, 'tb04 =', expresso)
            print()

#             self.sh.title('Toolbox algo tb04')
#             expresso = toolbox.algo(
#                 vconf          = self.conf.vconf,
#                 engine         = 'exec',
#                 kind           = 'guess',
#                 #terms          = footprints.util.rangex(self.conf.prv_terms),
#                 #members        = footprints.util.rangex(1, 40, 1),
#                 interpreter    = script[0].resource.language,
#                 ntasks         = self.conf.ntasks,
#                 # members        = footprints.util.rangex(self.conf.members)
#             )
#             print t.prompt, 'tb04 =', expresso
#             print

            self.component_runner(expresso, script, fortran = False)

        if 'backup' in self.steps or 'late-backup' in self.steps:

            pass

        if 'late-backup' in self.steps:

            while rundate <= self.conf.dateend:

                # 1. Save generated guess file in the corresponding Vortex experiment for a re-use
                self.sh.title('Toolbox output tb01')
                tb01 = toolbox.output(
                    role           = 'Ebauche',
                    local          = '[date::ymdh]/P[date::addcumul_yymdh]', # TODO : Check if OK
                    geometry       = self.conf.vconf,
                    vapp           = 's2m',
                    vconf          = '[geometry:area]',
                    experiment     = self.conf.xpid,
                    cutoff         = 'assimilation',
                    block          = self.conf.guess_block,
                    date           = ['{0:s}/-PT6H/-PT{1:s}H'.format(rundate.ymd6h, str(d)) for d in footprints.util.rangex(0, 24, self.conf.cumul)],
                    cumul          = self.conf.cumul,
                    nativefmt      = 'ascii',
                    kind           = 'guess',
                    model          = 'safran',
                    source_app     = self.conf.source_app,
                    source_conf    = self.conf.deterministic_conf,
                    namespace      = self.conf.namespace,
                    fatal          = False,
                ),
                print(t.prompt, 'tb01 =', tb01)
                print()

            # WARNING : The following only works for a 1-year execution
            season = self.conf.datebegin.nivologyseason
            tarname = 'p{0:s}.tar'.format(season)
            #thisdir = os.getcwd()
            with tarfile.open(tarname, mode='w') as tarfic:
                for f in glob.glob('*/P????????'):
                    #oldname = os.path.basename(f).split('_')[0]
                    #date = Date.strptime(oldname[1:], '%y%m%d%H') + Period(hours=6)
                    #arcname = 'P{0:s}'.format(date.yymdh)
                    arcname = os.path.basename(f)
                    tarfic.add(f, arcname=arcname)

            self.sh.title('Toolbox output tb05')
            tb05 = toolbox.output(
                role           = 'Ebauche',
                local          = tarname,
                remote         = '/home/vernaym/s2m/[geometry]/{0:s}/{1:s}'.format(self.conf.guess_block, tarname),
                hostname       = 'hendrix.meteo.fr',
                unknownflow    = True,
                username       = 'vernaym',
                tube           = 'ftp',
                geometry       = self.conf.vconf,
                cumul          = self.conf.cumul,
                cutoff         = 'assimilation',
                nativefmt      = 'ascii',
                kind           = 'guess',
                model          = 'safran',
                date           = self.conf.dateend.ymd6h,
            ),
            print(t.prompt, 'tb05 =', tb05)
            print()


            from vortex.tools.systems import ExecutionError
            raise ExecutionError('')
            pass
