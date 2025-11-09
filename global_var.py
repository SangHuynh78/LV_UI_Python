# globals.py

# Dữ liệu laser manual
manual_laser_percent = 0

# Dữ liệu nhiệt độ 8 NTC
# Mỗi phần tử là danh sách chứa lịch sử nhiệt độ
ntc_temp = [[] for _ in range(8)]

# Temperature variable
temp_tec_voltage = 0
temp_heater_duty = 0
temp_target = 0
temp_limit_min = 0
temp_limit_max = 0
temp_ntc_pri_ref = 0
temp_ntc_sec_ref = 0
temp_auto_state = 0

# Experiment variable
exp_sampling_rate = 0
exp_pos = 0
exp_laser_percent = 0
exp_pre_time = 0
exp_experiment_time = 0
exp_post_time = 0
