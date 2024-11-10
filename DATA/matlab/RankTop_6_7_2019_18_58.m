[labels,x,y] = readColData('RankTop_6_7_2019_18_58.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'MINa','b','c'})
xlabel('rank')
