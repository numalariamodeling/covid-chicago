import os


def load_box_paths(user_path=None):

    if not user_path :
        user_path = os.path.expanduser('~')
        if 'jlg1657' in user_path :
            if 'C:' in user_path :
                git_dir = os.path.join(user_path, 'Documents/covid-chicago/')
                user_path = 'E:/'
            else :
                git_dir = os.path.join(user_path, 'Documents/work/covid-chicago/')
            home_path = os.path.join(user_path, 'Box', 'NU-malaria-team','projects')
            data_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'data')
        if 'mrung' in user_path :
            user_path = 'C:/Users/mrung'
            home_path = os.path.join(user_path, 'Box', 'NU-malaria-team','projects')
            data_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'data')
            git_dir = os.path.join(user_path, 'gitrepos', 'covid-chicago/')
        if 'geickelb1' in user_path :
            user_path = 'C:/Users/mrung'
            home_path =os.path.join(user_path,'Box')
            #data_path = os.path.join(user_path, 'Box',  'data')
            git_dir = os.path.join(user_path, 'Documents', 'Github', 'covid-chicago')

    project_path = os.path.join(home_path, 'covid_chicago')
    wdir = os.path.join(project_path, 'cms_sim')
    exe_dir = os.path.join(home_path, 'binaries', 'compartments')

    return data_path, project_path, wdir , exe_dir, git_dir

