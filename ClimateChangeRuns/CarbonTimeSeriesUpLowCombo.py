#Various soil stats.py
#Written by Brendan C. Ward
#Overview: script reads LANDIS-II soil log files and creates pdfs.

import os,re,sets
from rpy import *

####################################################################################
### Input parameters ###############################################################
####################################################################################

#output_dir="j:/projects/century/willowcreekmulticell"
#base_dir="//Rubus/C Drive/Users/Rob/Projects/Century/WillowCreekMultiCell"
base_dir="j:/projects/NJPineBarrens2008/ClimateChangeRuns"
scenarios = ["baseline", "a2"]
ecoregions = ['upland','wetland','plains']

replicates=range(1,2)  #produces list of replicates from 1 to N-1



####################################################################################
# Convenience functions
####################################################################################

def list_to_str(cur_list):
    return str(cur_list).replace("[","").replace("]","").replace("'","").replace(" ","")


#function to plot time-series lines and error bars
def plot_TS_err(data,plot_params=[]):  #data is a dict, ...[time][x1...xi], plot_params is [lwd,lty,col]
    if plot_params:
        lwd,lty,col=plot_params
    else:
        lwd=1
        lty=1
        col="black"
    #deconstruct dictionary into stats
    intervals=data.keys()
    intervals.sort()
    means=[]
    upr_errs=[]
    lwr_errs=[]
    for interval in intervals:
        mean=r.mean(data[interval])
        means.append(mean)
        err=r.sd(data[interval])/r.sqrt(len(data[interval]))
        upr_errs.append(mean+err)
        lwr_errs.append(mean-err)
    #plot the line
    r.lines(intervals,means,lwd=lwd,lty=lty,col=col)
    #plot the error bars
    r.segments(intervals,lwr_errs,intervals,upr_errs,lty=2,col=col)
    #plot the bounding ticks
    r.points(intervals,lwr_errs,pch="-",cex=1.2,col=col)
    r.points(intervals,upr_errs,pch="-",cex=1.2,col=col)
    
####################################################################################
### Main
####################################################################################


# Summary data set for this scenario
scenario_data=dict()
#data structure: scenario_data[run][variable][year][rep1...repN], this makes it easier to use for time-series lines per variable

temp=[]

years=sets.Set()
for scenario in scenarios:
    scenario_data[scenario]=dict()

    #for ecoregion in ecoregions:
    scenario_data[scenario]['upland']=dict()
    scenario_data[scenario]['wetland']=dict()
    scenario_data[scenario]['plains']=dict()
    replicate_data=dict()

for scenario in scenarios:
    for replicate in replicates:
        working_dir="%s/fhmem-scenario-%s/replicate%s"%(base_dir,scenario,replicate)
 
        #Make sure files exist
        if not (os.access("%s/century-succession-log.csv"%(working_dir),os.F_OK) and os.access("%s/Landis-log.txt"%(working_dir),os.F_OK)):
            print "Missing files for replicate %s, %s"%(working_dir,replicate)
        else:
            infile=open("%s/century-succession-log.csv"%(working_dir),'r')
            header=infile.readline().split(",")
            data=infile.readlines()
            infile.close()

            #extract out the data
            for line in data:
                line=line.split(",")
                year=int(line[0])
                ecoregion=str.lstrip(line[1])
                if "up" in ecoregion:
                    ecoregion='upland'
                if "wet" in ecoregion:
                    ecoregion='wetland'
                #NEE=float(line[3])
                SOC=float(line[4])
                #ANPP=float(line[5])
                C_CohortLeaf=float(line[10])
                C_CohortWood=float(line[11])
                C_DeadWood=float(line[12])
                C_DeadRoot=float(line[13])
                C_SurfStruc=float(line[14])
                C_SurfMeta=float(line[15])
                C_SoilStruc=float(line[16])
                C_SoilMeta=float(line[17])
                #derive variables:
                Detritus=C_DeadWood+C_DeadRoot+C_SurfStruc+C_SurfMeta+C_SoilStruc+C_SoilMeta
                AGL=C_CohortLeaf+C_CohortWood
                TotalC=SOC+Detritus+AGL

                # set up container array
                if year > 0:
                    years.add(year)
                    if not scenario_data[scenario][ecoregion].has_key(year):
                        scenario_data[scenario][ecoregion][year]=[]
                            
                    scenario_data[scenario][ecoregion][year].append(TotalC)

