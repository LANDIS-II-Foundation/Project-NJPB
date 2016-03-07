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
base_dir="c:/users/rob/projects/NJPineBarrens2008/climatechangeruns"

replicates=range(1,2)  #produces list of replicates from 1 to N-1

#These two fields correspond to the path structure to the outputs and the names of things added to the graphs
runs = ["baseline"]

#Graph y-axis ranges
y_ranges=dict()#store in a dict for convenience later
y_ranges['Total C']=[5000,15000]
y_ranges['SOC']=[2000,5000]
y_ranges['Detrital C']=[500,1500]
y_ranges['Live C']=[4000,6000]
y_ranges['NEE']=[-50,20]

#graph line types, widths, point symbols, and colors - lists must be at least as long as number of replicates
#ltys=[1,2,3,1,2,3,1,2,3,1]
ltys=[1,1,5]
lwds=[1,2,2,1,2,2,1,2,2,1]
pchs=[20,19,1,2,18,10,4,5,7,8]
#cols=["black","gray"]
cols=["black","gray","black"]

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

#The summary data sets
soil_data=dict()
soil_data['Total C']=[]
soil_data['SOC']=[]
soil_data['Detrital C']=[]
soil_data['Live C']=[]
soil_data['NEE']=[]

# Summary data set for this scenario
scenario_data=dict()
#data structure: scenario_data[run][variable][year][rep1...repN], this makes it easier to use for time-series lines per variable

temp=[]

years=sets.Set()
for run in runs:
    run_dir="/fhmem-scenario-%s"%(run)

    scenario_data[run]=dict()
    scenario_data[run]['Total C']=dict()
    scenario_data[run]['SOC']=dict()
    scenario_data[run]['Detrital C']=dict()
    scenario_data[run]['Live C']=dict()
    scenario_data[run]['NEE']=dict()

    replicate_data=dict()

    for replicate in replicates:
        working_dir="%s/%s/replicate%s"%(base_dir,run_dir,replicate)
 
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
                years.add(year)
                NEEC=float(line[3])
                SOMTC=float(line[4])
                C_CohortLeaf=float(line[10])
                C_CohortWood=float(line[11])
                C_DeadWood=float(line[12])
                C_DeadRoot=float(line[13])
                C_SurfStruc=float(line[14])
                C_SurfMeta=float(line[15])
                C_SoilStruc=float(line[16])
                C_SoilMeta=float(line[17])

                #derive variables:
                NEE=NEEC
                SOC=SOMTC
                Detritus=C_DeadWood+C_DeadRoot+C_SurfStruc+C_SurfMeta+C_SoilStruc+C_SoilMeta
                AGL=C_CohortLeaf+C_CohortWood
                TotalC=SOC+Detritus+AGL

                # set up container array
                for variable in ['Total C','SOC','Detrital C','Live C','NEE']:
                    if not scenario_data[run][variable].has_key(year):
                        scenario_data[run][variable][year]=[]
                        
                scenario_data[run]['Total C'][year].append(TotalC)
                scenario_data[run]['SOC'][year].append(SOC)
                scenario_data[run]['Detrital C'][year].append(Detritus)
                scenario_data[run]['Live C'][year].append(AGL)
                scenario_data[run]['NEE'][year].append(NEE)

                temp.append(AGL)

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

for variable in ['Total C','SOC','Detrital C','Live C','NEE']:
    file_name="%s/Carbon_Time_Series_%s.jpg"%(base_dir, variable)
    r.jpeg(file_name,width=1100,height=850,quality=100)
    y_range=y_ranges[variable]
    # set up blank plot
    r.par(mgp = r.c(3,1,0), ps = 14)

    r.plot(start_year,y_range[0],pch=" ",xlim=[start_year,end_year],ylim=y_range,las=2,xlab="  ",ylab="  ",main=variable,xaxt='n')
    #make sure we have the x-axis correct
    r.axis(1,at=r.pretty(years,10),las=2) #this does 50 year intervals on the 0:400 range

    #add the lines
    run_num=0
    for run in runs:
        lwd=2
        lty=ltys[run_num]
        col=cols[run_num]
        plot_TS_err(scenario_data[run][variable],[lwd,lty,col])
        run_num+=1

    #add legend - upper left - need to tweak if we change lwd or lty
    r.legend(start_year,y_range[1],legend=runs,lwd=2,lty=1,col=cols[0:run_num+1])

    r.dev_off()



