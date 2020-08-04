

getRt <- function(disease_incidence_data, method="uncertain_si", weekwindow=13){
  
  library(EpiEstim)
  
  ## check what si_distr to assume, or calculate from predictions, here using an example from the package
  if(method=="non_parametric_si"){  
    si_distr <- c(0.000, 0.233, 0.359, 0.198, 0.103, 0.053, 0.027 ,0.014 ,0.007, 0.003, 0.002 ,0.001)
    res <- estimate_R(incid = disease_incidence_data$I,
                      method = "non_parametric_si",
                      config = make_config(list(si_distr = si_distr)))
    
  }
  
  ### use parametric_si
  if(method=="parametric_si"){  
    res <- estimate_R(incid = disease_incidence_data$I,
                      method = "parametric_si",
                      config = make_config(list(mean_si = 2.6, std_si = 1.5)))
  }
  
  ## biweekly sliding
  t_start <- seq(2, nrow(disease_incidence_data)-weekwindow)   
  t_end <- t_start + weekwindow 
  

  ## estimate the reproduction number (method "uncertain_si")
  if(method=="uncertain_si"){
    res <- estimate_R(disease_incidence_data$I,
                      method = "uncertain_si",
                      config = make_config(list(
                        t_start = t_start, 
                        t_end = t_end,
                        mean_si = 4.6, std_mean_si = 1,
                        min_mean_si = 1, max_mean_si = 7.5,
                        std_si = 1.5, std_std_si = 0.5,
                        min_std_si = 0.5, max_std_si = 2.5,
                        n1 = 100, n2 = 100
                      ))
    )
  }
  
  
  
  return(res)
  
  
}