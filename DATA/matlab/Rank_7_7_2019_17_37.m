[labels,x,y] = readColData('Rank_7_7_2019_17_37.txt', 7, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'a','b','c','MINn','d','g'})
xlabel('rank')
