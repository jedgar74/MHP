[labels,x,y] = readColData('Rank_6_7_2019_18_58.txt', 7, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'MINa','b','c','MINn','d','g'})
xlabel('rank')
