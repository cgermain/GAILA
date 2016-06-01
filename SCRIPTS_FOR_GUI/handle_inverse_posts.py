
"""
The file where you handle posts to the inverse.
All methods will return a text repesentation of an inverse file.
They will be routed by the reporterType attribute of the JSON.
They will be processed by unique methods for each, because they're
different. Maybe I can generalize based on a HEADER array.
"""

from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import sys, os, shutil


def inverse_to_txt(headers, inv_mat):
  print headers
  print inv_mat
  str_mat = ""
  for head in headers:
    str_mat += '\t'
    str_mat += head
  str_mat += '\n'
  # print str_mat
  for i in range(len(headers)):
    str_mat += headers[i]
    for j in range(len(headers)):
      str_mat += '\t'
      str_mat += str(inv_mat[i][j])
    str_mat += '\n'
    # print str_mat
  print '\n\n\n\n'
  print str_mat
  print '\n\n\n\n'
  return str_mat








def is_function(var):
  return hasattr(var, '__call__')

def create_inverse_file(post_obj):
  function_map = {
    'TMT10' : create_TMT10_inverse
  }

  reporterType = post_obj['reporterType']
  print 'type: ' + str(reporterType)
  data = post_obj['data']
  print 'data: '
  print post_obj['data']
  inverse_func = function_map[reporterType]
  if not is_function(inverse_func):
    print 'nothing here'
    return "Haven't written conversion yet."
  else:
    print 'something here.'
    inverse_string = inverse_func(data)
    return inverse_string




def create_TMT10_inverse(data):
  print 'create_TMT10_inverse called'
  HEADER = ['126','127N','127C','128N','128C','129N','129C','130N','130C','131']
  matrix = []
  normalization_array = []
  for head in HEADER:
    norm = 0.0
    print head
    head_data = data[head]
    to_append = []
    for head2 in HEADER:
      if head == head2:
        norm += 100.0
        to_append.append(100.0)
        continue
      if head2 in head_data:
        datum = head_data[head2]
        norm += datum
        to_append.append(datum)
      else:
        to_append.append(0.0)
    # Now for the 'other' ones
    # to_append.append(head_data['other'])
    if 'other' in head_data:
      norm += head_data['other']
    matrix.append(to_append)
    normalization_array.append([norm])
  
  # print normalization_array
  norm_np = np.asarray(normalization_array)
  matrix_np = np.asarray(matrix)
  # print matrix_np
  # print norm_np
  matrix_norm = matrix_np / norm_np
  print 'normalized: '
  # print matrix_norm
  norm_mat_inv = np.linalg.inv(matrix_norm)
  print 'norm inv: '
  # print norm_mat_inv
  # print matrix
  print 'done'
  inverse_str = inverse_to_txt(HEADER, norm_mat_inv)
  return inverse_str





