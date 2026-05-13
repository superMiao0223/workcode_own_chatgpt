import pandas as pd

mylist = ['abm4226h','p7d8cz7h','7deqr5sd','eg2o337x','x3b84vy7','37mrtiic','lh96i82y','m8hc5p7s','4k6rejn4','xk5nvxdd',
          'xoxygrqj','wp81a63k','ilgjd03w','aqgrugtz','nwf0lw1b','j9hrgujf']
df = pd.DataFrame(mylist)
print(df)
df.to_csv('shushu.csv',index=False,header=False)