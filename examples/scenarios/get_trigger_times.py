#!/usr/bin/env python

import yaml
import argparse
import numpy as np

parser = argparse.ArgumentParser('round_event_times')

parser.add_argument('seeds', type=str, nargs='+')
parser.add_argument('-tres', type=float, default=1.0) # Time resolution for events
parser.add_argument('-ls-int', type=str, default='dt 1 lc 0') # Gnuplot linestyle for interventions
parser.add_argument('-ls-trig', type=str, default='dt 1 lc rgb "#ff0000"') # Gnuplot linestyle for triggers

args = parser.parse_args()

for seed in args.seeds:
    # Open the original parameter file
    param_history = []
    with open(seed + '.yaml') as f:
        data = yaml.safe_load(f)
        params = data['parameters']
        tmax = data['meta']['tmax']
    param_history.append((0, params))
    with open(seed + '-out-0-events.yaml') as f:
        events = yaml.safe_load(f)
    # Merge non-unique events
    event_times = np.array([e['time'] for e in events])
    event_times = np.round(event_times/args.tres)*args.tres
    event_times, inds = np.unique(event_times, True)
    
    for t, e_i in zip(event_times, inds):
        e = events[e_i]
        params = dict(param_history[-1][1])
        params.update(e['parameters'])
        param_history.append((t, params))

    # Now extract the values we care for
    times, _ = zip(*param_history)
    times = list(times) + [tmax]
    phist = np.array([[p['c'] for t, p in param_history],
                      [p['theta'] for t, p in param_history],
                      [p['eta']*p['chi'] for t, p in param_history]])

    # Ranges?
    pranges = np.amin(phist, axis=1), np.amax(phist, axis=1)
    
    graph_Ymin = 0.5
    graph_Yh = 0.1
    graph_maxa = 0.5
    graph_colors = ['#aa3366', '#0066aa', '#00aa66']
    graph_labels = ['c', '{/Symbol q}', '{/Symbol h}{/Symbol c}']

    gpfname = seed + '-events.gp'
    with open(gpfname, 'w') as f:
        f.write('set xrange [0:{0}]\n'.format(tmax))
        for i in range(3):
            if pranges[1][i]-pranges[0][i] == 0:
                continue # Skip 0 range
            y0 = graph_Ymin+graph_Yh*i
            y1 = y0 + graph_Yh
            f.write('set label "{0}" at graph 0.9,{1}\n'.format(graph_labels[i], (y0+y1)/2))
            for j in range(len(times)-1):
                p = phist[i][j]
                t0 = times[j]
                t1 = times[j+1]
                pnorm = p/pranges[1][i]
                f.write('set style rect fc rgb "{0}" fs solid {1} noborder lw 0\n'.format(graph_colors[i], pnorm*graph_maxa))
                f.write('set obj rect from {0}, graph {1} to {2}, graph {3}\n'.format(t0,y0, t1, y1))


    # if fname[-12:] != '-events.yaml':
    #     print('File is not a valid events file!')
    #     continue
    # with open(fname) as f:
    #     events = yaml.safe_load(f)
    # # Find event times
    # event_times = np.array([e['time'] for e in events])
    # event_times = np.round(event_times/args.tres)*args.tres
    # is_trigger = np.array(['condition' in e for e in events])
    # event_times, inds = np.unique(event_times, True)
    # is_trigger = is_trigger[inds]
    # # Print them out
    # efname = fname.replace('-events.yaml', '-event-times.gp')
    # with open(efname, 'w') as f:
    #     for t, et in zip(event_times, is_trigger):
    #         ls = args.ls_int if not et else args.ls_trig
    #         f.write('set arrow from {0}, graph 0 to {0}, graph 1 nohead {1}\n'.format(t, ls))