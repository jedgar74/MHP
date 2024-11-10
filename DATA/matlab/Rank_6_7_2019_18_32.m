[labels,x,y] = readColData('Rank_6_7_2019_18_32.txt', 7, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'d','c','b','MINa','g','MINn'})
xlabel('rank')
