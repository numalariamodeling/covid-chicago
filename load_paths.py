import os

def load_box_paths(user_path=None, Location='Local'):
    if Location == 'NUCLUSTER':
        user_path = os.getcwd()[:16]  #'/projects/p30781/'
        home_path = os.path.join(user_path, 'covidproject', 'projects')
        data_path = os.path.join(user_path, 'covidproject', 'data')
        git_dir = os.path.join(user_path, 'covidproject', 'covid-chicago')
        project_path = os.path.join(home_path, 'covid_chicago')
        wdir = os.path.join(project_path, 'cms_sim')
        exe_dir = os.path.join(user_path,'covidproject', 'binaries', 'compartments')

    else:
        if not user_path:
            user_path = os.path.expanduser('~')

        if 'tmh6260' in user_path:
            data_path = os.path.join(user_path, 'Box Sync')
            home_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'projects')  # had an error so I added this
            project_path = os.path.join(user_path, 'Box Sync', 'covid_chicago')  #
            wdir = os.path.join(user_path, 'Box Sync', 'covid_chicago', 'cms_sim')
            exe_dir = os.path.join(user_path, 'Box Sync', 'compartments')
            git_dir = os.path.join(user_path, 'Documents', 'GitHub', 'covid-chicago')

        elif 'jlg1657' in user_path:
            git_dir = os.path.join('C:/Users/jlg1657', 'Documents/covid-chicago/')
            # user_path = 'E:/'
            home_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'projects')
            data_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'data')
            project_path = os.path.join(home_path, 'covid_chicago')
            wdir = os.path.join(project_path, 'cms_sim')
            exe_dir = os.path.join(home_path, 'binaries', 'compartments')

        elif 'mrung' in user_path or 'mrm9534' in user_path:
            user_path = user_path
            home_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'projects')
            data_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'data')
            git_dir = os.path.join(user_path, 'gitrepos', 'covid-chicago/')
            project_path = os.path.join(home_path, 'covid_chicago')
            wdir = os.path.join(project_path, 'cms_sim')
            exe_dir = os.path.join(home_path, 'binaries', 'compartments')

        elif 'Ibis' in user_path:
            # user_path = r'\~/'
            git_dir = os.path.join(user_path, 'Documents', 'GitHub', 'covid-chicago')
            home_path = os.path.join(user_path, 'Box')
            data_path = os.path.join(user_path, 'Box')
            project_path = os.path.join(home_path, 'covid_chicago')
            wdir = os.path.join(project_path, 'cms_sim')
            exe_dir = os.path.join(home_path, 'binaries', 'compartments')

        elif 'HP1' in user_path:
            # user_path = r'\~/'
            git_dir = os.path.join(user_path, 'Documents', 'covid-chicago')
            home_path = os.path.join(user_path, 'Box')
            data_path = os.path.join(user_path, 'Box')
            project_path = os.path.join(home_path, 'covid_chicago')
            wdir = os.path.join(project_path, 'cms_sim')
            exe_dir = os.path.join(home_path, 'binaries', 'compartments')

        elif 'aec7248' in user_path:
            user_path = user_path
            home_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'projects')
            data_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'data')
            git_dir = os.path.join(user_path, 'Documents', 'covid-chicago/')
            project_path = os.path.join(home_path, 'covid_chicago')
            wdir = os.path.join(project_path, 'cms_sim')
            exe_dir = os.path.join(home_path, 'binaries', 'compartments')

        else:
            from dotenv import load_dotenv
            load_dotenv()
            home_path = os.getenv("HOME_PATH")
            data_path = os.getenv("DATA_PATH")
            project_path = os.getenv("PROJECT_PATH")
            wdir = os.getenv("WDIR")
            exe_dir = os.getenv("EXE_DIR")
            git_dir = os.getenv("GIT_DIR")

    return data_path, project_path, wdir, exe_dir, git_dir

