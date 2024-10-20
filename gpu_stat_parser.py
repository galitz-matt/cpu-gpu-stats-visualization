from parser import *
from datetime import datetime
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import sys

timestamp_pattern = r'udc-an\d{2}-\d{2}\s+[A-Za-z]{3}\s+[A-Za-z]{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2}\s+\d{4}\s+\d+\.\d+\.\d+'
datetime_format = "%a %b %d %H:%M:%S %Y"


def get_path():
	return sys.argv[1]


def parse_timestamp(timestamp):
	components = timestamp.split()[1:-1]
	timestamp_string = " ".join(components)
	return datetime.strptime(timestamp_string, datetime_format)


def get_gpu(gpu_stats):
	return gpu_stats[0]


def get_gpu_percentage(gpu_stats):
	return int(gpu_stats[1].split()[1].strip('%').strip())


def get_gpu_memory(gpu_stats):
	return int(gpu_stats[2].split('/')[0].strip())


def get_plot_data(data):
	percent_data = defaultdict(list)
	memory_data = defaultdict(list)
	timestamps = []
	for timestamp, processes in data:
		timestamp = parse_timestamp(timestamp)
		timestamps.append(timestamp)
		for gpu_stats in processes:
			gpu = get_gpu(gpu_stats)
			percentage = get_gpu_percentage(gpu_stats)
			memory = get_gpu_memory(gpu_stats)
			percent_data[gpu].append((timestamp, percentage))
			memory_data[gpu].append((timestamp, memory))
	percent_df_dict = {gpu: pd.DataFrame(data, columns=['timestamp', '%GPU']).set_index('timestamp') for gpu, data in percent_data.items()}
	memory_df_dict = {gpu: pd.DataFrame(data, columns=['timestamp', 'MB']).set_index('timestamp') for gpu, data in memory_data.items()}
	return percent_df_dict, memory_df_dict


def plot_helper():
	plt.gca().xaxis.set_major_locator(mdates.SecondLocator(interval=45))
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
	plt.xticks(rotation=30)
	plt.xlabel('Time')
	plt.legend()
	plt.grid(True)


def plot(percent_df_dict, memory_df_dict):
	plt.figure(figsize=(15, 9))
	for gpu, df in percent_df_dict.items():
		plt.plot(df.index, df['%GPU'], label=f'{gpu}')
	plt.title('%GPU Usage Over Time')
	plt.ylabel('%GPU')
	plot_helper()
	plt.savefig('%GPU_TIME.png')
	plt.show()

	plt.figure(figsize=(15, 9))
	for gpu, df in memory_df_dict.items():
		plt.plot(df.index, df['MB'], label=f'{gpu}')
	plt.title('MB Usage Over Time')
	plt.ylabel('MB')
	plot_helper()
	plt.savefig('MB_TIME.png')
	plt.show()


if __name__ == '__main__':
	path = get_path()
	data = extract_data(path, timestamp_pattern)
	block_list = create_block_list(data)
	parsed_list = parse_block_list(block_list, delim='|')
	percent_df_dict, memory_df_dict = get_plot_data(parsed_list)
	plot(percent_df_dict, memory_df_dict)