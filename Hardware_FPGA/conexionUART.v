`timescale 1ns / 1ps

module uart_rx(

    input clk,
    input rx,

    output reg [7:0] datos = 0,
    output reg datos_validos = 0
);

parameter clks_por_bit = 10416;

localparam idle        = 0;
localparam bit_inicio  = 1;
localparam datos_bits  = 2;
localparam bit_termino = 3;
localparam limp        = 4;

reg [2:0]  estado       = idle;
reg [13:0] contador_clk = 0;
reg [2:0]  index_bit    = 0;
reg [7:0]  variacion_rx = 0;

always @(posedge clk) begin
    datos_validos <= 0;
    case(estado)
        idle: begin
            contador_clk <= 0;
            index_bit <= 0;
            if (rx == 0)
                estado <= bit_inicio;
        end

        bit_inicio: begin
            if (contador_clk == (clks_por_bit - 1)/2) begin
                if (rx == 0) begin
                    contador_clk <= 0;
                    estado <= datos_bits;
                end
                else
                    estado <= idle;
            end
            else begin
                contador_clk <= contador_clk + 1;
            end
        end

        datos_bits: begin
            if (contador_clk < clks_por_bit - 1)
                contador_clk <= contador_clk + 1;
            else begin
                contador_clk <= 0;
                variacion_rx[index_bit] <= rx;  
                if (index_bit < 7)
                    index_bit <= index_bit + 1;
                else begin
                    index_bit <= 0;
                    estado <= bit_termino;
                end
            end
        end

        bit_termino: begin
            if (contador_clk < clks_por_bit - 1)
                contador_clk <= contador_clk + 1;
            else begin
                datos <= variacion_rx;
                datos_validos <= 1;
                contador_clk <= 0;
                estado <= limp;
            end
        end

        limp:
            estado <= idle;

        default:
            estado <= idle;

    endcase
end
endmodule