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


def _construct_parser(opt_cum=False, opt_lab=False, opt_wind=False):
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
                            type=bool,
                            help=('Option of cumulative rain (False/True)'),
                            metavar='<cumrain>')
    if opt_lab:
        parser.add_argument('--mlabel',
                            type=bool,
                            help=('Option of marker label (False/True)'),
                            metavar='<markerlabel>')
    if opt_wind:
        parser.add_argument('--wind',
                            type=bool,
                            help=('Option of barbs (True/False)'),
                            metavar='<wind>')

    parser.add_argument('--output_dir',
                        type=str,
                        help=('Directory of output files'),
                        metavar='<output_dir>')

    return parser


def parse_command(args, opt_cum=False, opt_lab=False, opt_wind=False):
    """オプションの読み込み"""
    parser = _construct_parser(opt_cum=opt_cum,
                               opt_lab=opt_lab,
                               opt_wind=opt_wind)
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
    if opt_lab:
        if parsed_args.mlabel is None:
            parsed_args.mlabel = False
    if opt_wind:
        if parsed_args.wind is None:
            parsed_args.wind = True
    return parsed_args
