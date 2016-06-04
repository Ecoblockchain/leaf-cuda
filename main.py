#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import print_function
from __future__ import division


def get_wrap(l, colors, node_rad, render_steps=10, export_steps=10):

  from time import time
  from time import strftime
  from dddUtils.ioOBJ import export_2d as export
  from numpy.random import random

  t0 = time()

  from fn import Fn
  fn = Fn(prefix='./res/')

  rndcolors = random((l.nz2,3))
  rndcolors[:,0] *= 0.1
  step = l.step()

  def wrap(render):

    final = False
    vs_xy = []

    try:
      vs_xy = step.next()
    except StopIteration:
      final = True

    if (l.itt % render_steps == 0) or final:

      snum = l.snum
      vnum = l.vnum
      edges = l.edges[:l.enum,:]

      sxy = l.sxy[:snum,:]
      vxy = l.vxy[:vnum,:]

      zsize = len(l.zone_node)
      print(strftime("%Y-%m-%d %H:%M:%S"), 'itt', l.itt,
          'snum', snum, 'vnum', vnum, 'zone', zsize, 'time', time()-t0)

      render.clear_canvas()
      r = node_rad*0.5

      # # nearby
      # render.set_front(colors['cyan'])
      # for v,s in vs_xy:
        # render.line(v[0], v[1], s[0], s[1])

      # veins
      # render.set_front(colors['front'])
      # for i,(x,y) in enumerate(vxy):
        # render.circle(x, y, r, fill=True)

      # edges
      render.set_front(colors['front'])
      for xx in vxy[edges,:]:
        render.line(*xx.flatten())

      # # sources
      render.set_front(colors['light'])
      for x,y in sxy:
        render.circle(x, y, 0.5*r, fill=True)


    if (l.itt % export_steps == 0) or final:
      name = fn.name()
      render.write_to_png(name+'.png')
      # export('leaf', name+'.2obj', vxy)

    if final:
      return False

    return True

  return wrap



def main():

  from modules.leaf import LeafClosed as Leaf
  from render.render import Animate
  from numpy.random import random
  from numpy import array

  colors = {
    'back': [1,1,1,1],
    'front': [0,0,0,1.0],
    'cyan': [0,0.6,0.6,0.3],
    'red': [0.7,0.0,0.0,0.8],
    'blue': [0.0,0.0,0.7,0.8],
    'light': [0,0,0,0.2],
  }

  threads = 256

  render_steps = 1
  export_steps = 2000

  size = 1024
  one = 1.0/size

  node_rad = 10*one

  area_rad = 4*node_rad
  sources_rad = 1.5*node_rad
  stp = node_rad
  kill_rad = node_rad

  # init_num_sources = 4
  # init_veins = 0.2+0.6*random((init_num_sources,2))
  init_veins = array([[0.5, 0.5]])

  init_num_sources = 100000

  # from dddUtils.random import darts
  # init_sources = darts(init_num_sources, 0.5, 0.5, 0.45, sources_rad)
  from dddUtils.random import darts_rect
  init_sources = darts_rect(init_num_sources, 0.5, 0.5, 0.95, 0.95, sources_rad)

  L = Leaf(
    size,
    stp,
    init_sources,
    init_veins,
    area_rad,
    kill_rad,
    sources_rad,
    threads = threads
  )
  print('nz', L.nz)
  print('dens', L.sv_leap)

  wrap = get_wrap(
    L,
    colors,
    node_rad=node_rad,
    export_steps=export_steps,
    render_steps=render_steps
  )

  render = Animate(size, colors['back'], colors['front'], wrap)
  render.set_line_width(L.one*2)
  render.start()


if __name__ == '__main__':

  main()

