from datetime import datetime
from collections import defaultdict
from parser import *

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import sys

timestamp_pattern = r'\w{3} \w{3} \d{2} \d{2}:\d{2}:\d{2} \w{3} \d{4}'
datetime_format = '%a %b %d %H:%M:%S %Y'


def get_path():
	return sys.argv[1]


def convert_res(res):
	if 'g' in res.lower():
		return float(res.lower().replace('g', '')) * 1024
	if 'm' in res.lower():
		return float(res.lower().replace('m', ''))
	else:
		return float(res)


def parse_timestamp(timestamp):
	components = timestamp.split()
	timestamp_no_timezone = " ".join(components[:4]) + " " + components[5]
	return datetime.strptime(timestamp_no_timezone, datetime_format)


def get_plot_data(data):
	cpu_data = defaultdict(list)
	res_data = defaultdict(list)
	timestamps = []
	for timestamp, processes in data:
		timestamp = parse_timestamp(timestamp)
		timestamps.append(timestamp)
		for process in processes:
			pid = process['PID']
			cpu = float(process['%CPU'])
			res = convert_res(process['RES'])
			cpu_data[pid].append((timestamp, cpu))
			res_data[pid].append((timestamp, res))
	cpu_df_dict = {pid: pd.DataFrame(data, columns=['timestamp', '%CPU']).set_index('timestamp') for pid, data in cpu_data.items()}
	res_df_dict = {pid: pd.DataFrame(data, columns=['timestamp', 'RES']).set_index('timestamp') for pid, data in res_data.items()}
	return cpu_df_dict, res_df_dict


def plot_helper():
	plt.gca().xaxis.set_major_locator(mdates.SecondLocator(interval=45))
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
	plt.xticks(rotation=30)
	plt.xlabel('Time')
	plt.legend()
	plt.grid(True)


def plot(cpu_df_dict, res_df_dict):
	plt.figure(figsize=(15, 9))
	for pid, df in cpu_df_dict.items():
		plt.plot(df.index, df['%CPU'], label=f'PID {pid}')
	plt.title('%CPU Usage Over Time')
	plt.ylabel('%CPU')
	plot_helper()
	plt.savefig("%CPU_TIME.png")
	plt.show()

	plt.figure(figsize=(15, 9))
	for pid, df in res_df_dict.items():
		plt.plot(df.index, df['RES'], label=f'PID {pid}')
	plt.title('Resident Memory (RES) Usage Over Time')
	plt.ylabel('RES (MB)')
	plt.ylim(0, 3000)
	plot_helper()
	plt.savefig("RES_TIME.png")
	plt.show()


if __name__ == '__main__':
	path = get_path()
	data = extract_data(path, timestamp_pattern)
	block_list = create_block_list(data)
	parsed_list = parse_block_list(block_list, header=True)
	cpu_df_dict, res_df_dict = get_plot_data(parsed_list)
	plot(cpu_df_dict, res_df_dict)