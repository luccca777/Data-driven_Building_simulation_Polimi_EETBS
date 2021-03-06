import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
DataFolderPath="C:/Users/Clevo/Desktop/project data/0 Data"
DataFileName="building61duringoffice.csv"
DataFile=DataFolderPath+'/'+ DataFileName
DF_data=pd.read_csv(DataFile,sep=",",index_col=0) 
DF_data.head()
DF_data.index=pd.to_datetime(DF_data.index)
def lag_column(df, column_name, lag_period=1):
    for i in range(1,lag_period+1,1):
        new_column_name=column_name+"-"+str(i*15)+"min"
        df[new_column_name]=df[column_name].shift(i)
    return df
DF_lagged=DF_data.copy()
DF_lagged=lag_column(DF_data,"OAT",24)
DF_lagged.dropna(inplace=True)
DF_lagged.corr()
#From corellation plot, temperature shift of 15 min is most correlated with power consumption
def normalize(df):
    return (df-df.min())/(df.max()-df.min())
DF_Final=pd.read_csv(DataFile,sep=",",index_col=0) 
DF_Final.index=pd.to_datetime(DF_Final.index)
DF_Final["hour"]=DF_Final.index.hour
DF_Final["day of week"]=DF_Final.index.dayofweek #from 0-Monday to 6- Sunday
DF_Final["month"]=DF_Final.index.month #month 
DF_Final["week of year"]=DF_Final.index.week
DF_Final.head()
def weekendDetector(day):
    weekendLabel=0
    if (day==5 or day ==6):
        weekendLabel=1
    return weekendLabel
def dayDetector(hour):
    dayLabel=0
    if (hour<21 and hour>8):
        dayLabel=1
    return dayLabel
def SummSpringDetector(month): #There is a difference in power consumption in summer and in winter !!!! 
    monthDetector=0
    if(month>3 and month<10):
        monthDetector=1
    return monthDetector
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar #taking state hollidays in USA in period of 01.01.2010 - 31.12.2010
dr = pd.date_range(start='2010-01-01', end='2010-12-31')
df = pd.DataFrame()
df['Date'] = dr
cal = calendar()
holidays = cal.holidays(start=dr.min(), end=dr.max())
holiday=["2010-01-01","2010-01-18","2010-02-15","2010-05-31","2010-07-05","2010-09-06","2010-10-11","2010-11-11","2010-11-25","2010-12-24","2010-12-31"]      
#have some problems,because I was giving value of weekendDetector=1 for hollidays ( as it is a weekend ) 
DF_Final["weekend or weekday"]=[weekendDetector(day) for day in DF_Final["day of week"]]
DF_Final["day or night"]=[dayDetector(hour) for hour in DF_Final["hour"]]
DF_Final["summer or winter"]=[SummSpringDetector(month) for month in DF_Final["month"]]
for day in holiday:
    DF_Final["weekend or weekday"][day]=1
DF_Final["2010-11-25"]
DF_Final_Lagged=DF_Final
DF_Final_Lagged=lag_column(DF_Final_Lagged,"OAT",28) #taking values of temperatures for previous 7 hours in a range of 15 min as a different columns
DF_Final_Lagged=lag_column(DF_Final_Lagged,"Building 6 kW",96) #taking values of power consumption from previous 24 hours in a range of 15 min and put them in different columns
DF_Final_Lagged.head(96)
DF_Final_Lagged.dropna(inplace=True)
DF_target=DF_Final_Lagged["Building 6 kW"] #target values 
DF_features=DF_Final_Lagged.drop("Building 6 kW",axis=1) #values that should be used for building a model that should predict value of power consumption
DF_Final_Lagged_norm=normalize(DF_Final_Lagged) #normalized values of values 
DF_target_norm=DF_Final_Lagged_norm["Building 6 kW"] 
DF_features_norm=DF_Final_Lagged_norm.drop("Building 6 kW",axis=1)

from sklearn.model_selection import train_test_split #dividing data into train and test data
X_train, X_test, Y_train, Y_test=train_test_split(DF_features,DF_target,test_size=0.2,random_state=41234)
X_train_norm, X_test_norm, y_train_norm, y_test_norm = train_test_split(DF_features_norm, DF_target_norm, test_size=0.2, random_state=41234)

