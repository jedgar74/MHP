[labels,x,y] = readColData('RankTop_17_7_2019_10_42.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'a','b','c'})
xlabel('rank')
