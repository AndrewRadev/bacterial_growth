import os
import pandas as pd
from datetime import date

def isDir(string):
    '''
    This function checks if the given string is a directory path

    :param string
    :return string (if ok)
    '''
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def isFile(path):
    '''
    This function checks if the given string is a directory path

    :param path
    :return string (if ok)
    '''
    # if os.path.isfile(string):
    #     return string
    # else:
    #     raise FileNotFoundError(string)
    import argparse
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"{path} is not a valid file.")
    return path



def getZipName(dir_path):
    '''
    This function calculates the name of the new zip file depending on the already existing ones

    :param dir_path
    :return new_zip name
    '''
    today = date.today()
    res = []

    for path in os.listdir(dir_path):
        if 'zip' in path and 'Results' in path: res.append(path)

    if len(res) == 0:
        new_zip = 'Results_'+str(today)+'_0.zip'
    else:
        sorted_res = sorted(res)
        old_zip = sorted_res[-1]

        if old_zip[8:18] == str(today):
            new_zip = old_zip[:-5]+str(int(old_zip[-5])+1)+old_zip[-4:]
        else:
            new_zip = 'Results_'+str(today)+'_0.zip'

    return new_zip

def findOccurrences(string, ch):
    '''
    This function returns a list with all the positions of the string that contain the character ch

    :param string
    :param ch: character to look for
    :return list with positions
    '''
    return [i for i, letter in enumerate(string) if letter == ch]

def transformStringIntoList(string, ch):
    '''
    Gets a tring with values separated by ch and places them into a list

    :param stirng
    :param ch: separating character
    '''
    positions = findOccurrences(string, ch)
    list = []
    start = 0
    for i, pos in enumerate(positions):
        end = pos
        elem = string[start:end]
        list.append(elem)

        start = end + 1
        if string[start] == ' ':
            start = end + 2

    elem = string[start:]
    list.append(elem)

    return list

def getMatchingList (regex, lst):
    '''
    This function takes a regex expression and returns a list with all the matching words in the given lst

    :param regex
    :param lst
    :return res: list with matching elements
    '''
    res = []
    for word in lst:
        if regex.findall(word):
            res.append(word)
    return res

def saveFile(data, path):
    '''
    Saves the data into the indicated path

    :param data
    :param path
    '''
    if len(data.columns) > 1:
        data.to_csv(path, sep=" ", index=False)


def getIntersectionColumns(df, columns):
    '''
    This function returns a new df formed only by the indicated columns

    :param df
    :param columns to keep
    :return res new df
    '''
    res = df[df.columns.intersection(columns)]
    return res

def getMeanStd(files, regex=''):
    '''
    This function gets a set of files and the columns (regex or all columns) in which mean and std are going to be calculated
    For each header, a tmp df is created with the data from all the files. Then mean and std are calulcated and placed in a final df.

    :param fies
    :param regex
    :return msd: df with column 0 (time) and alternating columns with mean and std for all the headers
    '''
    df = pd.read_csv(files[0][0], sep=" ")

    if regex != '':
        headers = getMatchingList(regex, df)
    else:
        headers = df.columns

    msd = pd.DataFrame(columns=range(1))
    msd.set_axis(['time'], axis='columns', inplace=True)
    msd['time'] = df['time']

    for header in headers:
        if header != 'time':
            df_header = pd.DataFrame(columns=range(len(files)+1)) #Each column will be the value from each file

            # Fill the df parsing all the records' files
            for i, file in enumerate(files, 1):
                file_df = pd.read_csv(file[0], sep=" ")
                df_header.iloc[:,i] = file_df[header]

            # Calculate and keep mean and std
            msd_header = pd.DataFrame(columns=range(3))
            msd_header.set_axis(['time', header+'_mean', header+'_std'], axis='columns', inplace=True)
            msd_header['time'] = file_df['time']
            msd_header[header+'_mean'] = df_header.iloc[:,1:].mean(axis=1, numeric_only=True)
            msd_header[header+'_std'] = df_header.iloc[:,1:].std(axis=1, numeric_only=True)

            msd = pd.merge(msd, msd_header, on='time')

    return msd
