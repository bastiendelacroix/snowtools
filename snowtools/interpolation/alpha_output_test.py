#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from matplotlib import cm
import cartopy.crs as ccrs
from cartopy import config

from snowtools.utils import prosimu
from snowtools.plots.maps.cartopy import Map_alpes, MultiMap_Alps, Map_pyrenees, MultiMap_Pyr, Map_corse, MultiMap_Cor, MapFrance

class test_medianfile():
    def __init__(self, outputfile, outputreffile):
        self.ftest = Dataset(outputfile)
        self.fref = Dataset(outputreffile)

    def test(self):
        snowcomp = self.ftest.variables['SD_1DY_ISBA'][:, :]
        snowref = self.fref.variables['SD_1DY_ISBA'][:, :]
        # points = self.fref.variables['']

        diff = snowcomp - snowref
        for time in range(7):
            print(time, snowcomp[time, :].min(), snowcomp[time, :].max())
            print(time, snowref[time, :].min(), snowref[time, :].max())
            print(time, diff[time, :].min(), diff[time, :].max())
            plt.plot(diff[time, :])
            plt.show()

class test_pro():
    def __init__(self, inputzeros, inputnonzeros):
        self.bigfile = Dataset(inputzeros)
        self.smallfile = Dataset(inputnonzeros)

    def test(self):
        snowbig = self.bigfile.variables['SD_1DY_ISBA'][:, :]
        snowsmall = self.smallfile.variables['SD_1DY_ISBA'][:, :]
        slope = self.bigfile.variables['slope'][:]
        slopesmall = self.smallfile.variables['slope'][:]
        massif_small = self.smallfile.variables['massif_num'][:]
        massif_big = self.bigfile.variables['massif_num'][:]
        zs_small = self.smallfile.variables['ZS'][:]
        zs_big = self.bigfile.variables['ZS'][:]
        snowbig_sel = snowbig[:, ::17]
        massif_big_sel = massif_big[::17]
        print(sum(massif_small-massif_big_sel))
        timebig = self.bigfile.variables['time'][:]
        timesmall = self.smallfile.variables['time'][:]
        print(snowsmall.shape)
        print(snowbig.shape)
        snowtrans = np.transpose(snowbig_sel)
        snowtrans = snowtrans.reshape(snowsmall.shape)
        # snowtrans = snowtrans[:, ::17]
        diff = snowsmall - snowtrans
        for time in range(7):
            print(time, snowsmall[time, :].min(), snowsmall[time, :].max())
            print(time, snowbig_sel[time, :].min(), snowbig_sel[time, :].max())
            print(time, diff[time, :].min(), diff[time, :].max())
            plt.plot(diff[time, :])
            plt.show()
        # for ind, ms, zss, testval in zip(range(len(massif_small)), massif_small, zs_small,snowsmall[0, :]):
        #     if testval == 0:
        #         print(ind, ms, zss)
        #     for it in range(7):
        #         [print(ind, i, it, ms, massif_big[i], zss, zs_big[i], slope[i], testval, val) for i, val in enumerate(snowbig[it,:])
        #             if ((testval != 0.) & (abs(val - testval) < 0.00000001))]

