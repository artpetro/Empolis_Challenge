'''
Created on 1.12.2021

@author: Artem_Petrov
'''

import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import argparse


def compute_mean_std(data):
    '''
    Calculates mean and standard deviation of given data set
    
    @param data: array with values
    @return: mean and standard deviation 
    '''
    
    return np.mean(data), np.std(data)


def get_indices_from_windows_idx(windows_indices, window_size):
    '''
    Constructs an array of indices of data points located in the corresponding sliding windows
    
    @param windows_indices: array with indices of sliding windows to be concatenated
    @param window_size: size of sliding window
    @return: an array with indices of data points 
    '''
    
    ranges = list(map(lambda idx: np.array(range(idx, idx+window_size)), windows_indices))
    indices = np.unique(np.concatenate(ranges))
    
    return indices


def show_plots(input_data, mean, std, rules):
    '''
    Show plots
    
    @param data: data points
    @param mean: mean of data
    @param std: standard deviation
    @param rules: array with rules 
    '''
    
    for rule in rules:
        plot_data(input_data, mean, std, rule)
    

def plot_data(data, mean, std, indices):
    '''
    Plot data points. The points that meets the rule are red
    
    @param data: data points
    @param mean: mean of data
    @param std: standard deviation
    @param indices: indices of points that meets the rule
    '''
    
    colors = np.full((len(data)), 'b')
    colors[indices] = 'r'
    
    plt.scatter(data[:, 0], data[:, 1], c=colors, s=2)
    
    plt.axhline(mean, color='black', linestyle='dotted')
    plt.axhline(mean + std, color='purple', linestyle='dotted')
    plt.axhline(mean - std, color='purple', linestyle='dotted')
    plt.axhline(mean + 2*std, color='purple', linestyle='dotted')
    plt.axhline(mean - 2*std, color='purple', linestyle='dotted')
    plt.axhline(mean + 3*std, color='purple', linestyle='dotted')
    plt.axhline(mean - 3*std, color='purple', linestyle='dotted')
    
    plt.show()


def nelson_rule_1(data, mean, std):
    '''
    Checks if points satisfy the Nelson's rule 1: Out of 3 sigma: One point is more than 3 standard deviations from 
    the mean
    
    @param data: array of data points
    @param mean: mean of data
    @param std: standard deviation
    @return: an array of point indices that satisfy the rule
    '''
    
    (indices, ) = np.nonzero((abs(data - mean) > 3*std))
    
    return indices


def nelson_rule_2(data, mean):
    '''
    Checks if points satisfy the Nelson's rule 2: Bias: Nine (or more) points in a row are on the same side of the mean
    
    @param data: array of data points
    @param mean: mean of data
    @return: an array of point indices that satisfy the rule
    '''
    
    n = 9
    # first, we build the difference between mean and all the values
    # for each result we compute its sign, the sign is -1 (value is less as mean), 0 (value and mean are equal),
    # or 1 (value is greater as mean)
    signs = np.sign(data - mean).astype(np.int8)
    # we make a sliding window of size 6
    sliding_win = sliding_window_view(signs, n)
    
    # than we add all values in each sliding window
    consecutive = np.sum(sliding_win, axis=-1)

    # if all values in window are same and not 0, than all corresponding data points are above or under the mean
    # the abs of sum of signs and the size of window must be equal
    # now, we filter only such windows and get indices of this windows
    # the window index is the same as the index of start data point 
    (windows_indices, ) = np.nonzero(np.abs(consecutive)==n)
    
    # now we get indices of data points, that are in the windows
    indices = get_indices_from_windows_idx(windows_indices, n)
    
    return indices


def nelson_rule_3(data):
    '''
    Checks if points satisfy the Nelson's rule 3: Trend: Six (or more) points in a row are continually increasing 
    (or decreasing)
    
    @param data: array of data points
    @return: an array of point indices that satisfy the rule
    '''
    
    n = 6
    # first, we build a difference between each two consecutive points in our data set
    # and make a signs of those differences
    # we get -1 (point_1 < point_2), 0 (point_1 = point_2) or 1 (point_1 > point_2)
    signs = np.sign(np.diff(data)).astype(np.int8)
    
    # we run a sliding window of size 6 over the signs array
    sliding_win = sliding_window_view(signs, n)
    
    # in each window we build a sum of all values
    consecutive = np.sum(sliding_win, axis=-1)

    # when we have a trend, then all signs in one window must be equal and the sum of signs must be the same 
    # as the size of window
    (windows_indices, ) = np.nonzero(np.abs(consecutive)==n)
    
    # now we get indices of data points, that are in the windows
    indices = get_indices_from_windows_idx(windows_indices, n)
    
    return indices


