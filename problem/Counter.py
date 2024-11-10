# coding=UTF-8

class Counter(object):

  """  
  :version:
  :author:
  """

  """ ATTRIBUTES

   

  count  (public)

   

  limit  (public)

  """

  def __init__(self, limit):
    """
     

    @param int limit : 
    @return  :
    @author
    """
    self.limit = limit
    self.count = 0

  def getCount(self):
    """
     

    @return int :
    @author
    """
    return self.count 

  def setCount(self, count):
    """
     

    @param int count : 
    @return  :
    @author
    """
    self.count = count

  def getLimit(self):
    """
     

    @return int :
    @author
    """
    return self.limit 

  def setLimit(self, limit):
    """
     

    @param int limit : 
    @return  :
    @author
    """
    self.limit = limit



  def incCount(self, u=1):
    """
    @return  :
    @author
    """
    self.count = self.count+u