class output_test():
    def __init__(self, outputfile, outputreffile, lat_bnds, lon_bnds, figname, flip=True, doubleflip=False):
        self.ftot = Dataset(outputfile)
        self.fcomp = Dataset(outputreffile)
        self.lat_bnds = lat_bnds
        self.lon_bnds = lon_bnds
        self.figname = figname
        self.flip = flip
        self.doubleflip = doubleflip

    def slope_visu(self, figname):
        lats = self.ftot.variables['LAT'][:]
        lons = self.ftot.variables['LON'][:]
        ZS = self.ftot.variables['ZS'][:, :]
        slope = self.ftot.variables['slope'][:, :]
        if self.flip:
            ZS = np.flipud(ZS)
            slope = np.flipud(slope)

        ax = plt.axes(projection=ccrs.PlateCarree())
        plt.pcolormesh(lons, lats, ZS, transform=ccrs.PlateCarree(), cmap=cm.terrain)  # gist_earth
        plt.pcolormesh(lons, lats, slope,  # vmin=-0.0001,
                       transform=ccrs.PlateCarree(), cmap=cm.Reds)
        plt.title("Slopes", y=1.09)

        ax.gridlines(draw_labels=True)
        # plt.imshow(massif);
        m = plt.cm.ScalarMappable(cmap=cm.Reds)
        m.set_array(slope)
        # m.set_clim(-0.0001, snowcomp.max())
        m.cmap.set_under(color='w', alpha=0)
        plt.colorbar(m, orientation="horizontal")
        #
        plt.savefig(figname)

    def test(self):
        massif = self.ftot.variables['massif_num'][:, :]
        lats = self.ftot.variables['LAT'][:]
        lons = self.ftot.variables['LON'][:]
        ZS = self.ftot.variables['ZS'][:, :]
        snow = self.ftot.variables['SD_1DY_ISBA'][7, :, :]

        snowcomp = self.fcomp.variables['SD_1DY_ISBA'][7, :, :]
        complats = self.fcomp.variables['LAT'][:]
        complons = self.fcomp.variables['LON'][:]
        compZS = self.fcomp.variables['ZS'][:, :]
        compmassif = self.fcomp.variables['massif_num'][:, :]

        # print(complons)
        print(complats.min(), complats.max())
        print(complons.min(), complons.max())

        lat_inds = np.where((lats > self.lat_bnds[0]) & (lats < self.lat_bnds[1]))
        lon_inds = np.where((lons > self.lon_bnds[0]) & (lons < self.lon_bnds[1]))
        snow_region = self.ftot.variables['SD_1DY_ISBA'][7, np.min(lat_inds):np.max(lat_inds) + 1,
                                                         np.min(lon_inds):np.max(lon_inds) + 1]
        massif_region = massif[np.min(lat_inds):np.max(lat_inds)+1, np.min(lon_inds):np.max(lon_inds) + 1]
        # print(lons[np.min(lon_inds):np.max(lon_inds)+1])
        print(snow_region.shape)
        print(snowcomp.shape)
        if self.flip:
            diff = snow_region - np.flipud(snowcomp)
            massif_diff = massif_region - np.flipud(compmassif)
        else:
            diff = snow_region - snowcomp
            massif_diff = massif_region - compmassif

        if self.doubleflip:
            diff = np.flipud(diff)
            massif_diff = np.flipud(massif_diff)

        print(massif_diff.min(), massif_diff.max())
        print(len(diff[diff != 0]))
        # print(diff[diff < 999999].max())
        # print(np.unique(massif))

        # ax = plt.axes(projection=ccrs.PlateCarree())
        # plt.pcolormesh(lons, lats, ZS, transform=ccrs.PlateCarree(), cmap=cm.terrain) #gist_earth
        # plt.pcolormesh(lons, lats, snow, vmin=0,
        #              transform=ccrs.PlateCarree(), cmap=cm.bone)

        # ax.gridlines(draw_labels=True)
        # # plt.imshow(massif);
        # m = plt.cm.ScalarMappable(cmap=cm.bone)
        # m.set_array(snow)
        # m.set_clim(0., snow.max())
        # m.cmap.set_under(color='w', alpha=0)
        # plt.colorbar(m, orientation="horizontal")
        # #
        # plt.savefig('snow_test_alps_to_alpha.png')
        lim = max(diff.max(), abs(diff.min()))
        ax = plt.axes(projection=ccrs.PlateCarree())
        plt.pcolormesh(complons, complats, compZS, transform=ccrs.PlateCarree(), cmap=cm.terrain)  # gist_earth
        plt.pcolormesh(complons, complats, diff, vmin=-lim, vmax=lim,
                       transform=ccrs.PlateCarree(), cmap=cm.seismic)

        ax.gridlines(draw_labels=True)
        m = plt.cm.ScalarMappable(cmap=cm.seismic)
        m.set_array(diff)

        m.set_clim(-lim, lim)
        m.cmap.set_under(color='w', alpha=0)
        plt.colorbar(m, orientation="horizontal")
        #
        plt.savefig(self.figname)

        # ax = plt.axes(projection=ccrs.PlateCarree())
        # plt.pcolormesh(complons, complats, np.flipud(compZS), transform=ccrs.PlateCarree(), cmap=cm.terrain)
        # gist_earth
        # plt.pcolormesh(complons, complats, np.flipud(compmassif), #alpha=0.4, # vmin=-1, vmax=1,
        #              transform=ccrs.PlateCarree(), cmap=cm.seismic)
        #
        # ax.gridlines(draw_labels=True)
        # # plt.imshow(massif);
        # m = plt.cm.ScalarMappable(cmap=cm.seismic)
        # m.set_array(compmassif)
        # # m.set_clim(-1.000, 1)
        # # m.cmap.set_over(color='w', alpha=0)
        # plt.colorbar(m, orientation="horizontal")
        # #
        # plt.savefig(self.figname)

        # ax = plt.axes(projection=ccrs.PlateCarree())
        # plt.pcolormesh(complons, complats, compZS, transform=ccrs.PlateCarree(), cmap=cm.terrain) #gist_eart
        #
        # ax.gridlines(draw_labels=True)
        # # plt.imshow(massif);
        # # m = plt.cm.ScalarMappable(cmap=cm.seismic)
        # # m.set_array(diff)
        # #m.set_clim(-0.0001, snowcomp.max())
        # # m.cmap.set_under(color='w', alpha=0)
        # # plt.colorbar(m, orientation="horizontal")
        # #
        # plt.savefig('test_alps_terrain.png')

    def snowtest(self):
        lats = self.ftot.variables['LAT'][:]
        lons = self.ftot.variables['LON'][:]
        snowcomp = self.fcomp.variables['SD_1DY_ISBA'][:, :, :]
        complats = self.fcomp.variables['LAT'][:]
        complons = self.fcomp.variables['LON'][:]
        compmassif = self.fcomp.variables['massif_num'][:, :]

        lat_inds = np.where((lats > self.lat_bnds[0]) & (lats < self.lat_bnds[1]))
        lon_inds = np.where((lons > self.lon_bnds[0]) & (lons < self.lon_bnds[1]))
        snow_region = self.ftot.variables['SD_1DY_ISBA'][:, np.min(lat_inds):np.max(lat_inds) + 1,
                                                         np.min(lon_inds):np.max(lon_inds) + 1]
        massif_region = self.ftot.variables['massif_num'][np.min(lat_inds):np.max(lat_inds) + 1,
                                                          np.min(lon_inds):np.max(lon_inds) + 1]
        if self.flip:
            massif_diff = massif_region - np.flipud(compmassif)
        else:
            massif_diff = massif_region - compmassif
        for i in range(snowcomp.shape[0]):
            if self.flip:
                snowdiff = snow_region[i,:,:] - np.flipud(snowcomp[i,:,:])
            else:
                snowdiff = snow_region[i, :, :] - snowcomp[i, :, :]
            # print(snowdiff.shape)
            print(i, np.sum(snowdiff), sum(snowdiff[massif_diff==0]),
                  np.min(snow_region[i, :, :]), np.min(snowcomp[i,:,:]),
                  np.max(snow_region[i,:,:]), np.max(snowcomp[i,:,:]))