####################################################################################
### PLot
####################################################################################
    
#Open landscape summary PDF
#r.pdf("%s/Carbon_Time_Series.pdf"%(base_dir),width=11,height=8.5)
#plot one variable per page for now, multiple scenarios on one graph

years=list(years)
years.sort()
start_year=min(years)+1
end_year=max(years)

# GRAPH 1
#graph line types, widths, point symbols, and colors - lists must be at least as long as number of replicates
#ltys=[1,2,3,1,2,3,1,2,3,1]
#ltys: 1=solid; 5=dashed
ltys=[1,1,2, 2, 3, 3]
legendltys=[1,2]
lwds=[1,2,2,1,2,2,1,2,2,1,2,2]
pchs=[20,19,1,2,18,10,4,5,7,8,20,19]
#cols=["black","gray"]
cols=["blue", "red", "blue", "red", "blue", "red"]

file_name="%s/Combo_Time_Series_%s.jpg"%(base_dir, 'upwet')
r.jpeg(file_name,width=1100,height=850,quality=100)
y_range=[10000,20000]
# set up blank plot
r.par(mgp = r.c(3,1,0), ps = 14)

r.plot(start_year,y_range[0],pch=" ",xlim=[start_year,end_year],ylim=y_range,las=2,xlab="  ",ylab="  ",main="Total C",xaxt='n')
#make sure we have the x-axis correct
r.axis(1,at=r.pretty(years,5),las=2) #this does 50 year intervals on the 0:400 range

temp_ecoregions=['upland','wetland']
#add the lines
eco_num=0
scen_num=0
for scenario in scenarios:
    scen_num+=1
    for ecoregion in temp_ecoregions:
        lwd=2
        lty=ltys[scen_num]
        col=cols[eco_num]
        plot_TS_err(scenario_data[scenario][ecoregion],[lwd,lty,col])
        eco_num+=1

#add legend - upper left - need to tweak if we change lwd or lty
#r.legend(start_year,y_range[1],legend=ecoregions,lwd=2,lty=1,col=cols[0:eco_num+1])
r.legend("bottomleft", "(x,y)",legend=temp_ecoregions,lwd=2,lty=1,col=cols[0:eco_num+1])
r.legend("bottomright", "(x,y)",legend=scenarios,lwd=2,lty=legendltys[0:2],col="black")

r.dev_off()


# GRAPH 2
#graph line types, widths, point symbols, and colors - lists must be at least as long as number of replicates
#ltys=[1,2,3,1,2,3,1,2,3,1]
#ltys: 1=solid; 5=dashed
ltys=[1,2,3]
lwds=[1,2,2,1,2,2,1,2,2,1,2,2]
pchs=[20,19,1,2,18,10,4,5,7,8,20,19]
#cols=["black","gray"]
cols=["black", "black", "black"]

file_name="%s/Combo_Time_Series_%s.jpg"%(base_dir, 'plains')
r.jpeg(file_name,width=1100,height=850,quality=100)
y_range=[0,5000]
# set up blank plot
r.par(mgp = r.c(3,1,0), ps = 14)

r.plot(start_year,y_range[0],pch=" ",xlim=[start_year,end_year],ylim=y_range,las=2,xlab="  ",ylab="  ",main="Total C",xaxt='n')
#make sure we have the x-axis correct
r.axis(1,at=r.pretty(years,5),las=2) #this does 50 year intervals on the 0:400 range

temp_ecoregions=['plains']
#add the lines
eco_num=0
for scenario in scenarios:
    for ecoregion in temp_ecoregions:
        lwd=2
        lty=ltys[eco_num]
        col=cols[eco_num]
        plot_TS_err(scenario_data[scenario][ecoregion],[lwd,lty,col])
        eco_num+=1

#add legend - upper left - need to tweak if we change lwd or lty
#r.legend(start_year,y_range[1],legend=ecoregions,lwd=2,lty=1,col=cols[0:eco_num+1])
r.legend("bottomleft", "(x,y)",legend=temp_ecoregions,lwd=2,lty=1,col=cols[0:eco_num+1])


r.dev_off()



