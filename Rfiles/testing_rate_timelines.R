## Load packages
packages_needed <- c("tidyverse", "lubridate", "cowplot", "gridGraphics", "readxl")
lapply(packages_needed, require, character.only = TRUE)

## Load directories and custom objects and functions
source("load_paths.R")
source("processing_helpers.R")

LL_date <- "200727"

plot_dir <- file.path(project_path, "Plots + Graphs")
data_path <- file.path(data_path, "covid_IDPH") # covid_IDPH
shp_path <- file.path(data_path, "shapefiles")
plot_dir <- file.path(plot_dir, "_trend_tracking")
plot_dir_date <- file.path(plot_dir, "_trend_tracking", LL_date)
if (!dir.exists(plot_dir_date)) dir.create(plot_dir_date)

customTheme <- theme(
  strip.text.x = element_text(size = 16, face = "bold"),
  strip.text.y = element_text(size = 16, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 20, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 16),
  plot.caption = element_text(size = 10),
  legend.title = element_text(size = 16),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 18),
  axis.text.x = element_text(size = 16, angle = 45, vjust=0.5),
  axis.title.y = element_text(size = 18),
  axis.text.y = element_text(size = 16),
   panel.grid.major.x = element_blank(),
   panel.grid.minor.x = element_blank()
)

### Population
county_pop <- read.csv(file.path(data_path, "EMS Population", "covidregion_population_by_county.csv"))

### Case data
df <- read_csv(file.path(data_path, "/Corona virus reports", "IDPH Stats County public.csv")) %>%
  dplyr::mutate(update_date = as.Date(as.character(gsub("[/]", "-", update_date)), format = "%m-%d-%y")) %>%
  dplyr::filter(!(NOFO_Region %in% c("Illinois", "Out Of State", "Unassigned"))) %>%
  dplyr::mutate(
    County = toupper(County),
    County = gsub("DEWITT", "DE WITT", County)
  ) %>%
  left_join(county_pop, by = "County")


dfAggr <- df %>%
  as.data.frame() %>%
  dplyr::group_by(restore_region, new_restore_region, County, pop, update_date) %>%
  dplyr::summarize(
    Positive_Cases = max(Positive_Cases, na.rm = TRUE),
    Deaths = max(Deaths, na.rm = TRUE),
    Tested = max(Tested, na.rm = TRUE)
  ) %>%
  dplyr::group_by(restore_region, new_restore_region, County, pop) %>%
  dplyr::mutate(
    Positive_Casesd = Positive_Cases - lag(Positive_Cases),
    Deathsd = Deaths - lag(Deaths),
    Testedd = Tested - lag(Tested),
    week = week(update_date),
    month = month(update_date),
    nday = as.numeric(max(update_date) - update_date) + 1,
    weekday = weekdays(update_date)
  ) %>%
  dplyr::mutate(
    test_per1000 = (Testedd / pop) * 1000,
    test_per1000_cumul = (Tested / pop) * 1000
  )


dfAggr$nweek <- cut(dfAggr$nday, breaks = seq(0, max(dfAggr$nday), 7), labels = (c(1:19)))
dfAggr$new_restor = factor(dfAggr$new_restore_region, levels=c(1:11), labels=c(1:11))
dfAggr$new_restor_label = factor(dfAggr$new_restor, levels=c(1:11), labels=paste0("covid region ", c(1:11)))

dfAggr %>%
  group_by() %>%
  dplyr::select(nweek, update_date) %>%
  unique()

## ================================================
## PERCOUNTY
## ================================================

## Aggregate per week
dfAggr2 <- dfAggr %>%
  dplyr::group_by(restore_region, new_restore_region, County, pop, weekday, nweek, month) %>%
  dplyr::summarize(
    Testedd = mean(Testedd, na.rm = TRUE),
    test_per1000_cumul = mean(test_per1000_cumul, na.rm = TRUE),
    test_per1000 = mean(test_per1000, na.rm = TRUE),
    update_date = mean(update_date)
  )


sundays <- dfAggr2 %>%
  dplyr::group_by() %>%
  dplyr::filter(weekday == "Sunday" & update_date >= "2020-04-01") %>%
  dplyr::select(update_date) %>%
  unique() %>%
  rename(sunday = update_date)

saturdays <- dfAggr2 %>%
  dplyr::group_by() %>%
  dplyr::filter(weekday == "Saturday" & update_date >= "2020-04-01") %>%
  dplyr::select(update_date) %>%
  unique() %>%
  rename(saturday = update_date)

