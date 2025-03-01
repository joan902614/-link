def analog:
    V = I * R
    P = I * V
def digit:
    spi
def spi:
    master_count == 1
    slave_count >= 1
    master_CS_count >= slave_count
    master_mode == slave_mode
    master_bit == slave_bit
    master_first == slave_first
    slave_f_min <= master_f_SCK <= slave_f_max 
    # SPI CS（Chip Select）時序
    master_CS_low_time >= tramsmit_time(L / master_f_SCK)
    # 準備時間
    setup_time + hold_time < 1/sck