class Alphafile():
    def __init__(self, filename):
        self.ds = Dataset(filename)
        self.lats = self.ds.variables['LAT'][:]
        self.lons = self.ds.variables['LON'][:]
        self.snow = self.ds.variables['SD_1DY_ISBA'][:, :, :, 8]
        self.massifs = self.ds.variables['massif_num'][:,:]
        self.slopes = self.ds.variables['slope'][:,:]


print(config)
attributes = dict(
    PP_SD_1DY_ISBA=dict(convert_unit=1., forcemin=0., forcemax=60., palette='YlGnBu', seuiltext=50.,
                        label=u'Epaisseur de neige fraîche en 24h (cm)'),
    SD_1DY_ISBA=dict(convert_unit=100., forcemin=0., forcemax=50., palette='YlGnBu', seuiltext=50.,
                     label=u'Epaisseur de neige fraîche en 24h (cm)', unit='cm'),
    SD_3DY_ISBA=dict(convert_unit=100., forcemin=0., forcemax=60., palette='YlGnBu', seuiltext=50.,
                     label=u'Epaisseur de neige fraîche en 72h (cm)'),
    RAMSOND_ISBA=dict(convert_unit=100., forcemin=0., forcemax=60., palette='YlGnBu', seuiltext=50.,
                      label=u'Epaisseur mobilisable (cm)'),
    NAT_LEV=dict(forcemin=-0.5, forcemax=5.5, palette='YlOrRd', ncolors=6, label=u'Risque naturel',
                 ticks=[u'Très faible', u'Faible', u'Mod. A', u'Mod. D', u'Fort', u'Très fort']),
    naturalIndex=dict(forcemin=0., forcemax=8., palette='YlOrRd', label=u'Indice de risque naturel',
                      format= '%.1f', nolevel=True),
    DSN_T_ISBA=dict(convert_unit=100., label=u'Hauteur de neige (cm)'),
    WSN_T_ISBA=dict(label=u'Equivalent en eau (kg/m2)'),
    SNOMLT_ISBA=dict(convert_unit=3. * 3600., forcemin=0., forcemax=60., palette='YlGnBu', seuiltext=50.,
                     label=u'Ecoulement en 3h (kg/m2/3h)'),
    WET_TH_ISBA=dict(convert_unit=100., forcemin=0., forcemax=60., palette='YlGnBu', seuiltext=50.,
                     label=u'Epaisseur humide (cm)'),
    REFRZTH_ISBA=dict(convert_unit=100., forcemin=0., forcemax=60., palette='YlGnBu', seuiltext=50.,
                      label=u'Epaisseur regelée (cm)'),
    RAINF_ISBA=dict(convert_unit=3. * 3600., forcemin=0., forcemax=60., palette='YlGnBu', seuiltext=50.,
                    label=u'Pluie en 3h (kg/m2/3h)'),
)

