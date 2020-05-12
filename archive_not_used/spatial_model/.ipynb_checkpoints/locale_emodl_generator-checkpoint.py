import os
import subprocess

### FUNCTIONS
def SIER_init(county_dic, county):
    """
    chemical species starting values; aka initial SEIR numbers
    """
    S= "(species S::{} {})".format(county, county_dic[county][0])
    E= "(species E::{} {})".format(county, county_dic[county][1])
    I= "(species I::{} {})".format(county, county_dic[county][2])
    R= "(species R::{} {})".format(county, county_dic[county][3])
    
    return(S,E,I,R)



def SIER_output(county):
    "chemical species that are possible (what i want reporeted in output file)"
    S= "(observe susceptible_{} S::{})".format(county, county)
    E= "(observe exposed_{} E::{})".format(county, county)
    I= "(observe infectious_{} I::{})".format(county, county)
    R= "(observe recovered_{} R::{})".format(county, county)
    
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
(reaction exposure_{}   (S::{}) (E::{}) (* Ki S::{} I::{}))
(reaction infection_{}  (E::{})   (I::{})   (* Kl E::{}))
(reaction recovery_{}   (I::{})   (R::{})   (* Kr I::{}))
;(reaction waning_{}     (R::{})   (S::{})   (* Kw R::{}))""".format(county, county, county,
                                                                county, county, county,
                                                                county, county, county,
                                                                county, county, county,
                                                                county, county, county,                                           
                                                                county,county)
    return(reaction_str)

###

###stringing all of my functions together to make the file:

def generate_locale_emodl(county_dic, param_dic,file_output, verbose=False):
    model_name= "seir.emodl" ### can make this more flexible
    header_str="; simplemodel \n\n"+ "(import (rnrs) (emodl cmslib)) \n\n"+'(start-model "{}") \n\n'.format(model_name)
    footer_str ="(end-model)"
    
    #building up the .emodl string
    total_string=""
    sum_string= ""
    total_string= total_string + header_str

    for key in county_dic.keys():
        total_string= total_string+ "(locale site-{})\n".format(key)
        total_string= total_string+ "(set-locale site-{})\n".format(key)
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
    if verbose==True:
        print(total_string)
    emodl = open(file_output, "w") ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()

    
def generate_locale_cfg(cfg_filename,nruns, filepath):
    
    # generate the CFG file
    cfg="""{
        "duration" : 60,
        "runs" : %s,
        "samples" : 60,
        "solver" : "R",
        "output" : {
             "prefix": "%s",
             "headers" : true
        },
        "tau-leaping" : {
            "epsilon" : 0.01
        },
        "r-leaping" : {}
    }""" % (nruns, cfg_filename)

    file1 = open(filepath,"w") 
    file1.write(cfg)
    file1.close()
    
    

if __name__ == '__main__':
    generate_locale_emodl()
#print("{} file created".format(file_output))