weekendDat <- cbind(saturdays, sundays)


#### Create map
dfAggr2



for (reg in unique(dfAggr2$restore_region)) {
  dat1 <- subset(dfAggr, restore_region == reg)
  dat <- subset(dfAggr2, restore_region == reg)
  titlelab <- toupper(unique(dat$restore_region))

  pplot <- ggplot(data = subset(dat1, update_date >= "2020-06-01")) +
    theme_minimal() +
    geom_rect(data = subset(weekendDat, saturday >= "2020-06-01"), aes(xmin = saturday, xmax = sunday, ymin = 0, ymax = Inf), alpha = 0.2) +
    geom_line(aes(x = update_date, y = test_per1000, col = as.factor(County)), size = 0.7, col = "deepskyblue3") +
    geom_point(aes(x = update_date, y = test_per1000, col = as.factor(County)), size = 1.7, col = "deepskyblue3") +
    geom_area(aes(x = update_date, y = test_per1000, fill = as.factor(County)), fill = "deepskyblue3", alpha = 0.3) +
    geom_hline(yintercept = 1) +
    scale_fill_brewer(palette = "RdYlBu") +
    scale_color_brewer(palette = "RdYlBu") +
    facet_wrap(~County) +
    labs(title = titlelab, subtitle = "", y = "Tests per 1000 population\n(per day)\n", x = "", caption = "Truncated at 5 per 1000") +
    geom_hline(yintercept = 0) +
    customTheme +
    scale_y_continuous(lim = c(0, 5), breaks = c(1:5), labels = c(1:5)) +
    scale_x_date(breaks = "2 week", minor_breaks = "2 week", labels = date_format("%d\n%b"))


  ggsave(paste0("County_timeline_daily_", reg, ".pdf"),
    plot = pplot, path = plot_dir_date, width = 18, height = 12, device = "pdf"
  )

  ggsave(paste0("County_timeline_daily_", reg, ".png"),
    plot = pplot, path = plot_dir_date, width = 18, height = 12, device = "png"
  )
}


### County weekly
for (reg in unique(dfAggr2$restore_region)) {
  dat <- subset(dfAggr2, restore_region == reg)
  titlelab <- toupper(unique(dat$restore_region))

  pplot <- ggplot(data = subset(dat, update_date >= "2020-05-01")) +
    theme_minimal() +
    geom_line(aes(x = update_date, y = test_per1000, col = as.factor(County)), size = 1, col = "deepskyblue3") +
    geom_area(aes(x = update_date, y = test_per1000, fill = as.factor(County)), fill = "deepskyblue3", alpha = 0.3) +
    geom_hline(yintercept = 1) +
    scale_fill_brewer(palette = "RdYlBu") +
    scale_color_brewer(palette = "RdYlBu") +
    facet_wrap(~County) +
    labs(title = titlelab, subtitle = "", y = "Tests per 1000 population\n(7 days average)\n", x = "") +
    geom_hline(yintercept = 0) +
    customTheme +
    scale_x_date(breaks = "2 week", minor_breaks = "2 week", labels = date_format("%d\n%b")) +
    scale_y_continuous(lim = c(0, 10), breaks = seq(0, 10, 2), labels = seq(0, 10, 2))

  ggsave(paste0("County_timeline_7daysAvr_", reg, ".pdf"),
    plot = pplot, path = plot_dir_date, width = 18, height = 12, device = "pdf"
  )

  ggsave(paste0("County_timeline_7daysAvr_", reg, ".png"),
    plot = pplot, path = plot_dir_date, width = 18, height = 12, device = "png"
  )
}



## ================================================
##### Combined plot per restore and covid region
## ================================================
regions <- list(
  "North-Central" = c(1, 2),
  "Northeast" = c(7, 8, 9, 10, 11),
  "Central" = c(3, 6),
  "Southern" = c(4, 5)
)