### rectangle case ###
# sim000 = prosimu.prosimu("/home/radanovicss/Hauteur_neige_median/PRO_2020092706_2020092806_mb000.nc")
# sim001 = prosimu.prosimu("/home/radanovicss/Hauteur_neige_median/PRO_2020092706_2020092806_mb001.nc")
# sim002 = prosimu.prosimu("/home/radanovicss/Hauteur_neige_median/PRO_2020092706_2020092806_mb002.nc")
# points_nord = sim000.get_points(aspect=0, ZS=2100, slope=40)
# sim000_nord = sim000.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# sim001_nord = sim001.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# sim002_nord = sim002.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# points_sud = sim000.get_points(aspect=180, ZS=2100, slope=40)
# sim000_sud = sim000.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# sim001_sud = sim001.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# sim002_sud = sim002.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# massifs = sim000.read('massif_num', selectpoint=points_nord)
# m = Map_alpes(geofeatures=True)
# m.init_massifs(**attributes['NAT_LEV'])
# # print('massif init done')
# m.add_north_south_info()
# m.rectangle_massif(massifs, [0, 1, 2], [sim000_sud[2,:], sim001_sud[2,:], sim002_sud[2,:],
#                                        sim000_nord[2,:], sim001_nord[2,:], sim002_nord[2,:]], ncol=2,
#                    **attributes['NAT_LEV'])
# # m.plot_center_massif(massifs, massifs)
# # m.reset_massifs()
# # m.plot_center_massif(massifs, massifs)
# m.addlogo()
# m.set_maptitle("2020092712")
# m.set_figtitle("2100m")
# m.save("cartopy_massifs_2020092712_alps_matplotlib3.2_test.png", formatout="png")
# m.rectangle_massif(massifs, [0, 1, 2], [sim000_nord[2,:], sim001_nord[2,:], sim002_nord[2,:],
#                                         sim000_sud[2,:], sim001_sud[2,:], sim002_sud[2,:]], ncol=2,
#                    **attributes['NAT_LEV'])
# m.save("cartopy_massifs_2020092712_alps_matplotlib3.2_test_changetables.png", formatout="png")
#
# m.close()

