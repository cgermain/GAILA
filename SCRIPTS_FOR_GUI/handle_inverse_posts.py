
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
  return str_mat


def get_header_for_reporterType(r_t):
  if r_t == 'TMT0':
    return ['126']
  elif r_t == 'TMT2':
    return ['126','127']
  elif r_t == 'TMT6':
    return ['126','127','128','129','130','131']
  elif r_t == 'TMT6OLD':
    return ['126','127','128','129','130','131']
  elif r_t == 'TMT10':
    return ['126','127N','127C','128N','128C','129N','129C','130N','130C','131']
  elif r_t == 'TMT11':
    return ['126','127N','127C','128N','128C','129N','129C','130N','130C','131', '131C']
  elif r_t == 'iTRAQ4':
    return ['114','115','116','117']
  elif r_t == 'iTRAQ8':
    return ['113','114','115','116','117','118','119','121']
  else:
    raise Exception("For some reason header does not match any known type. That is bad.")


def create_inverse_given_header_and_data(header, data):
  # header = ['126','127N','127C','128N','128C','129N','129C','130N','130C','131', '131C']
  matrix = []
  normalization_array = []
  for head in header:
    norm = 0.0
    head_data = data[head]
    to_append = []
    for head2 in header:
      # if head == head2:
      #   norm += 100.0
      #   to_append.append(100.0)
      #   continue
      if head2 in head_data:
        datum = head_data[head2]
        norm += datum
        to_append.append(datum)
      else:
        to_append.append(0.0)
    if 'other' in head_data:
      norm += head_data['other']
    matrix.append(to_append)
    normalization_array.append([norm])
  
  norm_np = np.asarray(normalization_array)
  matrix_np = np.asarray(matrix)
  matrix_norm = matrix_np / norm_np
  norm_mat_inv = np.linalg.inv(matrix_norm)
  inverse_str = inverse_to_txt(header, norm_mat_inv)
  return inverse_str


def create_inverse_file(post_obj):
  reporterType = post_obj['reporterType']
  data = post_obj['data']
  timestamp = post_obj['timestamp']
  lot_details = post_obj['lot_details']
  if lot_details == "":
    lot_details = timestamp
  else:
    lot_details = lot_details.replace(" ", "_")
  header = get_header_for_reporterType(reporterType)
  inverse_string = create_inverse_given_header_and_data(header, data)
  this_dir = os.path.dirname(os.path.realpath(__file__))
  inv_path = os.path.join(this_dir, "inverse_files",reporterType+"_"+lot_details+"-inv.txt")
  with open(inv_path, 'w+') as out_file:
    out_file.write(inverse_string)
  return inv_path