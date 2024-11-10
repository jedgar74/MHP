[labels,x,y] = readColData('Rank_7_7_2019_16_6.txt', 7, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'a','b','c','MINn','d','g'})
xlabel('rank')
