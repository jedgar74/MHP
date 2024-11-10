[labels,x,y] = readColData('RankTop_6_7_2019_16_42.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'ICA---ICA','FWA---FWA20','GA---GA20o'})
xlabel('rank')
