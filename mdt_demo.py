import math
import gzip
import os
import pandas as pd
import numpy as np
from pandas import DataFrame

dir = "H:\MDT"


def cart2pol(x1, y1,x2,y2):
    rho = np.sqrt(((x1-x2)*27.21*3600)**2 + ((y1-y2)*30.887*3600)**2)
    phi = np.arctan2((y1-y2)*30.887*3600, (x1-x2)*27.21*3600)
    return(rho, phi)


"""读取目录下所有gz结尾的文件，整合成一张表"""
def read_all_gz(path):
    mdt = DataFrame()
    files = os.listdir(path)
    for file in files :
        if not os.path.isdir(file):
            if os.path.splitext(file)[-1] ==".gz":
                t = pd.read_csv(gzip.open(path +'/'+file),encoding = 'gbk')
                t = t.dropna(subset = ['UE经度','UE纬度'])
                t = t.drop([0])
                mdt = mdt.append(t,ignore_index=True)
    output = DataFrame()
    output["timestamp"]=mdt['时间戳']
    output["ue_x"]=mdt['UE经度'].astype("float")
    output["ue_y"]=mdt['UE纬度'].astype("float")
    output["ue_cell_id"]=mdt['服务小区ID'].astype("int64")
    output["ue_rsrp"]=mdt["服务小区RSRP"].astype("int")
    return output 

#ssssssss
#dsssdsdsd




def calc_polar_set(mdt_table,cell_table):
    mdt_polar_table = pd.merge(mdt_table,cell_table,how='left',left_on="ue_cell_id",right_on="cell_id")
    mdt_polar_table["distance"] = np.sqrt(((mdt_polar_table['ue_x']-mdt_polar_table['cell_x'])*np.cos(np.radians(mdt_polar_table["cell_y"]))*3600)**2 + ((mdt_polar_table['ue_y']-mdt_polar_table['cell_y'])*30.887*3600)**2)
    mdt_polar_table["rad"] = np.arctan2((mdt_polar_table["ue_y"]-mdt_polar_table["cell_y"]), (mdt_polar_table["ue_x"]-mdt_polar_table["cell_x"])*np.cos(np.radians(mdt_polar_table["cell_y"])))
    mdt_polar_table["degree"] = np.degrees(mdt_polar_table["rad"])

    return mdt_polar_table
def algorithm_real(raw_table,algorithm_type):
    f = lambda x:90 - x if x >=-180 and x<=90 else 450-x
    raw_table["degree_n"]  = raw_table["degree"].apply(f)

    f = lambda x:90 - x if x >=-90 and x<=180 else -270-x
    raw_table["degree_t"]  = raw_table["degree"].apply(f)

    if algorithm_type == "mean":
        grouped = raw_table.groupby(raw_table["cell_id"])

    return grouped

test = read_all_gz(dir)
cell = pd.read_csv("H:/MDT/cell.csv",encoding="gbk")
cell["cell_x"] = cell["cell_x"].astype("float")
cell["cell_y"] = cell["cell_y"].astype("float")

raw = calc_polar_set(test,cell)
out = algorithm_real(raw,"mean")

out.to_csv("H:/MDT/out11.csv",encoding="gbk")


