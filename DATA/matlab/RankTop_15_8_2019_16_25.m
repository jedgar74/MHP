[labels,x,y] = readColData('RankTop_15_8_2019_16_25.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'a','b','d'})
xlabel('rank')
