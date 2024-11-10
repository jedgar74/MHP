[labels,x,y] = readColData('RankTop_17_7_2019_9_53.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'a','b','c'})
xlabel('rank')
