[labels,x,y] = readColData('Rank_17_7_2019_11_3.txt', 7, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'a','b','c','MINn','d','g'})
xlabel('rank')
