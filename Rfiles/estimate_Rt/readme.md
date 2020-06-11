

### estimate Rt

Using [EpiEstim](https://www.rdocumentation.org/packages/EpiEstim/versions/2.2-1) 

The 'estimate_R' function takes the incidence data as well as information about the serial interval.
The serial interval input can take different forms depending on the method used. 
Currently the default estimates for a 'uncertain si' distribution are used:

- mean_si =  4.6  #  2.6 
- std_mean_si = 1
- min_mean_si = 1 
- max_mean_si = 7.5 # 4.2
- std_si = 1.5 
- std_std_si = 0.5
- min_std_si = 0.5 
- max_std_si = 2.5
- n1 = 100
- n2 = 100

Following the example as described in https://rdrr.io/cran/EpiEstim/man/estimate_R.html

EpiEstim reference:
Thompson RN, Stockwin JE, van Gaalen RD, Polonsky JA, et al. Improved inference of time-varying reproduction numbers during infectious disease outbreaks. Epidemics (2019).


Serial interval updated with estimates from 
Li Q, Guan X, Wu P, et al. Early transmission dynamics in Wuhan,
China, of novel coronavirus-infected pneumonia. N Engl J Med
2020; 382: 1199–207.
and
Nishiura H, Linton NM, Akhmetzhanov AR. Serial interval of novel
coronavirus (2019-nCoV) infections. medRxiv 2020; published
online Feb 17. DOI:10.1101/2020.02.03.20019497 (preprint).

cited in
Peak, Corey M., Rebecca Kahn, Yonatan H. Grad, Lauren M. Childs, Ruoran Li, Marc Lipsitch, and Caroline O. Buckee. “Individual Quarantine versus Active Monitoring of Contacts for the Mitigation of COVID-19: A Modelling Study.” The Lancet Infectious Diseases 0, no. 0 (May 20, 2020). https://doi.org/10.1016/S1473-3099(20)30361-3.


