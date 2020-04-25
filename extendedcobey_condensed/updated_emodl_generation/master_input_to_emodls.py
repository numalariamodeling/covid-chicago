import pandas as pd

def gen_emodls(emodl_base='emodl_', master_input_base='master_input_4grps', template_emodl_base='extendedmodel_cobey_age_4grp', \
               duration=365, nruns=3, monitoring_samples=365, prefix='trajectories_', \
               template_cfg_base='extendedmodel_cobey_age_4grp'):
    
    #Function takes master csv file (output of gen_combos from
    #combine_to_master_input_csv.py) and creates an emodl file
    #and corresponding cfg file for each line for each line.
    #Everything that goes in the emodl is contained within the
    #master csv file, whereas everything that goes in the cfg
    #file is determined at call (duration, nruns, nsamples,
    #etc...). Prefix emodl_base will also be used as the prefix
    #for the output cfg files.
    
    #Read in master input csv to DataFrame...
    master_df = pd.read_csv(master_input_base + '.csv', index_col=0)
    columns = list(master_df.columns)         
    
    #Read in template emodl and cfg as strings...
    template_emodl = open(template_emodl_base + '.emodl', 'r') 
    template_e_txt = template_emodl.read() #Read in template emodl as string
    template_emodl.close()
    
    template_cfg = open(template_cfg_base + '.cfg', 'r') 
    template_c_txt = template_cfg.read() #Read in template emodl as string
    template_cfg.close()
    
    
    #Create an emodl file and cfg file with specified base for each row...
    for index, row in master_df.iterrows():
        template_e = template_e_txt #Writing to output emodl
        for col in columns:
            if ('@' + col + '@') in template_e:
                template_e = template_e.replace('@' + col + '@', str(row[col]))
        output_emodl = open(emodl_base + str(index) + '.emodl', 'w')
        output_emodl.write(template_e)
        output_emodl.close()
        
        template_c = template_c_txt #Writing to output cfg
        template_c = template_c.replace('@duration@', str(duration))
        template_c = template_c.replace('@nruns@', str(nruns))
        template_c = template_c.replace('@monitoring_samples@', str(duration))
        template_c = template_c.replace('@prefix@', prefix + str(index))
        output_cfg = open(emodl_base + str(index) + '.cfg', 'w')
        output_cfg.write(template_c)
        output_cfg.close()