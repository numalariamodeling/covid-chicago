import os
import argparse
import sys
sys.path.append('../')
from load_paths import load_box_paths
import shutil


def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-s",
        "--stem",
        type=str,
        help="Name of simulation experiment"
    )
    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default="Local"
    )
    parser.add_argument(
        "--zip_dir",
        action='store_true',
        help="If specified archives the simulation folder",
    )
    parser.add_argument(
        "--delete_from_dir",
        action='store_true',
        help="If specified deletes the simulation folder after zipping",
    )
    return parser.parse_args()

"""
make_archive function copied from Sean Behan
http://www.seanbehan.com/how-to-use-python-shutil-make_archive-to-zip-up-a-directory-recursively-including-the-root-folder/
"""
def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)

def zip_exp_files(wdir, sim_output_path, delete_from_dir):
    make_archive(sim_output_path, os.path.join(wdir,'simulation_output', f'{exp_name}_zip.zip'))
    shutil.rmtree(os.path.join(sim_output_path, 'simulations'), ignore_errors=True)
    if delete_from_dir:
        shutil.rmtree(os.path.join(sim_output_path), ignore_errors=True)

def cleanup(sim_output_path):
    """Delete single trajectories and simulation files"""
    shutil.rmtree(os.path.join(sim_output_path,'trajectories'), ignore_errors=True)
    shutil.rmtree(os.path.join(sim_output_path,'simulations'), ignore_errors=True)

if __name__ == '__main__':

    args = parse_args()
    stem = args.stem
    Location = args.Location
    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        print("Zipping files for " + exp_name)
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        cleanup(sim_output_path)
        if zip_dir:
            zip_exp_files(wdir, sim_output_path, delete_from_dir=args.delete_from_dir)