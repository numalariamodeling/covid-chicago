import os
import subprocess

### directories
user_path = os.path.expanduser('~')

if "mrung" in user_path : 
    exe_dir = os.path.join(user_path, 'Box/NU-malaria-team/projects/binaries/compartments/')
    git_dir = os.path.join(user_path, 'gitrepos/covid-chicago/')
elif 'geickelb1' in user_path:
    exe_dir = os.path.join(user_path,'Desktop/compartments/')
    git_dir = os.path.join(user_path, 'Documents/Github/covid-chicago/')
###  
    
### initializing some default parameters and n for counties: 

##older hardcoding:
# county_dic={'illinois':[12671890, 0, 12, 0],
#             'cook':[5211000, 0, 1, 0]
#            } #cook county #s just roughly estimatd

##making the county dict, assuming each county is [pop, 0, 1, 0]
import csv
county_dic={}

###running with only first 10 counties (county_dic2):
with open('county_dic.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    i=0
    for row in reader:
        if i<5:
            county_dic[row['county']]= [int(x) for x in row['val_list'].strip('][').split(', ')] 
            i+=1
        else:
            pass


param_dic={'ki':4.45e-6,
           'incubation_pd':6.63,
           'recovery_rate':16,
           'waning':180}
###

### desired file name:
file_output='GE_county_model3.emodl'
###

### FUNCTIONS
def SIER_init(county_dic, county):
    """
    chemical species starting values; aka initial SEIR numbers
    """
    S= "(species S_{} {})".format(county, county_dic[county][0])
    E= "(species E_{} {})".format(county, county_dic[county][1])
    I= "(species I_{} {})".format(county, county_dic[county][2])
    R= "(species R_{} {})".format(county, county_dic[county][3])
    
    return(S,E,I,R)

def SIER_output(county):
    "chemical species that are possible (what i want reporeted in output file)"
    S= "(observe susceptible_{} S_{})".format(county, county)
    E= "(observe exposed_{} E_{})".format(county, county)
    I= "(observe infectious_{} I_{})".format(county, county)
    R= "(observe recovered_{} R_{})".format(county, county)
    
    return(S,E,I,R)

def params(param_dic):
    ki=param_dic['ki']
    params_string = """
(param Ki {})
(param incubation_pd {})
(param Kl (/ 1 incubation_pd))
(param recovery_rate {})
(param Kr (/ 1 recovery_rate))
(param waning {})
(param Kw (/ 1 waning))
    """.format(param_dic['ki'],
               param_dic['incubation_pd'],
               param_dic['recovery_rate'],
               param_dic['waning']
              )

    return(params_string)

def reactions(county):
    county= str(county)
    
    reaction_str="""
(reaction exposure_{}   (S_{}) (E_{}) (* Ki S_{} I_{}))
(reaction infection_{}  (E_{})   (I_{})   (* Kl E_{}))
(reaction recovery_{}   (I_{})   (R_{})   (* Kr I_{}))
;(reaction waning_{}     (R_{})   (S_{})   (* Kw R_{}))""".format(county, county, county,
                                                                county, county, county,
                                                                county, county, county,
                                                                county, county, county,
                                                                county, county, county,                                           
                                                                county,county)
    return(reaction_str)
###

###stringing all of my functions together to make the file:

def main():
    model_name= "seir.emodl" ### can make this more flexible
    header_str="; simplemodel \n\n"+ "(import (rnrs) (emodl cmslib)) \n\n"+'(start-model "{}") \n\n'.format(model_name)
    footer_str ="(end-model)"
    
    #building up the .emodl string
    total_string=""
    sum_string= ""
    total_string= total_string + header_str

    for key in county_dic.keys():
        S,E,I,R =SIER_init(county_dic, key)
        total_string= total_string+ S + '\n' + E + '\n' + I + '\n' + R + '\n'
        
    total_string= total_string+'\n' #adding a linebreak
    
    for key in county_dic.keys():
        S,E,I,R =SIER_output(key)
        total_string= total_string+ S + '\n' + E + '\n' + I + '\n' + R + '\n'
        sum_string=sum_string+" S_{}".format(key)

    sum_string=";(observe susceptible (sum {}))\n".format(sum_string)
    total_string= total_string+sum_string
         
    param= params(param_dic)
    total_string= total_string+ param

    for key in county_dic.keys(): 
        reaction= reactions(key)
        total_string= total_string+ reaction
    total_string=total_string + '\n\n' + footer_str

    ### write the file:
    print(total_string)
    emodl = open(file_output, "w") ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()


if __name__ == '__main__':
    main()
print("{} file created".format(file_output))