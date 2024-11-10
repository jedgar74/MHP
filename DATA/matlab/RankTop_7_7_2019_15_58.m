[labels,x,y] = readColData('RankTop_7_7_2019_15_58.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'a','b','c'})
xlabel('rank')
