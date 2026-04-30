`timescale 1ns / 1ps

module conexionUART (
    input clk,
    input rx,
    output reg [7:0] data = 0,
    output reg data_valid = 0
);

parameter CLKS_PER_BIT = 10416; 

reg [13:0] contador = 0;
reg [3:0] bit_index = 0;
reg [7:0] buffer = 0;
reg recibiendo = 0;

always @(posedge clk) begin

    data_valid <= 0; 

    if (!recibiendo && rx == 0) begin
        recibiendo <= 1;
        contador <= CLKS_PER_BIT/2;
        bit_index <= 0;
    end

    else if (recibiendo) begin

        if (contador < CLKS_PER_BIT-1) begin
            contador <= contador + 1;
        end

        else begin
            contador <= 0;

            if (bit_index < 8) begin
                buffer[bit_index] <= rx;
                bit_index <= bit_index + 1;
            end

            else begin
                data <= buffer;
                data_valid <= 1;   
                recibiendo <= 0;
            end
        end
    end
end

endmodule