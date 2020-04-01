import os


def load_box_paths(user_path=None):

    if not user_path :
        user_path = os.path.expanduser('~')
<<<<<<< HEAD
        if 'garrett' in user_path:
            #user_path= 'C:/Users/geickelb1'
            ## idk where to put datapath since i don't have access to NU-malaria-team
            data_path= os.path.join(user_path, 'Box',  'data')
            project_path= os.path.join(user_path,'Box/covid_chicago/cms_sim/') #was origionally project_path
            wdir= os.path.join(user_path,'Box/covid_chicago/cms_sim/')
            exe_dir = os.path.join(user_path, 'Box','compartments')
            git_dir = os.path.join(user_path, 'iCloudDrive','Documents','GitHub','covid-chicago')
        
        else:
        
            if 'jlg1657' in user_path :
                user_path = 'E:/'
                home_path = os.path.join(user_path, 'Box', 'NU-malaria-team','projects')
                data_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'data')
                #git_dir = os.path.join(user_path, 'Documents/covid-chicago/')
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
=======
        if 'jlg1657' in user_path :
            user_path = 'E:/'
            home_path = os.path.join(user_path, 'Box', 'NU-malaria-team','projects')
            data_path = os.path.join(user_path, 'Box', 'NU-malaria-team', 'data')
            #git_dir = os.path.join(user_path, 'Documents/covid-chicago/')
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
>>>>>>> parent of eed2ff3... update extended model postprocessing to include age groups (#9)

            project_path = os.path.join(home_path, 'covid_chicago')
            wdir = os.path.join(project_path, 'cms_sim')
            exe_dir = os.path.join(home_path, 'binaries', 'compartments')
        

    return data_path, project_path, wdir , exe_dir, git_dir

