print('Importing packages...')
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
import numpy as np
import matplotlib.dates as mdates
import datetime
#sns.set(color_codes=True)
import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42
import statistics as st
sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
from statsmodels.distributions.empirical_distribution import ECDF
import scipy
import gc

column_list = ['scen_num', 'reopening_multiplier_4']
for ems_region in range(1,12):
    column_list.append('hospitalized_det_EMS-' + str(ems_region))
    column_list.append('hosp_det_cumul_EMS-' + str(ems_region))
    column_list.append('detected_cumul_EMS-' + str(ems_region))

#Specify paths to trajectories. For this run, all trajectories were temporarily stored in the same folder.

print('Reading trajectories...')
sub1 = pd.read_csv('trajectoriesDat_1.csv', usecols=column_list) #0.08 - 0.09
print('Trajectory 1 read.')
sub2 = pd.read_csv('trajectoriesDat_2.csv', usecols=column_list) #0.10 - 0.115
print('Trajectory 2 read.')
sub3 = pd.read_csv('trajectoriesDat_3.csv', usecols=column_list) #0.087 - 0.10
print('Trajectory 3 read.')
sub4 = pd.read_csv('trajectoriesDat_08.csv', usecols=column_list) # 0.08 - 0.10
sub4['scen_num'] = sub4['scen_num'].values + 1000
print('Trajectory 4 read.')
sub5 = pd.read_csv('trajectoriesDat_300.csv', usecols=column_list) #0.1 - 0.11
sub5['scen_num'] = sub5['scen_num'].values + 2000
print('Trajectory 5 read.')
sub6 = pd.read_csv('trajectoriesDat_600.csv', usecols=column_list) #0.115 - 0.13
sub6['scen_num'] = sub6['scen_num'].values + 2000
print('Trajectory 6 read.')
sub7 = pd.read_csv('trajectoriesDat_1000.csv', usecols=column_list) #0.13 - 0.15
sub7['scen_num'] = sub7['scen_num'].values + 2000
print('Trajectory 7 read.')
sub8 = pd.read_csv('trajectoriesDat_15.csv', usecols=column_list) #0.13 - 0.15
sub8['scen_num'] = sub8['scen_num'].values + 3000
print('Trajectory 8 read.')

