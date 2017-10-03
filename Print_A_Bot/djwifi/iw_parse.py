#! /usr/bin/env python

# Hugo Chargois - 17 jan. 2010 - v.0.1
# Parses the output of iwlist scan into a table

# You can add or change the functions to parse the properties
# of each AP (cell) below. They take one argument, the bunch of text
# describing one cell in iwlist scan and return a property of that cell.

import re
from subprocess import call, Popen, PIPE
from time import sleep

VERSION_RGX = re.compile("version\s+\d+", re.IGNORECASE)


def get_ssid(cell):
    """ Gets the name / essid of a network / cell.
    @param str cell
        A network / cell from iwlist scan.

    @return str
        The name / essid of the network.
    """

    return matching_line(cell, "ESSID:")[1:-1]  # trim off "'s


def get_quality(cell):
    """ Gets the quality of a network / cell.
    @param str cell
        A network / cell from iwlist scan.

    @return str
        The quality of the network.
    """

    quality = matching_line(cell, "Quality=").split()[0].split("/")
    return int(float(quality[0]) / float(quality[1]) * 100)


def get_signal_level(cell):
    """ Gets the signal level of a network / cell.
    @param str cell
        A network / cell from iwlist scan.

    @return string
        The signal level of the network.
    """

    signal = matching_line(cell, "Signal level=").split("=")[1].split("/")
    if len(signal) == 2:
        return str(int(round(float(signal[0]) / float(signal[1]) * 100)))
    elif len(signal) == 1:
        return signal[0]
    else:
        return ""


def get_channel(cell):
    """ Gets the channel of a network / cell.
    @param str cell
        A network / cell from iwlist scan.

    @return string
        The channel of the network.
    """

    channel = matching_line(cell, "Channel:")
    if channel:
        return channel
    frequency = matching_line(cell, "Frequency:")
    channel = re.sub(r".*\(Channel\s(\d{1,2})\).*", r"\1", frequency)
    return channel


def get_encryption(cell):
    """ Gets the encryption type of a network / cell.
    @param str cell
        A network / cell from iwlist scan.

    @return string
        The encryption type of the network.
    """

    if matching_line(cell, "Encryption key:") == "off":
        return "Off"

    enc = "WEP"  # default encryption type
    for line in cell:
        matching = match(line, "IE:")
        if matching is None:
            continue

        wpa = match(matching, "WPA")
        if wpa is None:
            continue

        wpa2 = match(matching, "IEEE 802.11i/WPA2 Version ")
        if wpa2:
            # enc="WPA2 v."+wpa2
            enc = "WPA2"
        else:
            enc = "WPA"
    return enc


def get_is_encrypted(cell):
    if matching_line(cell, "Encryption key:") == "off":
        return False
    return True


def get_address(cell):
    """ Gets the address of a network / cell.
    @param str cell
        A network / cell from iwlist scan.

    @return string
        The address of the network.
    """

    return matching_line(cell, "Address: ")


def get_bit_rates(cell):
    """ Gets the bit rate of a network / cell.
    @param str cell
        A network / cell from iwlist scan.

    @return string
        The bit rate of the network.
    """

    return matching_line(cell, "Bit Rates:")


def sort_cells(cells, sort_by=None):
    """
    Here you can choose the way of sorting the table. sort_by should be a key of
    the dictionary rules.
    """
    if sort_by is None:
        sort_by = "Quality"
    reverse = True
    cells.sort(None, lambda el: el[sort_by], reverse)


# Below here goes the boring stuff. You shouldn't have to edit anything below
# this point

def matching_line(lines, keyword):
    """ Returns the first matching line in a list of lines.
    @see match()
    """
    for line in lines:
        matching = match(line, keyword)
        if matching is not None:
            return matching
    return None


def match(line, keyword):
    """ If the first part of line (modulo blanks) matches keyword,
    returns the end of that line. Otherwise checks if keyword is
    anywhere in the line and returns that section, else returns None"""

    line = line.lstrip()
    length = len(keyword)
    if line[:length] == keyword:
        return line[length:]
    else:
        if keyword in line:
            return line[line.index(keyword):]
        else:
            return None


def parse_cell(cell, rules):
    """
    Applies the rules to the bunch of text describing a cell.

    @return dictionary of parsed networks.
    """
    parsed_cell = {}
    for key in rules:
        rule = rules[key]
        parsed_cell.update({key: rule(cell)})
    return parsed_cell


def print_table(table):
    # Functional black magic.
    widths = map(max, map(lambda l: map(len, l), zip(*table)))

    justified_table = []
    for line in table:
        justified_line = []
        for i, el in enumerate(line):
            justified_line.append(el.ljust(widths[i] + 2))
        justified_table.append(justified_line)

    for line in justified_table:
        for el in line:
            print el,
        print ''


def print_cells(cells, columns):
    table = [columns]
    for cell in cells:
        cell_properties = []
        for column in columns:
            if column == 'Quality':
                # make print nicer
                cell[column] = cell[column].rjust(3) + " %"
            cell_properties.append(cell[column])
        table.append(cell_properties)
    print_table(table)


def get_parsed_cells(iw_data, rules=None, sort_by=None):
    """ Parses iwlist output into a list of networks.
        @param list iw_data
            Output from iwlist scan.
            A list of strings.

        @return list
            properties: Name, Address, Quality, Channel, Encryption.
    """

    # Here's a dictionary of rules that will be applied to the description
    # of each cell. The key will be the name of the column in the table.
    # The value is a function defined above.
    rules = rules or {
        "Name": get_ssid,
        "Quality": get_quality,
        "Channel": get_channel,
        "Encryption": get_encryption,
        "Address": get_address,
        "Signal Level": get_signal_level,
        "Bit Rates": get_bit_rates,
    }

    cells = [[]]
    parsed_cells = []

    for line in iw_data:
        cell_line = match(line, "Cell ")
        if cell_line is not None:
            cells.append([])
            line = cell_line[-27:]
        cells[-1].append(line.rstrip())

    cells = cells[1:]

    for cell in cells:
        parsed_cells.append(parse_cell(cell, rules))

    sort_cells(parsed_cells, sort_by)
    return parsed_cells


def get_djwifi_list(iw_data):
    rules = {
        'essid': get_ssid,
        'quality': get_quality,
        'encryption': get_encryption,
        'encrypted': get_is_encrypted,
        'channel': get_channel,
    }
    return get_parsed_cells(iw_data, rules, 'quality')


def call_iwlist(interface='wlan0'):
    """ Get iwlist output via subprocess
        @param str interface
            interface to scan
            default is wlan0

        @return string
            properties: iwlist output
    """
    p = Popen(['sudo', 'iwlist', interface, 'scanning'],
              stdout=PIPE, stderr=PIPE)
    output = p.stdout.read()
    if output:
        return output
    elif p.stderr.read().count('Network is down'):
        call(['sudo', 'ifconfig', interface, 'up'])
        sleep(2)
        return call_iwlist(interface)


def get_interfaces(interface="wlan0"):
    """ Get parsed iwlist output
        @param str interface
            interface to scan
            default is wlan0

        @param list columns
            default data attributes to return

        @return dict
            properties: dictionary of iwlist attributes
    """
    return get_parsed_cells(call_iwlist(interface).split('\n'))


