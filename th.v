`timescale 1ns / 1ps

module th_calculator(
    input clk,
    input [15:0] valor_nahid,
    input valid,            
    input start_training,   

    output reg [15:0] th = 0,
    output reg listo = 0   
);

parameter N = 256;  // cantidad de muestras

reg [31:0] acumulado = 0;
reg [15:0] contador = 0;
reg entrenando = 0;

always @(posedge clk) begin


    if (start_training) begin
        acumulado <= 0;
        contador <= 0;
        entrenando <= 1;
        listo <= 0;
    end

    else if (entrenando && valid) begin
        acumulado <= acumulado + valor_nahid;
        contador <= contador + 1;

        if (contador == N) begin
            th <= (acumulado >> 8) - 50; 
            entrenando <= 0;
            listo <= 1;
        end
    end

end

endmodule
