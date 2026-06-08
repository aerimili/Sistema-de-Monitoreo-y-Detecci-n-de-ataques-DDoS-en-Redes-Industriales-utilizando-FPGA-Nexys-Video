set_property -dict { PACKAGE_PIN R4    IOSTANDARD LVCMOS33 } [get_ports { clk }]; 
create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports clk]
set_property -dict { PACKAGE_PIN T14   IOSTANDARD LVCMOS25 } [get_ports { led_alerta }]; 
set_property -dict { PACKAGE_PIN Y13   IOSTANDARD LVCMOS25 } [get_ports { led_uart }]; 
set_property -dict { PACKAGE_PIN V18   IOSTANDARD LVCMOS33 } [get_ports { rx }]; 
set_property -dict { PACKAGE_PIN AA19  IOSTANDARD LVCMOS33 } [get_ports { tx }];
set_property -dict { PACKAGE_PIN B22 IOSTANDARD LVCMOS12 } [get_ports { btn_reset }];