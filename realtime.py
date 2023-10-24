from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowOperations, DetrendOperations

import serial.tools.list_ports
import time

def get_alpha_beta(board, board_id):
    data = board.get_board_data()

    eeg_channels = BoardShim.get_eeg_channels(board_id)
    eeg_channel = eeg_channels[1]
    sampling_rate = BoardShim.get_sampling_rate(board_id)
    nfft = DataFilter.get_nearest_power_of_two(sampling_rate)
    DataFilter.detrend(data[eeg_channel], DetrendOperations.LINEAR.value)
    psd = DataFilter.get_psd_welch(data[eeg_channel], nfft, nfft // 2, sampling_rate, WindowOperations.HANNING.value)

    # calc band power
    alpha = DataFilter.get_band_power(psd, 7.0, 13.0)
    beta = DataFilter.get_band_power(psd, 14.0, 30.0)

    print(alpha / beta)

def main():
    # setup
    board_id = BoardIds.SYNTHETIC_BOARD
    params = BrainFlowInputParams()

    # ports = serial.tools.list_ports.comports()
    # print("---PORTS---")
    # for port, desc, hwid in sorted(ports):
    #     print(f"{port}: {desc} [{hwid}]")
    # params.serial_port = ""

    # create a board
    board = BoardShim(board_id, params)

    board.prepare_session()
    board.start_stream()

    # retrive data
    try:
        while True:
            time.sleep(5)
            get_alpha_beta(board, board_id)
    finally:
        if board.is_prepared():
            board.release_session()

if __name__ == "__main__":
    main()