# pyr
# sim000 = prosimu.prosimu("/home/radanovicss/PycharmProjects/snowtools_git/tasks/oper/pyr/2020092806/mb000/PRO_2020092706_2020092806.nc")
# sim001 = prosimu.prosimu("/home/radanovicss/PycharmProjects/snowtools_git/tasks/oper/pyr/2020092806/mb001/PRO_2020092706_2020092806.nc")
# sim002 = prosimu.prosimu("/home/radanovicss/PycharmProjects/snowtools_git/tasks/oper/pyr/2020092806/mb002/PRO_2020092706_2020092806.nc")
# points_nord = sim000.get_points(aspect=0, ZS=1800, slope=40)
# sim000_nord = sim000.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# sim001_nord = sim001.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# sim002_nord = sim002.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# points_sud = sim000.get_points(aspect=180, ZS=1800, slope=40)
# sim000_sud = sim000.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# sim001_sud = sim001.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# sim002_sud = sim002.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# massifs = sim000.read('massif_num', selectpoint=points_nord)
# m = Map_pyrenees(geofeatures=True)
# m.init_massifs(**attributes['NAT_LEV'])
# m.add_north_south_info()
# m.rectangle_massif(massifs, [0, 1, 2], [sim000_sud[2,:], sim001_sud[2,:], sim002_sud[2,:],
#                                         sim000_nord[2,:], sim001_nord[2,:], sim002_nord[2,:]], ncol=2,
#                    **attributes['NAT_LEV'])
# m.plot_center_massif(massifs, massifs)
# # m.reset_massifs()
# # m.plot_center_massif(massifs, massifs)
# m.addlogo()
# m.set_maptitle("2020092712")
# m.set_figtitle("1800m")
#
# m.save("cartopy_massifs_2020092712_pyr_tab_test.png", formatout="png")
# m.close()
#
# # cor
# sim000 = prosimu.prosimu("/home/radanovicss/PycharmProjects/snowtools_git/tasks/oper/cor/2020092806/mb000/PRO_2020092706_2020092806.nc")
# sim001 = prosimu.prosimu("/home/radanovicss/PycharmProjects/snowtools_git/tasks/oper/cor/2020092806/mb001/PRO_2020092706_2020092806.nc")
# sim002 = prosimu.prosimu("/home/radanovicss/PycharmProjects/snowtools_git/tasks/oper/cor/2020092806/mb002/PRO_2020092706_2020092806.nc")
# points_nord = sim000.get_points(aspect=0, ZS=1800, slope=40)
# sim000_nord = sim000.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# sim001_nord = sim001.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# sim002_nord = sim002.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# points_sud = sim000.get_points(aspect=180, ZS=1800, slope=40)
# sim000_sud = sim000.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# sim001_sud = sim001.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# sim002_sud = sim002.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# massifs = sim000.read('massif_num', selectpoint=points_nord)
# m = Map_corse(geofeatures=True)
# m.init_massifs(**attributes['NAT_LEV'])
# m.add_north_south_info()
# m.rectangle_massif(massifs, [0, 1, 2], [sim000_sud[2,:], sim001_sud[2,:], sim002_sud[2,:],
#                                         sim000_nord[2,:], sim001_nord[2,:], sim002_nord[2,:]], ncol=2,
#                    **attributes['NAT_LEV'])
# m.plot_center_massif(massifs, massifs)
# # m.reset_massifs()sim000 = prosimu.prosimu("/home/radanovicss/Hauteur_neige_median/PRO_2020092706_2020092806_mb000.nc")
# sim001 = prosimu.prosimu("/home/radanovicss/Hauteur_neige_median/PRO_2020092706_2020092806_mb001.nc")
# sim002 = prosimu.prosimu("/home/radanovicss/Hauteur_neige_median/PRO_2020092706_2020092806_mb002.nc")
# points_nord = sim000.get_points(aspect=0, ZS=2100, slope=40)
# sim000_nord = sim000.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# sim001_nord = sim001.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# sim002_nord = sim002.read('NAT_LEV', selectpoint=points_nord, hasDecile=False)
# points_sud = sim000.get_points(aspect=180, ZS=2100, slope=40)
# sim000_sud = sim000.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# sim001_sud = sim001.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# sim002_sud = sim002.read('NAT_LEV', selectpoint=points_sud, hasDecile=False)
# massifs = sim000.read('massif_num', selectpoint=points_nord)
# m = Map_alpes(geofeatures=True)
# m.init_massifs(**attributes['NAT_LEV'])
# # print('massif init done')
# m.add_north_south_info()
# m.rectangle_massif(massifs, [0, 1, 2], [sim000_sud[2,:], sim001_sud[2,:], sim002_sud[2,:],
#                                        sim000_nord[2,:], sim001_nord[2,:], sim002_nord[2,:]], ncol=2,
#                    **attributes['NAT_LEV'])
# # m.plot_center_massif(massifs, massifs)
# # m.reset_massifs()
# # m.plot_center_massif(massifs, massifs)
# m.addlogo()
# m.set_maptitle("2020092712")
# m.set_figtitle("2100m")
# m.save("cartopy_massifs_2020092712_alps_matplotlib3.2_test.png", formatout="png")
# m.rectangle_massif(massifs, [0, 1, 2], [sim000_nord[2,:], sim001_nord[2,:], sim002_nord[2,:],
#                                         sim000_sud[2,:], sim001_sud[2,:], sim002_sud[2,:]], ncol=2,
#                    **attributes['NAT_LEV'])
# m.save("cartopy_massifs_2020092712_alps_matplotlib3.2_test_changetables.png", formatout="png")
#
# m.close()
# # m.plot_center_massif(massifs, massifs)
# m.addlogo()
# m.set_maptitle("2020092712")
# m.set_figtitle("1800m")
#
# m.save("cartopy_massifs_2020092712_cor_tab_test.png", formatout="png")
# m.close()

