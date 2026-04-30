`timescale 1ns / 1ps

module nahid(
    input [15:0] C1, C2, C3,
    input [15:0] C1n, C2n, C3n,
    input [15:0] th,

    output [15:0] valor_nahid,
    output alerta
);

wire [15:0] meanX = (C1 + C2 + C3) / 3;
wire [15:0] meanY = (C1n + C2n + C3n) / 3;

// desviaciones correctas
wire [15:0] devX1 = (C1 > meanX) ? (C1 - meanX):(meanX - C1);
wire [15:0] devX2 = (C2 > meanX) ? (C2 - meanX):(meanX - C2);
wire [15:0] devX3 = (C3 > meanX) ? (C3 - meanX):(meanX - C3);

wire [15:0] stdX = (devX1 + devX2 + devX3) /3;

wire [15:0] devY1 = (C1n > meanY) ? (C1n - meanY):(meanY - C1n);
wire [15:0] devY2 = (C2n > meanY) ? (C2n - meanY):(meanY - C2n);
wire [15:0] devY3 = (C3n > meanY) ? (C3n - meanY):(meanY - C3n);

wire [15:0] stdY = (devY1 + devY2 + devY3) /3;

function [15:0] Di;
    input [15:0] a, b;
    begin Di = (a > b) ? (a - b) : (b - a);
    end
endfunction

wire [15:0] num1 = Di(C1, C1n);
wire [15:0] num2 = Di(C2, C2n);
wire [15:0] num3 = Di(C3, C3n);

wire [15:0] den1 = Di(meanX - stdX, C1) + Di(meanY - stdY, C1n) + 1;
wire [15:0] den2 = Di(meanX - stdX, C2) + Di(meanY - stdY, C2n) + 1;
wire [15:0] den3 = Di(meanX - stdX, C3) + Di(meanY - stdY, C3n) + 1;

wire [15:0] div1 = (num1*1000)/den1;
wire [15:0] div2 = (num2*1000)/den2;
wire [15:0] div3 = (num3*1000)/den3;

wire [15:0] Prom = (div1 + div2 + div3) / 3;

assign valor_nahid = 1000 - Prom;
assign alerta = (valor_nahid < th);

endmodule