[labels,x,y] = readColData('Rank_15_8_2019_16_25.txt', 6, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'a','b','d','e','c'})
xlabel('rank')
