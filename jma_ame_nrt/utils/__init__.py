#
#  2021/08/13 Yamashita
#
import os
import argparse
from .cutil import ColUtils
from .cbar import val2col, collevs

__all__ = ["ColUtils", "val2col", "collevs"]

# デフォルトの出力ディレクトリ
output_dir_default = "map"


def os_mkdir(dir_name):
    """ディレクトリを作成する

    Parameters:
    ----------
    dir_name: str
        作成するディレクトリ名
    ----------
    """
    if not os.path.isdir(dir_name):
        if os.path.isfile(dir_name):
            os.remove(dir_name)
        print("mkdir " + dir_name)
        os.mkdir(dir_name)


def _construct_parser(opt_cum=False,
                      opt_lab=False,
                      opt_wind=False,
                      opt_temp=False,
                      opt_trange=False):
    """オプションの読み込み"""
    parser = argparse.ArgumentParser(description='Matplotlib cartopy, ')

    parser.add_argument('--time_sta',
                        type=str,
                        help=('start time; yyyymmddhhMMss, or ISO date'),
                        metavar='<timesta>')
    parser.add_argument('--time_end',
                        type=str,
                        help=('end time; yyyymmddhhMMss, or ISO date'),
                        metavar='<timeend>')
    parser.add_argument('--sta',
                        type=str,
                        help=('Station name; e.g. Tokyo'),
                        metavar='<sta>')
    if opt_cum:
        parser.add_argument('--cumrain',
                            type=str,
                            help=('Option of cumulative rain'),
                            metavar='<False/True>')
    if opt_lab:
        parser.add_argument('--mlabel',
                            type=str,
                            help=('Option to add marker label'),
                            metavar='<False/True>')
    if opt_wind:
        parser.add_argument('--addwind',
                            type=str,
                            help=('Option to add barbs'),
                            metavar='<True/False>')
    if opt_temp:
        parser.add_argument('--addtemp',
                            type=str,
                            help=('Option to add temperature'),
                            metavar='<True/False>')
    if opt_trange:
        parser.add_argument('--temprange',
                            type=str,
                            help=('temperature range of colorbar label, '
                                  'tmin: minimum, tmax: maximum, '
                                  'step: tick interval (optional)'),
                            metavar='<min,max,step>')

    parser.add_argument('--output_dir',
                        type=str,
                        help=('Directory of output files'),
                        metavar='<output_dir>')

    return parser


def _str2bool(s):
    """文字列からboolへの変換"""
    return s.lower() in ["true", "t", "yes", "1"]


def parse_command(args,
                  opt_cum=False,
                  opt_lab=False,
                  opt_wind=False,
                  opt_temp=False,
                  opt_trange=False):
    """オプションの読み込み"""
    parser = _construct_parser(opt_cum=opt_cum,
                               opt_lab=opt_lab,
                               opt_wind=opt_wind,
                               opt_temp=opt_temp,
                               opt_trange=opt_trange)
    parsed_args = parser.parse_args(args[1:])
    if parsed_args.output_dir is None:
        parsed_args.output_dir = output_dir_default
    if parsed_args.time_sta is None:
        raise ValueError("time_sta is needed")
    if parsed_args.time_end is None:
        raise ValueError("time_end is needed")
    if parsed_args.sta is None:
        raise ValueError("sta is needed")
    if opt_cum:
        if parsed_args.cumrain is None:
            parsed_args.cumrain = False
        else:
            parsed_args.cumrain = _str2bool(parsed_args.cumrain)
    if opt_lab:
        if parsed_args.mlabel is None:
            parsed_args.mlabel = False
        else:
            parsed_args.mlabel = _str2bool(parsed_args.mlabel)
    if opt_wind:
        if parsed_args.addwind is None:
            parsed_args.addwind = True
        else:
            parsed_args.addwind = _str2bool(parsed_args.addwind)
    if opt_temp:
        if parsed_args.addtemp is None:
            parsed_args.addtemp = True
        else:
            parsed_args.addtemp = _str2bool(parsed_args.addtemp)
    if opt_trange:
        if parsed_args.temprange is None:
            parsed_args.temprange = "18.,38.,2."
    return parsed_args