from sklearn import linear_model #usage of Linear Regression for building prediction model
linear_reg=linear_model.LinearRegression()
linear_reg.fit(X_train,Y_train)
predict_linearReg_split=linear_reg.predict(X_test)
Y_test.index
predict_DF_linearReg_split=pd.DataFrame(predict_linearReg_split,index=Y_test.index,columns=["Power predicted_Linear Reg. [kW]"])
predict_DF_linearReg_split=predict_DF_linearReg_split.join(Y_test)
predict_DF_linearReg_split['2010-08-01':'2010-08-05'].plot()
plt.xlabel('Time')
plt.ylabel("Power Consumption with Linear Regression[kW]")
plt.ylim([0,400])
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
mean_absolute_error_linearReg_split=mean_absolute_error(Y_test,predict_DF_linearReg_split["Power predicted_Linear Reg. [kW]"])
print "Mean absolute error using  Linear Regression is :"+str(mean_absolute_error_linearReg_split)
mean_squared_error_linearReg_split=mean_squared_error(Y_test,predict_DF_linearReg_split["Power predicted_Linear Reg. [kW]"])
print "Mean squared error using  Linear Regression is :"+str(mean_squared_error_linearReg_split)
r2_error=r2_score(Y_test,predict_DF_linearReg_split["Power predicted_Linear Reg. [kW]"])
print "R2 error using  Linear Regression is :"+str(r2_error)
coeff_variation = np.sqrt(mean_squared_error_linearReg_split)/Y_test.mean()
print "Coefficient variation using  Linear Regression is :"+str(coeff_variation)

from sklearn.model_selection import cross_val_predict #Usage of Cross Validation
predict_linearReg_CV=cross_val_predict(linear_reg,DF_features,DF_target,cv=10)
predict_DF_linearReg_split_CV=pd.DataFrame(predict_linearReg_CV,index=DF_target.index,columns=["Power cons Predict_linearReg_CV"])
predict_DF_linearReg_split_CV=predict_DF_linearReg_split_CV.join(DF_target)
predict_DF_linearReg_split_CV_ChosenDates=predict_DF_linearReg_split_CV["2010-08-01":"2010-08-05"]
R2_score_linearReg_CV = r2_score(predict_DF_linearReg_split_CV["Building 6 kW"],predict_DF_linearReg_split_CV["Power cons Predict_linearReg_CV"])
print "R2 error using Linear Regression is :"+str(R2_score_linearReg_CV)
mean_absolute_error_linearReg_CV = mean_absolute_error(predict_DF_linearReg_split_CV["Building 6 kW"],predict_DF_linearReg_split_CV["Power cons Predict_linearReg_CV"])
print "Mean absolute error using Cross Validation  is :"+str(mean_absolute_error_linearReg_CV)
mean_squared_error_linearReg_CV = mean_squared_error(predict_DF_linearReg_split_CV["Building 6 kW"],predict_DF_linearReg_split_CV["Power cons Predict_linearReg_CV"])
print "Mean squared error using Cross Validation is :"+str(mean_squared_error_linearReg_CV)
coeff_variation_linearReg_CV = np.sqrt(mean_squared_error_linearReg_CV)/predict_DF_linearReg_split_CV["Building 6 kW"].mean()
print "Coefficient variation using  Linear Regression is :"+str(coeff_variation_linearReg_CV)


from sklearn.ensemble import RandomForestRegressor #Usage of Random Forest Regression
reg_RF=RandomForestRegressor()
predict_RF_CV=cross_val_predict(reg_RF,DF_features,DF_target,cv=10)
predict_DF_RF_CV=pd.DataFrame(predict_RF_CV,index=DF_target.index,columns=["Power cons.Predict_Forest_Regressor"])
predict_DF_RF_CV=predict_DF_RF_CV.join(DF_target)
predict_DF_RF_CV_ChosenDates=predict_DF_RF_CV["2010-08-01":"2010-08-05"]


from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
mean_absolute_error_RF_CV=mean_absolute_error(DF_target,predict_RF_CV)
print "Mean absolute error using RF Regressor  is :"+str(mean_absolute_error_RF_CV)
mean_squared_error_RF_CF=mean_squared_error(DF_target,predict_RF_CV)
print "Mean squared error using RF Regressor is :"+str(mean_squared_error_RF_CF)
r2_error_RF_CF=r2_score(DF_target,predict_RF_CV)
print "R2 error using  RF Regressor is :"+str(r2_error_RF_CF)

