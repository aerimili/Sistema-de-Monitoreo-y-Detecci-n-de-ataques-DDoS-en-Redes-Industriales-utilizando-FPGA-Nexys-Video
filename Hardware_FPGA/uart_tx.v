`timescale 1ns / 1ps

module uart_tx (
    input  wire       mandar_uart,
    input  wire [7:0] datos_uart,
    input  wire       clk,
    
    output wire       uart_listo,
    output wire       tx
);

localparam [1:0]  listo         = 2'b00;
localparam [1:0]  cargar_bit    = 2'b01;
localparam [1:0]  mandar_bit    = 2'b10;
localparam [13:0] tmr_bit_max   = 14'd10415; 
localparam [3:0]  index_bit_max = 4'd10;

reg [1:0]  estado_tx = listo;
reg [13:0] tmr_bit   = 0;
reg [3:0]  index_bit = 0;
reg [9:0]  datos_tx    = 10'b1111111111;
reg        bit_tx     = 1'b1;

wire bit_listo = (tmr_bit == tmr_bit_max);


always @(posedge clk) begin
    case (estado_tx)
        listo: begin
            if (mandar_uart) estado_tx <= cargar_bit;
        end
        
        cargar_bit: begin
            estado_tx <= mandar_bit;
        end
        
        mandar_bit: begin
            if (bit_listo) begin
                if (index_bit == index_bit_max) estado_tx <= listo;
                else estado_tx <= cargar_bit;
            end
        end
        default: estado_tx <= listo;
    endcase
end


always @(posedge clk) begin
    if (estado_tx == listo || bit_listo) tmr_bit <= 0;
    else tmr_bit <= tmr_bit + 1;
end


always @(posedge clk) begin
        if (estado_tx == listo) index_bit <= 0;
        else if (estado_tx == cargar_bit) index_bit <= index_bit + 1;
end


always @(posedge clk) begin
    if (mandar_uart && estado_tx == listo) datos_tx <= {1'b1, datos_uart, 1'b0};
end


always @(posedge clk) begin
    if (estado_tx == listo) bit_tx <= 1'b1;
    else if (estado_tx == cargar_bit) bit_tx <= datos_tx[index_bit];
end

assign tx         = bit_tx;
assign uart_listo = (estado_tx == listo);

endmodule