postproc = prosimu.prosimu("/home/radanovicss/Hauteur_neige_median/Percentiles/Alp/postproc_2021041006_2021041406.nc")
print(postproc.listvar(), postproc.listdim())
points = postproc.get_points(aspect=-1, ZS=2100)
postproc_flat = postproc.read('SD_1DY_ISBA', selectpoint=points, hasDecile=True)
massifs = postproc.read('massif_num', selectpoint=points)
# massifs2 = postproc.read('massif_num')
# print(np.unique(massifs))
# print(postproc_flat.shape, massifs.shape, postproc_flat[5, :, :].max())
m = Map_alpes(geofeatures=True)
print(m.latmax, m.infospos)
m.init_massifs(**attributes['SD_1DY_ISBA'])
m.draw_massifs(massifs, postproc_flat[5, :, 8], **attributes['SD_1DY_ISBA'])
m.plot_center_massif(massifs, postproc_flat[5, :, 0], postproc_flat[5, :, 4], postproc_flat[5, :, 8],
                     **attributes['SD_1DY_ISBA'])
m.add_north_south_info()
m.addlogo()
m.set_maptitle("2021041112 percentile 90")
m.set_figtitle("2100m")

m.save("cartopy_massifs_2021041112_alps_refactor_test.png", formatout="png")
m.close()
#
# lo = MultiMap_Alps(nrow=3, ncol=3, geofeatures=True)
# lo.init_massifs(**attributes['SD_1DY_ISBA'])
# # lo.draw_massifs(massifs,postproc_flat[5,:,:], axis=1, **attributes['SD_1DY_ISBA'])
# lo.set_figtitle("SD_1DY_ISBA 2021041112 2100m")
# titles = ['Percentile {0}'.format(i) for i in range(10, 100, 10)]
# lo.set_maptitle(titles)
# lo.plot_center_massif(massifs, postproc_flat[5,:,:], axis=1, **attributes['SD_1DY_ISBA'])
# lo.add_north_south_info()
# lo.addlogo()
# lo.save("cartopy_massifs_multi_2021041112_alps_no_so_box.png", formatout="png")

