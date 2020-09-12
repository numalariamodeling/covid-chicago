

user_path =  Sys.getenv("USERNAME")

if(!exists('Location'))Location="LOCAL"

if(tolower(Location)=="nucluster"){
  user_path = '/projects/p30781/covidproject/'
  home_path = file.path(user_path, 'projects')
  data_path = file.path(user_path,  'data')
  git_dir = file.path(user_path, 'covid-chicago/')
  project_path = file.path(home_path, 'projects','covid_chicago')
  wdir = file.path(project_path, 'cms_sim')
  exe_dir = file.path(home_path, 'binaries', 'compartments') 
}


if(tolower(Location)=="local"){
  
  if('patri' %in%  user_path){
    data_path= file.path(user_path, 'Box Sync')
    project_path= file.path(user_path,'Box Sync','covid_chicago') #was origionally project_path
    wdir= file.path(user_path,'Box Sync','covid_chicago','cms_sim')
    exe_dir = file.path(user_path, 'Box Sync','compartments')
    git_dir = file.path(user_path, 'Documents','GitHub','covid-chicago')
  }
  
  
  if('tmh6260' %in%  user_path){
    data_path = file.path(user_path, 'Box Sync')
    home_path = file.path(user_path, 'Box', 'NU-malaria-team', 'projects') # had an error so I added this
    project_path = file.path(user_path, 'Box Sync', 'covid_chicago')  #
    wdir = file.path(user_path, 'Box Sync', 'covid_chicago', 'cms_sim')
    exe_dir = file.path(user_path, 'Box Sync', 'compartments')
    git_dir = file.path(user_path, 'Documents', 'GitHub', 'covid-chicago')
  }
  
  
  if('jlg1657' %in%  user_path){
    git_dir = file.path('C:/Users/jlg1657', 'Documents/covid-chicago/')
    # user_path = 'E:/'
    home_path = file.path(user_path, 'Box', 'NU-malaria-team','projects')
    data_path = file.path(user_path, 'Box', 'NU-malaria-team', 'data')
    project_path = file.path(home_path, 'covid_chicago')
    wdir = file.path(project_path, 'cms_sim')
    exe_dir = file.path(home_path, 'binaries', 'compartments')
  }
  
  
  if('mrung' %in% user_path){
    user_path = 'C:/Users/mrung'
    home_path = file.path(user_path, 'Box', 'NU-malaria-team','projects')
    data_path = file.path(user_path, 'Box', 'NU-malaria-team', 'data')
    git_dir = file.path(user_path, 'gitrepos', 'covid-chicago/')
    project_path = file.path(home_path, 'covid_chicago')
    wdir = file.path(project_path, 'cms_sim')
    exe_dir = file.path(home_path, 'binaries', 'compartments')
  }
  
  
  if('mrm9534' %in%  user_path){
    user_path = 'C:/Users/mrm9534'  #'/home/mrm9534/'
    home_path = file.path(user_path, 'Box', 'NU-malaria-team', 'projects')
    data_path = file.path(user_path, 'Box', 'NU-malaria-team', 'data')
    git_dir = file.path(user_path, 'gitrepos', 'covid-chicago/')
    project_path = file.path(home_path, 'covid_chicago')
    wdir = file.path(project_path, 'cms_sim')
    exe_dir = file.path(home_path, 'binaries', 'compartments')
  }
  
  
  if('Ibis' %in%  user_path){
    #user_path = r'\~/'
    git_dir = file.path(user_path, 'Documents', 'GitHub', 'covid-chicago')
    home_path = file.path(user_path, 'Box')
    data_path = file.path(user_path, 'Box')
    project_path = file.path(home_path, 'covid_chicago')
    wdir = file.path(project_path, 'cms_sim')
    exe_dir = file.path(home_path, 'binaries', 'compartments')
  }
}



simulation_output <- file.path(wdir, "simulation_output")

