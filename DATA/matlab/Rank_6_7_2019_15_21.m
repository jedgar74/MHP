[labels,x,y] = readColData('Rank_6_7_2019_15_21.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'FWA---FWA20','GA---GA20o','SA---SAR'})
xlabel('rank')
