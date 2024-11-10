[labels,x,y] = readColData('Rank_6_7_2019_16_42.txt', 5, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'ICA---ICA','FWA---FWA20','GA---GA20o','SA---SAR'})
xlabel('rank')
