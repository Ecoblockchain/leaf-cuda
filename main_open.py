#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import print_function
from __future__ import division


def get_wrap(l, colors, render_steps=10, export_steps=10):

  from time import time
  from time import strftime
  from modules.helpers import show_open
  from numpy.random import random

  t0 = time()

  from fn import Fn
  fn = Fn(prefix='./res/')

  rndcolors = random((l.nz2,3))
  rndcolors[:,0] *= 0.1
  step = l.step()

  def wrap(render):

    try:
      sv = step.next()
    except StopIteration:
      return False

    if l.itt % render_steps == 0:

      snum = l.snum
      vnum = l.vnum

      # sxy = l.sxy[:snum,:]
      vxy = l.vxy[:vnum,:]

      print(strftime("%Y-%m-%d %H:%M:%S"), 'itt', l.itt, 'snum', snum, 'vnum', vnum, 'time', time()-t0)

      render.clear_canvas()

      # veins
      render.set_front(colors['front'])
      for x,y in vxy:
        render.circle(x, y, l.one, fill=True)

      # # sources
      # render.set_front(colors['cyan'])
      # for x,y in sxy:
        # render.circle(x, y, l.one, fill=True)

      # # nearby
      # render.set_front(colors['front'])
      # show_open(render, snum, sxy, vxy, sv)

    if l.itt % export_steps == 0:
      name = fn.name()
      render.transparent_pix()
      render.write_to_png(name+'.png')

    return True

  return wrap



def main():

  from modules.leaf_open import LeafOpen as Leaf
  from render.render import Animate
  from numpy.random import random
  from numpy import array
  from numpy import pi
  from numpy import column_stack
  from numpy import sin
  from numpy import cos

  colors = {
    'back': [1,1,1,1],
    'front': [0,0,0,0.5],
    'cyan': [0,0.6,0.6,0.3],
    'red': [0.7,0.0,0.0,0.3],
    'light': [0,0,0,0.2],
  }

  threads = 512

  render_steps = 10
  export_steps = 10

  size = 512*2
  one = 1.0/size

  node_rad = 2*one

  area_rad = 5*node_rad
  sources_rad = 1*node_rad
  stp = node_rad*0.5
  kill_rad = node_rad

  # init_veins = 0.2+0.6*random((10,2))
  # init_veins = array([[0.5]*2])
  phi = random(3)*2*pi
  init_veins = 0.5+column_stack([cos(phi), sin(phi)])*0.45


  from dddUtils.random import darts
  init_num_sources = 100000
  init_sources = darts(init_num_sources, 0.5, 0.5, 0.45, sources_rad)

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

  wrap = get_wrap(
    L,
    colors,
    export_steps=export_steps,
    render_steps=render_steps
  )

  render = Animate(size, colors['back'], colors['front'], wrap)
  render.set_line_width(L.one)
  render.start()


if __name__ == '__main__':

  main()
