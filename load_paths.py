import os


def load_box_paths(user_path=None):
    data_path = os.getenv("DATA_PATH")
    project_path = os.getenv("PROJECT_PATH")
    wdir = os.getenv("WDIR")
    exe_dir = os.getenv("EXE_DIR")
    git_dir = os.getenv("GIT_DIR")

    if not user_path :
        user_path = os.path.expanduser('~')

    if 'garrett' in user_path:
        #user_path= 'C:/Users/geickelb1'
        ## idk where to put datapath since i don't have access to NU-malaria-team
        data_path= os.path.join(user_path, 'Box',  'data')
        project_path= os.path.join(user_path,'Box','covid_chicago') #was origionally project_path
        wdir= os.path.join(user_path,'Box','covid_chicago','cms_sim')
        exe_dir = os.path.join(user_path, 'Box','compartments')
        git_dir = os.path.join(user_path, 'Documents','GitHub','covid-chicago')
    elif 'jlg1657' in user_path or 'mrung' in user_path or 'geickelb1' in user_path:

        if 'jlg1657' in user_path :
            git_dir = os.path.join('C:/Users/jlg1657', 'Documents/covid-chicago/')
            user_path = 'E:/'
            home_path = os.path.join(user_path, 'Box', 'NU-malaria-team','projects')
            data_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'data')
        if 'mrung' in user_path :
            user_path = 'C:/Users/mrung'
            home_path = os.path.join(user_path, 'Box', 'NU-malaria-team','projects')
            data_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'data')
            git_dir = os.path.join(user_path, 'gitrepos', 'covid-chicago/')
        if 'geickelb1' in user_path :
            #user_path = 'C:/Users/geickelb1'
            home_path =os.path.join(user_path,'Box')
            #data_path = os.path.join(user_path, 'Box',  'data')
            git_dir = os.path.join(user_path, 'Documents', 'Github', 'covid-chicago')

        project_path = os.path.join(home_path, 'covid_chicago')
        wdir = os.path.join(project_path, 'cms_sim')
        exe_dir = os.path.join(home_path, 'binaries', 'compartments')

    return data_path, project_path, wdir , exe_dir, git_dir