# postproc = prosimu.prosimu("/home/radanovicss/Hauteur_neige_median/Percentiles/Pyr/postproc_2021041006_2021041406.nc")
# print(postproc.listvar(), postproc.listdim())
# points = postproc.get_points(aspect = -1, ZS=1800)
# postproc_flat = postproc.read('SD_1DY_ISBA', selectpoint=points, hasDecile=True)
# massifs = postproc.read('massif_num', selectpoint=points)
# # massifs2 = postproc.read('massif_num')
# # print(np.unique(massifs))
# # print(postproc_flat.shape, massifs.shape)
# # [print(i, postproc_flat[i, :, :].max()) for i in range(32)]
# m = Map_pyrenees(geofeatures=True)
# m.init_massifs(**attributes['SD_1DY_ISBA'])
# # m.draw_massifs(massifs,postproc_flat[16,:,8], **attributes['SD_1DY_ISBA'])
# m.set_maptitle("2021041212 percentile 90")
# m.set_figtitle("1800m")
# m.plot_center_massif(massifs, postproc_flat[27,:,0], postproc_flat[27,:,4], postproc_flat[27,:,8], **attributes['SD_1DY_ISBA'])
# m.add_north_south_info()
# m.addlogo()
#
# m.save("cartopy_massifs_2021041212_pyr_no_so_box.png", formatout="png")
# m.close()
#
# lo = MultiMap_Pyr(nrow=3, ncol=3, geofeatures=True)
# lo.init_massifs(**attributes['SD_1DY_ISBA'])
# # lo.draw_massifs(massifs, postproc_flat[16,:,:], axis=1, **attributes['SD_1DY_ISBA'])
# lo.plot_center_massif(massifs, postproc_flat[27,:,:], axis=1, **attributes['SD_1DY_ISBA'])
# lo.set_figtitle("SD_1DY_ISBA 2021041212 1800m")
# titles = ['Percentile {0}'.format(i) for i in range(10, 100, 10)]
# lo.set_maptitle(titles)
# lo.add_north_south_info()
# lo.addlogo()
# lo.save("cartopy_massifs_multi_2021041212_pyr_no_so_box.png", formatout="png")
# lo.close()

# postproc = prosimu.prosimu("/home/radanovicss/Hauteur_neige_median/Percentiles/Cor/postproc_2021041006_2021041406.nc")
# print(postproc.listvar(), postproc.listdim())
# points = postproc.get_points(aspect = -1, ZS=1800)
# postproc_flat = postproc.read('SD_1DY_ISBA', selectpoint=points, hasDecile=True)
# massifs = postproc.read('massif_num', selectpoint=points)
# massifs2 = postproc.read('massif_num')
# print(np.unique(massifs))
# print(postproc_flat.shape, massifs.shape)
# #[print(i, postproc_flat[i, :, :].max()) for i in range(32)]
# m = Map_corse(geofeatures=True)
# m.init_massifs(**attributes['SD_1DY_ISBA'])
# # m.draw_massifs(massifs, postproc_flat[27,:,8], **attributes['SD_1DY_ISBA'])
# m.plot_center_massif(massifs, postproc_flat[27,:,0], postproc_flat[27,:,4], postproc_flat[27,:,8], **attributes['SD_1DY_ISBA'])
# m.set_maptitle("2021041318 percentile 90")
# m.add_north_south_info()
# m.addlogo()
# # m.set_figtitle("1800m")
# #
# m.save("cartopy_massifs_2021041318_cor_test_box.png", formatout="png")
# m.close()
#
# lo = MultiMap_Cor(nrow=3, ncol=3, geofeatures=True)
# lo.init_massifs(**attributes['SD_1DY_ISBA'])
# # lo.draw_massifs(massifs, postproc_flat[27,:,:], axis=1, **attributes['SD_1DY_ISBA'])
# # lo.plot_center_massif(massifs, postproc_flat[27,:,:], axis=1, **attributes['SD_1DY_ISBA'])
# lo.set_figtitle("SD_1DY_ISBA 2021041318 1800m")
# lo.addlogo()
# # lo.empty_massifs()
# lo.add_north_south_info()
# # titles = ['Percentile {0}'.format(i) for i in range(10, 100, 10)]
# # lo.set_maptitle(titles)
# lo.save("cartopy_massifs_multi_2021041318_cor_no_so_box.png", formatout="png")
# lo.close()

# indata = Alphafile("grid_postproc_2021041006_2021041406_cor.nc")
# print(indata.snow[27,:,:,8].max(), indata.snow[27,:,:,8].min())
# m = Map_corse(geofeatures=True)
# m.init_massifs(**attributes['SD_1DY_ISBA'])
# m.draw_mesh(indata.lons, indata.lats, np.flipud(indata.snow[27,:,:,8]), **attributes['SD_1DY_ISBA'])
# m.set_figtitle("SD_1DY_ISBA 2021041318")
# m.set_maptitle("Percentile 90")
# m.save("grid_postproc_p90_2021041318_cor.png", formatout="png")
# m.close()

