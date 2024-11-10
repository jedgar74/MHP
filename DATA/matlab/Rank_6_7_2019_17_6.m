[labels,x,y] = readColData('Rank_6_7_2019_17_6.txt', 5, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'ICA---ICA','FWA---FWA20','GA---GA20o','SA---SAR'})
xlabel('rank')
