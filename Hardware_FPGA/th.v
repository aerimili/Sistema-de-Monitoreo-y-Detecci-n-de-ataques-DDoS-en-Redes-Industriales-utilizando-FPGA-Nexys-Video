`timescale 1ns / 1ps

module th_calculator(

    input clk,

    input vector_listo,
    input [15:0] valor_nahid,

    input reset_training,

    output reg [15:0] th = 0,
    output reg listo = 0,

    // DEBUG
    output reg [31:0] acumulado = 0,
    output reg [15:0] contador = 0,
    output reg [15:0] promedio = 0
);

parameter MARGEN = 20;

reg [15:0] nahid_reg = 0;

always @(posedge clk) begin

    nahid_reg <= valor_nahid;

    if (reset_training) begin

        acumulado <= 0;
        contador  <= 0;

        promedio  <= 0;

        th        <= 0;
        listo     <= 0;
    end

    else if (vector_listo && !listo) begin

        acumulado <= acumulado + nahid_reg;

        if (contador == 1023) begin

            promedio <= (acumulado + nahid_reg) >> 10;

            if (((acumulado + nahid_reg) >> 10) > MARGEN)
                th <= ((acumulado + nahid_reg) >> 10) - MARGEN;
            else
                th <= 0;

            listo <= 1;
        end

        contador <= contador + 1;
    end
end

endmodule