# indata = Alphafile("/home/radanovicss/Interpol_hauteur_neige/Results/Test_MPI/Test_2D_multi2single/1Proc/grid_postproc_2021041006_2021041406_all2alpha_testwrite2.nc")
# indata_multi = Alphafile("/home/radanovicss/Interpol_hauteur_neige/Results/Test_MPI/Test_2D_multi2single/Multiproc/grid_postproc_2021041006_2021041406_all2alpha_testmpi.nc")
# for i in range(32):
# #    print(i, indata.snow[i,:,:].max(), indata_multi.snow[i,:,:].max(), indata.snow[i,:,:].min(), indata_multi.snow[i,:,:].min())
#     print(i, np.sum(indata.snow[i,:,:] - indata_multi.snow[i,:,:]))
# print(np.sum(indata.lats - indata_multi.lats), np.sum(indata.lons - indata_multi.lons),
#       np.sum(indata.massifs - indata_multi.massifs), np.sum(indata.slopes - indata_multi.slopes))

# m = MapFrance(geofeatures=False, bgimage=True)
# m.init_massifs(**attributes['SD_1DY_ISBA'])
# m.draw_mesh(indata.lons, indata.lats, indata.snow[18,:,:], **attributes['SD_1DY_ISBA'])
# m.set_figtitle("SD_1DY_ISBA 2021041218")
# m.set_maptitle("Percentile 90")
# m.save("grid_postproc_p90_2021041218_alpha_terrimage.png", formatout="png")
# m.close()


# test_median = test_medianfile("/home/radanovicss/Hauteur_neige_median/Out_Belenos/postproc_2020092706_2020092806.nc",
#                               "/home/radanovicss/Hauteur_neige_median/Out_Belenos/cdo_median_numpy_2020092706_2020092806.nc")
# test_median.test()
# test_mb000 = test_medianfile("/home/radanovicss/Hauteur_neige_median/Out_Belenos/pro_2020092706_2020092806.nc",
#                              "/home/radanovicss/Hauteur_neige_median/PRO_2020092706_2020092806_mb000.nc")
# test_mb000.test()
# test_input = test_pro("PRO_2020092706_2020092806_mb035_alps.nc",
#                       "PRO_2020092706_2020092806_mb035_zeroslope_mslab_alps.nc")
# test_input.test()

# def test_pyr():

    # ALPS
# lat_bnds, lon_bnds = [43.909, 46.42], [5.19, 7.77]
# PYRENNEES
# lat_bnds, lon_bnds = [42.07, 43.18], [-1.63, 2.71]
# CORSE
# lat_bnds, lon_bnds = [41.69, 42.56], [8.779, 9.279]
# alp_test = output_test("test_ignore_nonzeroslopes_allslopes_alps.nc",
#                        "test_ignore_nonzeroslopes_zeroslopes_alps.nc",
#                        lat_bnds=[43.909, 46.42], lon_bnds = [5.19, 7.77],
#                        figname='diff_test_ignore_nonzeroslopes_alps.png',
#                        flip=False, doubleflip=True)
# alp_test.snowtest()
# alp_test.test()
# alp_test.slope_visu('resolved_slopes_alps.png')
# pyr_test = output_test("dev_multiin_singleout_test_single_in_single_out_pyr.nc",
#                        "output_mulitin_zeroslope_input_pyr.nc",
#                        lat_bnds=[42.07, 43.18], lon_bnds = [-1.63, 2.71],
#                        figname='diff_test_pyr_to_pyr_dev_multiin_singleout_pyr.png',
#                        flip=False)
# pyr_test.test()
# pyr_test.snowtest()

# corse_test = output_test("test_v2_multi_in_single_out_alpha.nc",
#                          "output_mulitin_zeroslope_input_cor.nc",
#                        lat_bnds=[41.69, 42.56], lon_bnds = [8.779, 9.279],
#                        figname='diff_test_all_to_alpha_dev_multiin_singleout_cor.png', flip=True)
# corse_test.test()
# corse_test.snowtest()
# corse_massiftest = output_test("/home/radanovicss/Interpol_hauteur_neige/Results/Alpha_output_file_test/output_cor_alpha.nc", "output_original_version_zeroslope_input_cor.nc",
#                        lat_bnds=[41.69, 42.56], lon_bnds = [8.779, 9.279],
#                        figname='massif_comp_test_cor_to_alpha_flipped.png')
# #corse_massiftest.test()
# corse_massiftest.snowtest()
