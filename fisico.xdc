#Clock
set_property -dict { PACKAGE_PIN R4    IOSTANDARD LVCMOS33 } [get_ports { clk }]; #IO_L13P_T2_MRCC_34 Sch=sysclk
create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports clk]

#Led
set_property -dict { PACKAGE_PIN T14   IOSTANDARD LVCMOS25 } [get_ports { alerta }]; #IO_L15P_T2_DQS_13 Sch=led[0]

#UART
set_property -dict { PACKAGE_PIN V18  IOSTANDARD LVCMOS33 } [get_ports { rx }]; #IO_L15P_T2_DQS_RDWR_B_14 Sch=uart_rx_out
