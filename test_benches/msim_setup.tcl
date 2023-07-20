#run vsim -c -do <file_name>
# Compile the files
vlog -reportprogress 300 -work work /home/marcanthony/Research/hardware_space_exploration/hardware_modules/basic_blocks/*.sv
vlog -reportprogress 300 -work work /home/marcanthony/Research/hardware_space_exploration/generated_files/verilog/*.sv
vlog -reportprogress 300 -work work /home/marcanthony/Research/hardware_space_exploration/test_benches/*.sv
# Run the simulation
vsim -voptargs=+acc work.top_module_tb

# add wave -position insertpoint sim:/adder_tb/*
# add wave -position insertpoint sim:/adder_tb/dut/*

run -all
