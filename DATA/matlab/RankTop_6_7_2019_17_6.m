[labels,x,y] = readColData('RankTop_6_7_2019_17_6.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'ICA---ICA','GA---GA20o','FWA---FWA20'})
xlabel('rank')