###loop here
for region in ['NE', 'NC', 'CE', 'SO']:
    for capacity in ['high', 'low']:
        for metric in ['det', 'hosp']: #current implementation only allows tracking new_detected and new_hosp.
            boink = []

            ### Region

            #hospital_capacity = 1907
            #NE 4919 8609 12299
            #NC 1089 1907 2724
            #CE 856 1498 2140
            #SO 640 1121 1601

            ### Metric to assess:
            if metric == 'det':
                notif = 'new_det_' + region
            if metric == 'hosp':
                notif = 'new_hosp_det_' + region

            ### Simulation Dates to Examine
            lower_limit = 145
            upper_limit = 225
            grain = 1

            prob_over_array = []
            range_1 = np.arange(0, 25, 0.01)

            ### Capacity
            ### Which trajectories to use for each capacity were determined by hand.
            if region == 'NE':
                if capacity == 'low':
                    hospital_capacity = 4919
                    trajectories = pd.concat([sub1, sub3, sub4]).reset_index()
                elif capacity == 'high':
                    hospital_capacity = 8609
                    trajectories = pd.concat([sub1, sub2, sub3]).reset_index()
            elif region == 'NC':
                if capacity == 'low':
                    hospital_capacity = 1089
                    trajectories = pd.concat([sub4, sub5, sub6, sub7]).reset_index()
                elif capacity == 'high':
                    hospital_capacity = 1907
                    trajectories = pd.concat([sub5, sub6, sub7]).reset_index()
            elif region == 'CE':
                if capacity == 'low':
                    hospital_capacity = 856
                    trajectories = pd.concat([sub5, sub6, sub7]).reset_index()
                elif capacity == 'high':
                    hospital_capacity = 1498
                    trajectories = sub8 #pd.concat([sub5, sub6, sub7, sub8]).reset_index() ##need new
            elif region == 'SO':
                if capacity == 'low':
                    hospital_capacity = 640
                    trajectories = pd.concat([sub1, sub2, sub3]).reset_index()
                elif capacity == 'high':
                    hospital_capacity = 1121
                    trajectories = pd.concat([sub5, sub6, sub7]).reset_index()

            #NE Region

            trajectories['hospitalized_det_NE'] = trajectories['hospitalized_det_EMS-11'] + \
            trajectories['hospitalized_det_EMS-10'] + \
            trajectories['hospitalized_det_EMS-9'] + \
            trajectories['hospitalized_det_EMS-8'] + \
            trajectories['hospitalized_det_EMS-7']

            trajectories['hosp_det_cumul_NE'] = trajectories['hosp_det_cumul_EMS-11'] + \
            trajectories['hosp_det_cumul_EMS-10'] + \
            trajectories['hosp_det_cumul_EMS-9'] + \
            trajectories['hosp_det_cumul_EMS-8'] + \
            trajectories['hosp_det_cumul_EMS-7']

            trajectories['detected_cumul_NE'] = trajectories['detected_cumul_EMS-11'] + \
            trajectories['detected_cumul_EMS-10'] + \
            trajectories['detected_cumul_EMS-9'] + \
            trajectories['detected_cumul_EMS-8'] + \
            trajectories['detected_cumul_EMS-7']

            #NC Region

            trajectories['hospitalized_det_NC'] = trajectories['hospitalized_det_EMS-1'] + trajectories['hospitalized_det_EMS-2'] 
            trajectories['hosp_det_cumul_NC'] = trajectories['hosp_det_cumul_EMS-1'] + trajectories['hosp_det_cumul_EMS-2'] 
            trajectories['detected_cumul_NC'] = trajectories['detected_cumul_EMS-1'] + trajectories['detected_cumul_EMS-2']

            #CE Region

            trajectories['hospitalized_det_CE'] = trajectories['hospitalized_det_EMS-3'] + trajectories['hospitalized_det_EMS-6'] 
            trajectories['hosp_det_cumul_CE'] = trajectories['hosp_det_cumul_EMS-3'] + trajectories['hosp_det_cumul_EMS-6'] 
            trajectories['detected_cumul_CE'] = trajectories['detected_cumul_EMS-3'] + trajectories['detected_cumul_EMS-6']

            #SO Region

            trajectories['hospitalized_det_SO'] = trajectories['hospitalized_det_EMS-4'] + trajectories['hospitalized_det_EMS-5'] 
            trajectories['hosp_det_cumul_SO'] = trajectories['hosp_det_cumul_EMS-4'] + trajectories['hosp_det_cumul_EMS-5'] 
            trajectories['detected_cumul_SO'] = trajectories['detected_cumul_EMS-4'] + trajectories['detected_cumul_EMS-5']

            print('Region: ' + region)
            print('Capacity: ' + str(capacity))
            print('Metric: ' + str(notif))
            thresh = []
            p_array = []
            dates_array = []
            over_array = []
            no_array = []
            days_array = np.arange(lower_limit,upper_limit, grain)
            for notif_period in days_array:
                trajectories_new = trajectories
                unique_scen = np.array(list(set(trajectories_new['scen_num'].values)))
                overflow_date = []
                max_date = []
                #notif = 'new_detected'
                overflow_traj = []
                traj = []
                non_overflow_traj = []
                overflow_scens = []
                non_overflow_scens = []
                non_overflow_crit_day = []
                overflow_crit_day = []
                overflow_week = []
                overflow_prior_week = []
                non_overflow_week = []
                non_overflow_prior_week = []
                crit_day = []
                week = []
                week_prior = []
                crit = notif_period
                for scen in unique_scen:
                    new = trajectories_new[(trajectories_new['scen_num'] == scen)].reset_index()
                    new['new_hosp_det_NE'] = np.append(np.array([0.0]), np.diff(new['hosp_det_cumul_NE'].values))
                    new['new_det_NE'] = np.append(np.array([0.0]), np.diff(new['detected_cumul_NE'].values))
                    new['new_hosp_det_NC'] = np.append(np.array([0.0]), np.diff(new['hosp_det_cumul_NC'].values))
                    new['new_det_NC'] = np.append(np.array([0.0]), np.diff(new['detected_cumul_NC'].values))
                    new['new_hosp_det_CE'] = np.append(np.array([0.0]), np.diff(new['hosp_det_cumul_CE'].values))
                    new['new_det_CE'] = np.append(np.array([0.0]), np.diff(new['detected_cumul_CE'].values))
                    new['new_hosp_det_SO'] = np.append(np.array([0.0]), np.diff(new['hosp_det_cumul_SO'].values))
                    new['new_det_SO'] = np.append(np.array([0.0]), np.diff(new['detected_cumul_SO'].values))
                    hosp = new['hospitalized_det_' + region].values #new['hospitalized_det'].values
                    i = 0
                    traj.append(hosp)
                    while (hosp[i] < hospital_capacity) & (i < len(hosp)-1):
                        i += 1
                    crit_day.append(i)
                    if i == len(hosp) - 1:
                        non_overflow_traj.append(hosp)
                        non_overflow_scens.append(scen)

                        #crit_day.append(i)
                        non_overflow_week.append(np.mean(new[notif].values[crit-7:crit]))
                        non_overflow_prior_week.append(np.mean(new[notif].values[crit-14:crit-7]))
                    else:
                        overflow_traj.append(hosp)
                        overflow_scens.append(scen)

                        #crit_day.append(i)
                        overflow_week.append(np.mean(new[notif].values[crit-7:crit]))
                        overflow_prior_week.append(np.mean(new[notif].values[crit-14:crit-7]))
                overflow_week = np.array(overflow_week)
                overflow_prior_week = np.array(overflow_prior_week)
                non_overflow_week = np.array(non_overflow_week)
                non_overflow_prior_week = np.array(non_overflow_prior_week)     
                overflow_date = np.array(overflow_date)
                max_date = np.array(max_date)
                week = np.array(week)
                crit_day = np.array(crit_day)
                week_prior = np.array(week_prior)
                boink.append(np.mean(week/week_prior))
                over = overflow_week/overflow_prior_week
                no = non_overflow_week/non_overflow_prior_week
                #ecdf_over = ECDF(over)
                #ecdf_no = ECDF(no)
                #prob_over = np.cumsum(ecdf_no(range_1)-ecdf_over(range_1))/np.sum(ecdf_no(range_1)-ecdf_over(range_1))
                #print('Mean Over: ' + str(np.mean(over)))
                #print('Mean No: ' + str(np.mean(no)))
                if np.mean(over) > np.mean(no):
                    p_over = scipy.stats.norm.pdf(range_1, np.mean(over), np.std(np.append(over,no, axis=0)))
                    p_no = scipy.stats.norm.pdf(range_1, np.mean(no), np.std(np.append(over,no, axis=0)))
                    prob_over = p_over/(p_over+p_no)
                    prob_over_array.append(prob_over)
                    over_array.append(np.median(over))
                    no_array.append(np.median(no))
                    #thresh.append((np.median(over) + np.median(no))/2)
                    stat, p = scipy.stats.ttest_ind(over,no)
                    p_array.append(p)
                    dates_array.append(dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(crit)))
                    print(crit)
            over_array = np.array(over_array)
            no_array = np.array(no_array)
            print('done')

            #trace fig
            full_dates_array = []
            for ni in np.arange(0,370,1):
                full_dates_array.append(dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(ni)))
            plt.figure(figsize=(10,6))
            for traject in overflow_traj:
                if (len(traject) == len(full_dates_array)):
                    plt.plot(full_dates_array, traject, color='r', alpha=0.1)
            for traject in non_overflow_traj:
                if (len(traject) == len(full_dates_array)):
                    plt.plot(full_dates_array, traject, color='b', alpha=0.1)
            #plt.yscale('log')
            plt.hlines(hospital_capacity, xmin=dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(0)), xmax=dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(ni)))
            plt.xlim([dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(0)), dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(ni))])
            #plt.vlines(np.median(crit_day[crit_day != 369]),ymin=1,ymax=30000, linestyle='dashed', alpha=0.4)
            plt.ylabel(region + ' Hospitalized', fontsize=14)
            formatter = mdates.DateFormatter("%m-%y")
            ax = plt.gca()
            ax.xaxis.set_major_formatter(formatter)
            #ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            #plt.xlabel('Simulation Day', fontsize=14)
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            #plt.savefig('sims_2.png', dpi=200)
            #plt.savefig('sims_2.pdf')
            print('Proportion of sims that do not exceed: ' + str(np.sum(crit_day == 369)/(len(trajectories)/370)))
            print('Number of trajectories: ' + str(len(trajectories)/370))


            #p-value fig
            plt.figure(figsize=(10,6))
            plt.plot(dates_array, p_array)
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            ax = plt.gca()
            formatter = mdates.DateFormatter("%m-%d")
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            #ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.yscale('log')
            plt.ylabel('Significance of Difference Between\nOverflow Scenarios and Non-Overflow Scenarios\n(p-value of t-test)', fontsize=14)
            plt.savefig('p_val_' + str(notif) + '_' + region + str(hospital_capacity) + '_1.png', dpi=200)
            plt.savefig('p_val_' + str(notif) + '_' + region + str(hospital_capacity) + '_1.pdf')
            pd.DataFrame({'date':dates_array, 'p_val':p_array}).to_csv('p_val_' + str(notif) + '_' + region + str(hospital_capacity) + '_1.csv')


            #Threshold fig
            thresh_0 = .05
            thresh_1 = .20
            thresh_2 = .50
            thresh_3 = .80
            thresh_4 = .95
            thresh_0_array = []
            thresh_1_array = []
            thresh_2_array = []
            thresh_3_array = []
            thresh_4_array = []
            count = 0
            for prob_array in prob_over_array:
                i = 0
                while prob_array[i] < thresh_0:
                    i += 1
                thresh_0_array.append(i)
                i = 0
                while prob_array[i] < thresh_1:
                    i += 1
                thresh_1_array.append(i)
                i = 0
                while prob_array[i] < thresh_2:
                    i += 1
                thresh_2_array.append(i)
                i = 0
                while prob_array[i] < thresh_3:
                    i += 1
                thresh_3_array.append(i)
                i = 0
                while prob_array[i] < thresh_4:
                    i += 1
                thresh_4_array.append(i)
                count += 1
                print(count)
            thresh_0_array = np.array(thresh_0_array)
            thresh_1_array = np.array(thresh_1_array)
            thresh_2_array = np.array(thresh_2_array)
            thresh_3_array = np.array(thresh_3_array)
            thresh_4_array = np.array(thresh_4_array)

            plt.figure(figsize=(10,6))

            plt.plot(dates_array, 100*(range_1[thresh_4_array]-1), alpha=1.0, color='r', label='95% chance of exceeding capacity')
            plt.plot(dates_array, 100*(range_1[thresh_3_array]-1), alpha=0.75, color='r', label='80% chance of exceeding capacity')
            plt.plot(dates_array, 100*(range_1[thresh_2_array]-1), alpha=1.0, color='k', linestyle='dashed', label='50% chance of exceeding capacity')
            plt.plot(dates_array, 100*(range_1[thresh_1_array]-1), alpha=0.50, color='r', label='20% chance of exceeding capacity')
            plt.plot(dates_array, 100*(range_1[thresh_0_array]-1), alpha=0.25, color='r', label='5% chance of exceeding capacity')
            #plt.axvline(dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(193)))
            ax = plt.gca()
            formatter = mdates.DateFormatter("%m-%d")
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            overflows_occur = 175
            alpha = 0.02
            for ele in np.sort(crit_day[crit_day != 369].copy()):
                    plt.fill_between(x=[dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(ele)), dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(upper_limit+5))], y1=-30, y2=120, color='k', alpha=alpha, hatch='/', linewidth=0) #label='scenarios begin to exceed capacity'
            #plt.fill_between(x=[dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(overflows_occur)), dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(205))], y1=-30, y2=120, color='k', alpha=0.05, hatch='/', linewidth=0) #label='scenarios begin to exceed capacity'
            #plt.fill_between(x=[dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(overflows_occur+2)), dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(205))], y1=-30, y2=120, color='k', alpha=0.05, hatch='/', linewidth=0) #label='scenarios begin to exceed capacity'
            plt.xlim([dt.datetime(month=2, day=13, year=2020) + dt.timedelta(days=int(145)),dt.datetime(month=10, day=1, year=2020)])
            plt.ylim([-30,100])
            plt.ylabel('Threshold % change in\n' + notif + '\nfrom previous week', fontsize=14)
            plt.xlabel('Date of Assessment', fontsize=14)
            plt.legend(fontsize=12)
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            #plt.savefig('overflow_prob_draft_2.png', dpi=200)
            #plt.savefig('overflow_prob_draft_2.pdf')
            plt.savefig('overflow_prob_draft_' + str(notif) + '_' + region + str(hospital_capacity) + '_1.png', dpi=200)
            plt.savefig('overflow_prob_draft_' + str(notif) + '_' + region + str(hospital_capacity) + '_1.pdf')