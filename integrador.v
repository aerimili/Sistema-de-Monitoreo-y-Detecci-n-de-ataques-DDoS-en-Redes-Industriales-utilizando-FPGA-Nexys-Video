`timescale 1ns / 1ps

module integrador(
    input clk,
    input rx,
    output alerta
);

wire [7:0] data;
wire data_valid;

wire [15:0] C1, C2, C3;
wire [15:0] C1n, C2n, C3n, th_parser;

wire [15:0] valor_nahid;

wire vector_ready;

// UART
conexionUART uart (
    .clk(clk),
    .rx(rx),
    .data(data),
    .data_valid(data_valid)
);

// Parser
parser parse (
    .clk(clk),
    .data(data),
    .data_valid(data_valid),
    .C1(C1), .C2(C2), .C3(C3),
    .C1n(C1n), .C2n(C2n), .C3n(C3n),
    .th(th_parser),
    .vector_ready(vector_ready)
);

// TH automático
wire [15:0] th_auto;
wire th_listo;

th_calculator th_block (
    .clk(clk),
    .valor_nahid(valor_nahid),
    .valid(vector_ready),
    .th(th_auto),
    .listo(th_listo)
);

// NaHiD
nahid detector (
    .C1(C1), .C2(C2), .C3(C3),
    .C1n(C1n), .C2n(C2n), .C3n(C3n),
    .th(th_auto),
    .valor_nahid(valor_nahid),
    .alerta(alerta)
);

// ILA
ila_0 ila_inst (
    .clk(clk),
    .probe0(C1),
    .probe1(C2),
    .probe2(C3),
    .probe3(valor_nahid),
    .probe4(alerta),
    .probe5(data),
    .probe6(data_valid),
    .probe7(rx),
    .probe8(vector_ready),
    .probe9(th_auto),
    .probe10(th_listo)
);

endmodule