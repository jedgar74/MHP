[labels,x,y] = readColData('RankTop_6_7_2019_18_32.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'d','c','b'})
xlabel('rank')
