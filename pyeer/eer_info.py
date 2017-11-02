# -*- coding:utf-8 -*-

import argparse
from os.path import join

import matplotlib.pyplot as plt
import matplotlib.font_manager as font
import numpy as np

from stats import calculate_eer, calculate_eer_step_by_step

__copyright__ = 'Copyright 2016'
__author__ = u'Bsc. Manuel Aguado Martínez'


def __get_score(line):
    """Get the score value from an input score file line

    Keyword Arguments:
    line -- An input score file line
    """
    sline = line.strip().split(' ')
    return float(sline[-1])


def get_eer_info():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required=True, help="path to exp files")
    ap.add_argument("-i", "--iscores_files", required=True,
                    help="Impostor exp file names separated by comma")
    ap.add_argument("-g", "--gscores_files", required=True,
                    help="Genuine exp file names separated by comma")
    ap.add_argument("-e", "--experiment_ids", required=True,
                    help="Experiment names separated by comma")
    ap.add_argument("-lw", "--line_width", required=False, default=3,
                    help="The width of the plotted curves (default=5)")
    ap.add_argument("-ls", "--legend_font_size", required=False, default=15,
                    help="The size of the legend font (default=20)")
    ap.add_argument("-ht", "--hist", required=False, action='store_true',
                    help="Indicates that the impostor file is in"
                         "histogram format")
    ap.add_argument("-s", "--save_plots", required=False, action='store_true',
                    help="Indicates whether to save the plots instead of"
                         " showing them")
    ap.add_argument("-sp", "--save_path", required=False, default='',
                    help="Path to save the plots in the cases where the option"
                         " -s was specified")
    ap.add_argument("-sf", "--save_format", required=False, default='png',
                    help="Format to save the plots in the cases where the"
                         " option -s was specified. Valid formats are: "
                         "(png, pdf, ps, eps and svg)")
    ap.add_argument("-sr", "--save_dpi", required=False, default=None,
                    help="Plots resolution (dots per inch) in the cases"
                         " where the option -s was specified. If not given"
                         " it will default to the value savefig.dpi in the"
                         " matplotlibrc file")
    ap.add_argument("-ts", "--thr_step", required=False, default=0,
                    help="The value in which increase the threshold at each"
                         " step, if 0 (default) we will use the scores as"
                         " thrs")
    args = ap.parse_args()

    # Parsing arguments
    gscores_files = [f.strip() for f in args.gscores_files.split(',')]
    iscores_files = [f.strip() for f in args.iscores_files.split(',')]
    experiment_ids = [e.strip() for e in args.experiment_ids.split(',')]
    experiments = zip(gscores_files, iscores_files, experiment_ids)
    line_width = int(args.line_width)
    legend_font = int(args.legend_font_size)

    # Preparing plots
    eer_fig = plt.figure()
    eer_plot = eer_fig.add_subplot(111)
    eer_plot.grid(True)
    eer_plot.set_ylabel('Error')
    eer_plot.set_xlabel('Matching Scores')
    eer_plot.set_title('fmr and fnmr Curves')

    det_fig = plt.figure()
    det_plot = det_fig.add_subplot(111)
    det_plot.set_title('DET Curves')
    det_plot.grid(True)
    det_plot.set_ylabel('fnmr')
    det_plot.set_xlabel('fmr')

    roc_fig = plt.figure()
    roc_plot = roc_fig.add_subplot(111)
    roc_plot.set_title('ROC Curves')
    roc_plot.grid(True)
    roc_plot.set_ylabel('1 - fnmr')
    roc_plot.set_xlabel('fmr')
    roc_plot.plot([0, 1], [0, 1], 'k--', linewidth=line_width)

    for exp in experiments:
        # Printing experiment log header
        print(''.join(['=' for _ in xrange(len(exp[2]) + 12)]))
        print('Experiment: ' + exp[2])
        print(''.join(['=' for _ in xrange(len(exp[2]) + 12)]))

        # Loading scores
        print('Loading genuine scores file...')
        with open(join(args.path, exp[0])) as tf:
            genuine_match = [__get_score(line) for line in tf]

        print('Loading impostor scores file...')
        with open(join(args.path, exp[1])) as tf:
            impostor_match = [__get_score(line) for line in tf]

        print('Calculating probabilities...')
        if args.thr_step != 0 or args.hist:
            # Setting threshold step for step by step calculation
            thr_step = (1 if args.hist and args.thr_step == 0
                        else float(args.thr_step))

            # Calculating probabilities step by step
            roc_info = calculate_eer_step_by_step(genuine_match,
                                                  impostor_match,
                                                  thr_step, args.hist)
        else:
            # Calculating probabilities using scores as thrs
            roc_info = calculate_eer(genuine_match, impostor_match)

        # Unboxing probability rates and info
        (thrs, fmr, fnmr, eer) = roc_info

        # Printing EER and operation points values
        print(exp[2] + ' EER \t= ' + str(eer))

        index = np.argmin(abs(fmr - 0))
        print(exp[2] + ' FNMR_0 \t= ' + str(fnmr[index]))

        index = np.argmin(abs(fmr - 0.2))
        print(exp[2] + ' FNMR_5 \t= ' + str(fnmr[index]))

        index = np.argmin(abs(fmr - 0.1))
        print(exp[2] + ' FNMR_10 \t= ' + str(fnmr[index]))

        index = np.argmin(abs(fmr - 0.05))
        print(exp[2] + ' FNMR_20 \t= ' + str(fnmr[index]))

        index = np.argmin(abs(fmr - 0.001))
        print(exp[2] + ' FNMR_100 \t= ' + str(fnmr[index]))

        index = np.argmin(abs(fmr - 0.0001))
        print(exp[2] + ' FNMR_1000 \t= ' + str(fnmr[index]))

        print('Ploting Curves...')

        # Plotting fmr and fnmr curves
        eer_plot.plot(thrs, fmr, linewidth=line_width,
                      label=exp[2] + ' (FMR)')
        eer_plot.plot(thrs, fnmr, linewidth=line_width,
                      label=exp[2] + ' (FNMR)')

        # Plotting DET Curves
        det_plot.plot(fmr, fnmr, label=exp[2], linewidth=line_width)

        # Plotting ROC Curves
        roc_plot.plot(fmr, 1 - fnmr, label=exp[2], linewidth=line_width)

    # Finalizing plots
    eer_plot.legend(loc='best', prop=font.FontProperties(size=legend_font))
    det_plot.legend(loc='best', prop=font.FontProperties(size=legend_font))
    roc_plot.legend(loc='best', prop=font.FontProperties(size=legend_font))

    # Showing plots or saving plots
    if args.save_plots:
        # Parsing dpi
        dpi = None if args.save_dpi is None else int(args.save_dpi)

        # saving plots
        ext = '.' + args.save_format
        eer_fig.savefig(join(args.save_path, 'EER' + ext), dpi=dpi)
        det_fig.savefig(join(args.save_path, 'DET' + ext), dpi=dpi)
        roc_fig.savefig(join(args.save_path, 'ROC' + ext), dpi=dpi)

        # closing plots
        plt.close()
    else:
        plt.show()
