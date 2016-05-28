# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division


from numpy import pi
from numpy import zeros
from numpy import sin
from numpy import cos
from numpy import sqrt
from numpy.random import random

from numpy import float32 as npfloat
from numpy import int32 as npint


TWOPI = pi*2
PI = pi



class Leaf(object):

  def __init__(
      self,
      size,
      stp,
      num_sources,
      veins,
      rad,
      sources_dst,
      threads = 256,
      nmax = 1000000
    ):

    self.itt = 0

    self.rad = rad
    self.threads = threads
    self.nmax = nmax
    self.size = size

    self.one = 1.0/size
    self.stp = stp
    self.init_sources = num_sources

    self.sources_dst = sources_dst

    self.__init()
    self.__init_sources(self.init_sources)
    self.__init_veins(veins)
    self.__cuda_init()

  def __init(self):

    self.vnum = 0
    self.snum = 0

    nz = int(1.0/(2*self.rad))
    self.nz = nz

    self.nz2 = self.nz**2
    nmax = self.nmax

    self.sxy = zeros((nmax, 2), npfloat)
    self.dxy = zeros((nmax, 2), npfloat)
    self.sv = zeros(nmax, npint)
    self.tmp = zeros(nmax, npfloat)
    self.zone = zeros(nmax, npint)

    zone_map_size = self.nz2*64
    self.zone_node = zeros(zone_map_size, npint)

    self.zone_num = zeros(self.nz2, npint)

  def __cuda_init(self):

    import pycuda.autoinit
    from helpers import load_kernel

    self.cuda_agg_count = load_kernel(
      'modules/cuda/agg_count.cu',
      'agg_count',
      subs = {'_THREADS_': self.threads}
    )

    self.cuda_agg = load_kernel(
      'modules/cuda/agg.cu',
      'agg',
      subs = {'_THREADS_': self.threads}
    )
    self.cuda_nn = load_kernel(
      'modules/cuda/nn.cu',
      'NN',
      subs = {'_THREADS_': self.threads}
    )

  def __init_sources(self, init_num):

    from dddUtils.random import darts_rect

    sources = darts_rect(
      init_num,
      0.5,
      0.5,
      0.9,
      0.9,
      self.sources_dst
    )

    snum = len(sources)
    self.sxy[:snum,:] = sources[:,:]
    self.snum = snum

  def __init_veins(self, veins):

    self.vnum = len(veins)
    self.vxy = veins.astype(npfloat)

  def __make_zonemap(self):

    from pycuda.driver import In
    from pycuda.driver import Out
    from pycuda.driver import InOut

    vxy = self.vxy
    vnum = self.vnum

    zone_num = self.zone_num
    zone_node = self.zone_node
    zone = self.zone

    zone_num[:] = 0

    self.cuda_agg_count(
      npint(vnum),
      npint(self.nz),
      In(vxy[:vnum,:]),
      InOut(zone_num),
      block=(self.threads,1,1),
      grid=(vnum//self.threads + 1,1)
    )

    zone_leap = zone_num[:].max()
    zone_map_size = self.nz2*zone_leap

    if zone_map_size>len(zone_node):
      print('resize, new zone leap: ', zone_map_size*2./self.nz2)
      zone_node = zeros(zone_map_size*2, npint)

    zone_node[:] = 0
    zone_num[:] = 0

    self.cuda_agg(
      npint(vnum),
      npint(self.nz),
      npint(zone_leap),
      In(vxy[:vnum,:]),
      InOut(zone_num),
      InOut(zone_node),
      Out(zone[:vnum]),
      block=(self.threads,1,1),
      grid=(vnum//self.threads + 1,1)
    )

    return zone_leap, zone_node, zone_num

  def __nn_query(self, zone_leap, zone_node, zone_num):

    from pycuda.driver import In
    from pycuda.driver import Out

    snum = self.snum
    vnum = self.vnum

    sv = self.sv[:snum]
    tmp = self.tmp[:snum]

    self.cuda_nn(
      npint(self.nz),
      npfloat(self.rad),
      npint(zone_leap),
      In(zone_num),
      In(self.zone_node),
      npint(snum),
      npint(vnum),
      In(self.sxy[:snum,:]),
      In(self.vxy[:vnum,:]),
      Out(sv),
      Out(tmp),
      block=(self.threads,1,1),
      grid=(snum//self.threads + 1,1)
    )

    return sv, tmp

  def __grow(self, sxy, vxy, sv):

    print(sv)

  def step(self, t=None):

    self.itt += 1

    zone_leap, zone_node, zone_num = self.__make_zonemap()
    sv, dst = self.__nn_query(zone_leap, zone_node, zone_num)

    return zone_leap, zone_node, zone_num, sv, dst

