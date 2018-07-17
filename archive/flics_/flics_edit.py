# -*- coding: utf-8 -*-
"""
Created on Tue May  8 17:06:00 2018

@author: bar23
"""

import PIL.Image
import scipy
import scipy.fftpack
import numpy as np


filepath ="D://bio_project//Angoli_vena_conventional_Series012t5_6gradi.tif"

# here you have to write the name of the file
#image=PIL.Image.open("Angoli_vena_conventional_Series012t5_6gradi.tif")  

image=PIL.Image.open(filepath)
# half of the y dimension (in pixels) since we compute the 
#correlation function with FFTs
corrlimit=50     
columnlimit=320   # maximum distance (in pixels) between the columns
# to cross-correlate;  
columnstep=20    # possible column distances go from 0 to columnlimit, with 
#step equal to columnstep (in pixels):see line 49.(usually we choose columnstep
# equal to 5 or 10, and columnlimit equal to 30-50, but it depends on the data)
threshold=0    # here you can select a threshold to highlight 
#the fluorescent diagonal lines with respect to black stripes (the intensity 
#value of a pixel is put to zero every time it is below the chosen threshold)

def correlation(t1,m1,t2,m2,y):    
    fft1=scipy.fftpack.fft([(t1[i])-m1 for i in range(y)])
    fft2=scipy.fftpack.fft([(t2[i])-m2 for i in range(y)])
    fft1=np.ma.conjugate(fft1)
    crosscorr=np.real(scipy.fftpack.ifft(fft1*fft2)/(m1*m2*y))
    return crosscorr


def main_ccf(image,corrlimit,columnlimit,columnstep,threshold):
    x=image.size[0]
    y=image.size[1]
    data=[[0 for i in range(y)]for j in range(x)]
    a=list(image.getdata())
    #storage of the .tif file as an image matrix
    for i in range(y):
        for j in range(x):
            data[j][i]=float(a[i*x+j])
    #data thresholding (if needed)         
    for i in range(y):
        for j in range(x):
            if data[j][i]<threshold:
                data[j][i]=0.0
    #computation of the average value for each image column + 
    #computation of the cross-correlation function
    mean=[0.0 for i in range(x)]
    for i in range(x):
        for j in range(y):
            mean[i]=mean[i]+data[i][j]/y
    # the distance between the columns to cross-correlate varies
    # from 0 to columnlimit, with step equal to columnstep. 
    ccf_results={}   
    for i in range(0,columnlimit,columnstep):
        print (i)
        output=[0 for k in range(y)]
        for j in range(x-(i)):  #For each distance, ALL the pairs of columns at that distance are exploited. The average cross-correlation function is provided (convenient for statistical reasons)
            corr=correlation(data[j+i],mean[j+i],data[j],mean[j],y) 
            output=[output[l]+corr[l]/(x-i) for l in range(y)]     
            
        #only for lefttoright option
        #key= "correlation"+str(i)+"leftright"
        key = i
        res =[]
        res.append((0,output[0]))
        
        #f=open("correlation"+str(i)+"leftright.txt","w") 
        #f.write(str(0)+","+str(output[0])+"\n")
        for k in range(corrlimit):
            res.append((k+1,output[y-k-1]))
            #f.write(str(k+1)+","+str(output[y-k-1])+"\n")
            #(str(k+1)+","+str(output[y-k-1])
        ccf_results[key]=res
        #f.close()
    return ccf_results
            
results = main_ccf(image,corrlimit,columnlimit,columnstep,threshold)
global_fitting_res =[]


            
#para= [1,0.04,39.27101,0.04,0.02472,0.03651,0.001]
#fiting, pcoving=  global_fitting_v3.global_fit(results,para)           
            
            



         
            
            