for (i in c(1:length(regions))) {
  reg <- names(regions)[[i]]
  covidregs <- regions[[i]]

  ptotal <- dfAggr %>%
    filter(restore_region == reg) %>%
    mutate(restore_region = "total") %>%
    dplyr::group_by(restore_region, week, month) %>%
    dplyr::summarize(
      update_date = max(update_date),
      Tested = sum(Tested, na.rm = TRUE),
      Testedd = sum(Testedd, na.rm = TRUE),
      pop = sum(pop, na.rm = TRUE)
    ) %>%
    mutate(
      test_per1000 = (Testedd / pop) * 1000,
      test_per1000_cumul = (Tested / pop) * 1000
    ) %>%
    filter(update_date >= "2020-06-01") %>%
    ggplot() +
    theme_cowplot() +
    facet_wrap(~restore_region, scales = "free", nrow = 1) +
    geom_line(aes(x = update_date, y = test_per1000), size = 1.3, col = "deepskyblue3") +
    geom_point(aes(x = update_date, y = test_per1000), size = 2.3, fill = "deepskyblue3", shape = 21, col = "white") +
    geom_area(aes(x = update_date, y = test_per1000), fill = "deepskyblue3", alpha = 0.3) +
    geom_hline(yintercept = 1, linetype = "dashed") +
    scale_fill_brewer(palette = "RdYlBu") +
    scale_color_brewer(palette = "RdYlBu") +
    labs(subtitle = "", y = reg, x = "") +
    geom_hline(yintercept = c(-Inf, Inf)) +
    geom_vline(xintercept = c(-Inf, Inf)) +
    customTheme +
    scale_x_date(breaks = "1 week", minor_breaks = "1 week", labels = date_format("%d/%m")) +
    scale_y_continuous(lim = c(0, 5), breaks = c(1:5), labels = c(1:5), expand=c(0,0)) +
    theme(panel.spacing = unit(2, "lines"),
          plot.margin = unit(c(0,0,0,0), "cm"))

  pcovidreg <- dfAggr %>%
    filter(new_restor %in% covidregs) %>%
    dplyr::group_by(new_restor,new_restor_label, week, month) %>%
    dplyr::summarize(
      update_date = max(update_date),
      Tested = sum(Tested, na.rm = TRUE),
      Testedd = sum(Testedd, na.rm = TRUE),
      pop = sum(pop, na.rm = TRUE)
    ) %>%
    mutate(
      test_per1000 = (Testedd / pop) * 1000,
      test_per1000_cumul = (Tested / pop) * 1000
    ) %>%
    filter(update_date >= "2020-06-01") %>%
    ggplot() +
    theme_cowplot() +
    geom_line(aes(x = update_date, y = test_per1000), size = 1.3, col = "deepskyblue3") +
    geom_point(aes(x = update_date, y = test_per1000), size = 2.3, fill = "deepskyblue3", shape = 21, col = "white") +
    geom_area(aes(x = update_date, y = test_per1000), fill = "deepskyblue3", alpha = 0.3) +
    geom_hline(yintercept = 1, linetype = "dashed") +
    scale_fill_brewer(palette = "RdYlBu") +
    scale_color_brewer(palette = "RdYlBu") +
    facet_wrap(~new_restor_label, scales = "free", nrow = 1) +
    labs(subtitle = "", y = "", x = "") +
    geom_hline(yintercept = c(-Inf, Inf)) +
    geom_vline(xintercept = c(-Inf, Inf)) +
    customTheme +
    scale_x_date(breaks = "1 week", minor_breaks = "1 week", labels = date_format("%d/%m")) +
    scale_y_continuous(lim = c(0, 5), breaks = c(1:5), labels = c(1:5), expand=c(0,0)) +
    theme(panel.spacing = unit(2, "lines"),
          plot.margin = unit(c(0,0,0,0), "cm"))


  if (i == 1) r1 <- ptotal
  if (i == 2) r2 <- ptotal
  if (i == 3) r3 <- ptotal
  if (i == 4) r4 <- ptotal


  if (i == 1) p1 <- pcovidreg
  if (i == 2) p2 <- pcovidreg
  if (i == 3) p3 <- pcovidreg
  if (i == 4) p4 <- pcovidreg
}


# Tests per 1000 population\n(7 day average)
c1 <- plot_grid(r1, p1, NULL, NULL, NULL, nrow = 1, rel_widths = c(1, 2, 1, 1, 1))
c2 <- plot_grid(r2, p2, nrow = 1, rel_widths = c(1, 5))
c3 <- plot_grid(r3, p3, NULL, NULL, NULL, nrow = 1, rel_widths = c(1, 2, 1, 1, 1))
c4 <- plot_grid(r4, p4, NULL, NULL, NULL, nrow = 1, rel_widths = c(1, 2, 1, 1, 1))


title <- ggdraw() + draw_label("Tests per 1000 population (7 day average)", fontface='bold')

