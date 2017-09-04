from scipy.stats import norm
import sys
import os
import pandas as pd
import numpy as np
from scipy import optimize

dflines = pd.read_csv("underover.csv")
df = pd.read_csv("schedule.csv")
col1 = "\xef\xbb\xbfAway"
col2 = "Home"
teams = list(dflines["Team"])

df['aidx'] = df[col1].apply(lambda x: teams.index(x))
df['hidx'] = df[col2].apply(lambda x: teams.index(x))

n_teams = 32
home_edge = 3

def rtg_constr(x):
    return np.mean(x)

def obj(x):
	err = 0
	df['proj'] = 3+df.hidx.apply(lambda i: x[i]) - df.aidx.apply(lambda i: x[i])
	df['hwinpr']=1 - norm.cdf(0.5,df['proj'],14.5)
	df['awinpr'] = 1-df['hwinpr']
	w = np.zeros(shape=n_teams)
	for i in range(len(df)):
		w[teams.index(df[col1][i])] = w[teams.index(df[col1][i])] + df['awinpr'][i]
		w[teams.index(df[col2][i])] = w[teams.index(df[col2][i])] + df['hwinpr'][i]
	err = ((dflines["Line"]-w)**2).sum()
	return err

x0 = np.zeros(shape=n_teams)

res = optimize.minimize(obj,x0, constraints=[{'type':'eq', 'fun':rtg_constr}], method="SLSQP",
                        options={'maxiter':10000})


df['proj'] = 3+df.hidx.apply(lambda i: res.x[i]) - df.aidx.apply(lambda i: res.x[i])
df['hwinpr']=1 - norm.cdf(0.5,df['proj'],14.5)
df['awinpr'] = 1-df['hwinpr']
w = np.zeros(shape=n_teams)
for i in range(len(df)):
	w[teams.index(df[col1][i])] = w[teams.index(df[col1][i])] + df['awinpr'][i]
        w[teams.index(df[col2][i])] = w[teams.index(df[col2][i])] + df['hwinpr'][i]
print res.success, res.message
print("                Team   Rating   Line   ExpWins")
for i, t in enumerate(dflines["Team"]):
    print("{:>20s}    {:.4f}    {:.4f}    {:.4f}".format(t, res.x[i],dflines["Line"][i],w[i]))

print("Home	Away	HomeWinProb	AwayWinProb")

for i in range(len(df)):
	print df[col2][i],"\t",df[col1][i],"\t",df['hwinpr'][i],"\t",df['awinpr'][i]