def nelson_rule_4(data):
    '''
    Checks if points satisfy the Nelson's rule 4: Alternating: Fourteen (or more) points in a row alternate in direction, 
    increasing then decreasing
    
    @param data: array of data points
    @return: an array of point indices that satisfy the rule
    '''
    
    n = 14
    # first, we build a difference between each two consecutive points in our data set
    # and make a signs of those differences
    # we get -1 (point_1 < point_2), 0 (point_1 = point_2) or 1 (point_1 > point_2)
    signs = np.sign(np.diff(data)).astype(np.int8)
    
    # we run a sliding window of size 14 over the signs array
    sliding_win = sliding_window_view(signs, n)
    
    # we check each window if it contains alternating values, e.g. -1, 1, -1, 1....
    # we filter such windows and get the indices of this windows
    (windows_indices, ) = np.nonzero(list(map(lambda i: True if check_toggle(sliding_win[i]) else False, range(len(sliding_win)))))
            
    # now we get indices of data points, that are in the windows
    indices = get_indices_from_windows_idx(windows_indices, n)
    
    return indices



def check_toggle(signs):
    '''
    Checks if an array contains alternating values
    
    @param signs: array with signs, contains -1 and 1 
    (and 0, but this case occurs if the values array contains two equal values) 
    @return: True if all values of array are alternating
    '''
    
    n = 2
    
    # we run a sliding window of size 2 other all values
    # then we sum both values in each window
    # if all the values are alternating, then all the sums must be zero
    sliding_win = sliding_window_view(signs, n)
    consecutive = np.sum(sliding_win, axis=-1)

    return np.count_nonzero(consecutive) == 0


def write_result(timestamps, rules, output_data_path):
    '''
    Write results into csv file in defined format
    
    @param timestamps: time stamps
    @param rules: list of numpy arrays with activated rules
    @param output_data_path: path to output file   
    '''
    
    # while reading timestamps are floats, so we convert it back to int and finaly to string
    timestamps = timestamps.astype('int').astype('str')
    
    rules_res = []
    
    # create arrays with rule's numbers
    for idx in range(len(rules)):
        rule_res = np.empty(len(timestamps), dtype='str')
        rule_res[rules[idx]] = idx + 1
        rules_res.append(rule_res)
    
    # join all rules (string wise) to one array
    # each element of resulting array contains a string with numbers of activated rules, e.g. "123"
    rules_res_mat = np.core.defchararray.add(rules_res[0], rules_res[1])
    rules_res_mat = np.core.defchararray.add(rules_res_mat, rules_res[2])
    rules_res_mat = np.core.defchararray.add(rules_res_mat, rules_res[3])
    
    # perform some formatting ';' between rule's numbers
    rules_joined = list(map(lambda rule: ';'.join(rule), rules_res_mat))
    # concatenate time stamp and activated rules
    result = np.array(list(map(lambda timestamp, rule: ','.join(filter(None, [timestamp, rule])), timestamps, rules_joined)))
    
    # save to file
    np.savetxt(output_data_path, result, fmt='%s', comments='', header='timestamp,rules')


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Apply the Nelson\'s rules to data set.')
    parser.add_argument('-i', '--input_file', type=str, help='input file', required=True)
    parser.add_argument('-o', '--output_file', type=str, help='output file', required=True)
    parser.add_argument('-p', '--plot_data', help='show plots')
    
    args = parser.parse_args()
    
    input_data_path = args.input_file
    output_data_path = args.output_file
    plot = args.plot_data
    
    input_data = np.genfromtxt(input_data_path, delimiter=',', skip_header=1)
    
    sensor_values = input_data[:, 1]
    
    mean, std = compute_mean_std(sensor_values[:100])
    
    # check rules
    rules = []
    rules.append(nelson_rule_1(sensor_values, mean, std))
    rules.append(nelson_rule_2(sensor_values, mean))
    rules.append(nelson_rule_3(sensor_values))
    rules.append(nelson_rule_4(sensor_values))
    
    
    if plot:
        show_plots(input_data, mean, std, rules)
    
    write_result(input_data[:, 0], rules, output_data_path)