pplot <- plot_grid(c1, c2, c3, c4, ncol = 1)
pplot <-  plot_grid(title, pplot, ncol=1, rel_heights=c(0.1, 1)) # rel_heights values control title margins


ggsave(paste0("Regions_7dayAvr_testingRates_", LL_date, "LLpublic.png"),
       plot = pplot, path = plot_dir, width = 20, height = 14, device = "png"
)

ggsave(paste0("Regions_7dayAvr_testingRates_", LL_date, "LLpublic.pdf"),
       plot = pplot, path = plot_dir, width = 20, height = 14, device = "pdf"
)

###### Adjust for Champaign county
p3sub1 <- dfAggr %>%
  filter(new_restor %in% c(6) & County !="CHAMPAIGN" ) %>%
  mutate(new_restor_label="6 - without Champaign") %>%
  dplyr::group_by(new_restor,new_restor_label, week, month) %>%
  dplyr::summarize(
    update_date = max(update_date),
    Tested = sum(Tested, na.rm = TRUE),
    Testedd = sum(Testedd, na.rm = TRUE),
    pop = sum(pop, na.rm = TRUE)
  ) %>%
  mutate(
    test_per1000 = (Testedd / pop) * 1000,
    test_per1000_cumul = (Tested / pop) * 1000
  ) %>%
  filter(update_date >= "2020-06-01") %>%
  ggplot() +
  theme_cowplot() +
  geom_line(aes(x = update_date, y = test_per1000), size = 1.3, col = "deepskyblue3") +
  geom_point(aes(x = update_date, y = test_per1000), size = 2.3, fill = "deepskyblue3", shape = 21, col = "white") +
  geom_area(aes(x = update_date, y = test_per1000), fill = "deepskyblue3", alpha = 0.3) +
  geom_hline(yintercept = 1, linetype = "dashed") +
  scale_fill_brewer(palette = "RdYlBu") +
  scale_color_brewer(palette = "RdYlBu") +
  facet_wrap(~new_restor_label, scales = "free", nrow = 1) +
  labs(subtitle = "", y = "", x = "") +
  geom_hline(yintercept = c(-Inf, Inf)) +
  geom_vline(xintercept = c(-Inf, Inf)) +
  customTheme +
  scale_x_date(breaks = "1 week", minor_breaks = "1 week", labels = date_format("%d/%m")) +
  scale_y_continuous(lim = c(0, 5), breaks = c(1:5), labels = c(1:5), expand=c(0,0)) +
  theme(panel.spacing = unit(2, "lines"))


p3sub2 <- dfAggr %>%
  filter(new_restor %in% c(6) & County =="CHAMPAIGN" ) %>%
  mutate(new_restor_label="6 - Champaign county") %>%
  dplyr::group_by(new_restor_label, week, month) %>%
  dplyr::summarize(
    update_date = max(update_date),
    test_per1000 = mean(test_per1000, na.rm = TRUE),
  ) %>%
  filter(update_date >= "2020-06-01") %>%
  ggplot() +
  theme_cowplot() +
  geom_line(aes(x = update_date, y = test_per1000), size = 1.3, col = "deepskyblue3") +
  geom_point(aes(x = update_date, y = test_per1000), size = 2.3, fill = "deepskyblue3", shape = 21, col = "white") +
  geom_area(aes(x = update_date, y = test_per1000), fill = "deepskyblue3", alpha = 0.3) +
  geom_hline(yintercept = 1, linetype = "dashed") +
  scale_fill_brewer(palette = "RdYlBu") +
  scale_color_brewer(palette = "RdYlBu") +
  facet_wrap(~new_restor_label, scales = "free", nrow = 1) +
  labs(subtitle = "", y = "", x = "") +
  geom_hline(yintercept = c(-Inf, Inf)) +
  geom_vline(xintercept = c(-Inf, Inf)) +
  customTheme +
  scale_x_date(breaks = "1 week", minor_breaks = "1 week", labels = date_format("%d/%m")) +
  scale_y_continuous(lim = c(0,10), breaks = seq(1,10,2), labels =seq(1,10,2), expand=c(0,0)) +
  theme(panel.spacing = unit(2, "lines"))


# Tests per 1000 population\n(7 day average)
c1 <- plot_grid(r1, p1, NULL, NULL, NULL, nrow = 1, rel_widths = c(1, 2, 1, 1, 1))
c2 <- plot_grid(r2, p2, nrow = 1, rel_widths = c(1, 5))
c3 <- plot_grid(r3, p3, p3sub1, p3sub2, NULL, nrow = 1, rel_widths = c(1, 2, 1, 1, 1))
c4 <- plot_grid(r4, p4, NULL, NULL, NULL, nrow = 1, rel_widths = c(1, 2, 1, 1, 1))


title <- ggdraw() + draw_label("Tests per 1000 population (7 day average)", fontface='bold')

pplot <- plot_grid(c1, c2, c3, c4, ncol = 1)
pplot <-  plot_grid(title, pplot, ncol=1, rel_heights=c(0.01,1)) # rel_heights values control title margins


ggsave(paste0("Regions_7dayAvr_testingRates_Champaign_", LL_date, "LLpublic.png"),
       plot = pplot, path = plot_dir, width = 20, height = 14, device = "png"
)

ggsave(paste0("Regions_7dayAvr_testingRates_Champaign_", LL_date, "LLpublic.pdf"),
       plot = pplot, path = plot_dir, width = 20, height = 14, device = "pdf"
)



plotRestoreCovidSeparate=FALSE
if(plotRestoreCovidSeparate){
  ## ================================================
  ## PER RESTORE REGION
  ## ================================================
  weekendDat <- weekendDat %>% filter(saturday >= "2020-06-01")
  
  pdaily <- dfAggr %>%
    group_by(restore_region, weekday, update_date, nweek, month) %>%
    dplyr::summarize(
      Tested = sum(Tested, na.rm = TRUE),
      Testedd = sum(Testedd, na.rm = TRUE),
      pop = sum(pop, na.rm = TRUE),
      update_date = max(update_date)
    ) %>%
    mutate(
      test_per1000 = (Testedd / pop) * 1000,
    ) %>%
    filter(update_date >= "2020-06-01") %>%
    ggplot() +
    theme_minimal() +
    geom_rect(data = weekendDat, aes(xmin = saturday, xmax = sunday, ymin = 0, ymax = Inf), alpha = 0.2) +
    geom_line(aes(x = update_date, y = test_per1000), size = 1, col = "deepskyblue3") +
    geom_point(aes(x = update_date, y = test_per1000), size = 2.3, fill = "deepskyblue3", shape = 21, col = "white") +
    geom_area(aes(x = update_date, y = test_per1000), fill = "deepskyblue3", alpha = 0.3) +
    scale_fill_brewer(palette = "RdYlBu") +
    scale_color_brewer(palette = "RdYlBu") +
    facet_wrap(~restore_region) +
    labs(subtitle = "", y = "Tests per 1000 population\n(per day)\n", x = "") +
    geom_hline(yintercept = 0) +
    customTheme +
    scale_x_date(breaks = "1 week", minor_breaks = "1 week", labels = date_format("%d/%m"))
  
  
  ggsave(paste0("RestoreRegion_daily_testingRates.pdf"),
         plot = pdaily, path = plot_dir_date, width = 12, height = 8, device = "pdf"
  )
  
  ggsave(paste0("RestoreRegion_daily_testingRates.png"),
         plot = pdaily, path = plot_dir_date, width = 12, height = 8, device = "png"
  )
  
  
  ### Aggregate weeks
  pweekly <- dfAggr %>%
    group_by(restore_region, week, month) %>%
    dplyr::summarize(
      Tested = sum(Tested, na.rm = TRUE),
      Testedd = sum(Testedd, na.rm = TRUE),
      pop = sum(pop, na.rm = TRUE),
      update_date = max(update_date)
    ) %>%
    mutate(
      test_per1000 = (Testedd / pop) * 1000,
    ) %>%
    filter(update_date >= "2020-06-01") %>%
    ggplot() +
    theme_minimal() +
    geom_line(aes(x = update_date, y = test_per1000), size = 1.3, col = "deepskyblue3") +
    geom_point(aes(x = update_date, y = test_per1000), size = 2.3, fill = "deepskyblue3", shape = 21, col = "white") +
    geom_area(aes(x = update_date, y = test_per1000), fill = "deepskyblue3", alpha = 0.3) +
    geom_hline(yintercept = 1, linetype = "dashed") +
    scale_fill_brewer(palette = "RdYlBu") +
    scale_color_brewer(palette = "RdYlBu") +
    facet_wrap(~restore_region, scale = "free_x") +
    labs(subtitle = "", y = "Tests per 1000 population\n(7 day average)\n", x = "") +
    geom_hline(yintercept = 0) +
    customTheme +
    scale_x_date(breaks = "1 week", minor_breaks = "1 week", labels = date_format("%d/%m"))
  
  
  ggsave(paste0("RestoreRegion_7dayAvr_testingRates.png"),
         plot = pweekly, path = plot_dir_date, width = 12, height = 8, device = "png"
  )
  
  ggsave(paste0("RestoreRegion_7dayAvr_testingRates.pdf"),
         plot = pweekly, path = plot_dir_date, width = 12, height = 8, device = "pdf"
  )
  
  rm(pweekly)
  
  ## ================================================
  ## PER COVID REGION
  ## ================================================
  
  weekendDat <- weekendDat %>% filter(saturday >= "2020-04-15")
  dfAggr$new_restor <- factor(dfAggr$new_restore_region, levels = c(1:12), labels = c(1:12))
  
  
  pdaily <- dfAggr %>%
    group_by(new_restor, weekday, update_date, nweek, month) %>%
    dplyr::summarize(
      Tested = sum(Tested, na.rm = TRUE),
      Testedd = sum(Testedd, na.rm = TRUE),
      pop = sum(pop, na.rm = TRUE)
    ) %>%
    mutate(
      test_per1000 = (Testedd / pop) * 1000,
      test_per1000_cumul = (Tested / pop) * 1000
    ) %>%
    filter(update_date >= "2020-06-01") %>%
    ggplot() +
    theme_minimal() +
    geom_line(aes(x = update_date, y = test_per1000), size = 1, col = "deepskyblue3") +
    geom_point(aes(x = update_date, y = test_per1000), size = 2.3, col = "deepskyblue3") +
    geom_area(aes(x = update_date, y = test_per1000), fill = "deepskyblue3", alpha = 0.3) +
    scale_fill_brewer(palette = "RdYlBu") +
    scale_color_brewer(palette = "RdYlBu") +
    facet_wrap(~new_restor, scales = "free_x") +
    labs(subtitle = "", y = "Tests per 1000 population\n(per day)\n", x = "") +
    geom_hline(yintercept = 0) +
    customTheme +
    scale_x_date(breaks = "1 week", minor_breaks = "1 week", labels = date_format("%d/%m"))
  
  
  ggsave(paste0("CovidRegion_daily_testingRates.pdf"),
         plot = pdailyTrunc, path = plot_dir_date, width = 12, height = 8, device = "pdf"
  )
  
  ggsave(paste0("CovidRegion_daily_testingRates.png"),
         plot = pdailyTrunc, path = plot_dir_date, width = 12, height = 8, device = "png"
  )
  
  
  
  pweekly <- dfAggr %>%
    group_by(new_restor, week, month) %>%
    dplyr::summarize(
      update_date = max(update_date),
      Tested = sum(Tested, na.rm = TRUE),
      Testedd = sum(Testedd, na.rm = TRUE),
      pop = sum(pop, na.rm = TRUE)
    ) %>%
    mutate(
      test_per1000 = (Testedd / pop) * 1000,
      test_per1000_cumul = (Tested / pop) * 1000
    ) %>%
    filter(update_date >= "2020-06-01") %>%
    ggplot() +
    theme_minimal() +
    geom_line(aes(x = update_date, y = test_per1000), size = 1.3, col = "deepskyblue3") +
    geom_point(aes(x = update_date, y = test_per1000), size = 2.3, fill = "deepskyblue3", shape = 21, col = "white") +
    geom_area(aes(x = update_date, y = test_per1000), fill = "deepskyblue3", alpha = 0.3) +
    geom_hline(yintercept = 1, linetype = "dashed") +
    scale_fill_brewer(palette = "RdYlBu") +
    scale_color_brewer(palette = "RdYlBu") +
    facet_wrap(~new_restor, scales = "free_x") +
    labs(subtitle = "Covid-regions (1-11)", y = "Tests per 1000 population\n(7 day average)\n", x = "") +
    geom_hline(yintercept = 0) +
    customTheme +
    scale_x_date(breaks = "1 week", minor_breaks = "1 week", labels = date_format("%d/%m")) +
    theme(panel.spacing = unit(2, "lines"))
  
  
  ggsave(paste0("CovidRegion_7dayAvr_testingRates.png"),
         plot = pweekly, path = plot_dir_date, width = 12, height = 8, device = "png"
  )
  
  ggsave(paste0("CovidRegion_7dayAvr_testingRates.pdf"),
         plot = pweekly, path = plot_dir_date, width = 12, height = 8, device = "pdf"
  )
  
}