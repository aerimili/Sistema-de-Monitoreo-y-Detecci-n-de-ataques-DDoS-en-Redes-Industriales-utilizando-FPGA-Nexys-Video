`timescale 1ns / 1ps

module ddos_message (
    input  wire clk,
    input  wire alerta,
    
    output wire tx
);

localparam [2:0] reset_reg   = 3'd0,
                 esp_alerta  = 3'd1,
                 ld_str      = 3'd2,
                 mandar_char = 3'd3,
                 listo_bajo  = 3'd4,
                 esp_listo   = 3'd5;

localparam [3:0] fin_str         = 4'd12; 
localparam [17:0] reset_cntr_max = 18'd200000;

reg [2:0] estado_uart = reset_reg;
reg mandar_uart       = 0;
reg [7:0] datos_uart  = 0;
reg [3:0] index_str   = 0;   
reg alerta_ff1        = 0;
reg alerta_ff2        = 0;
reg [17:0] reset_cntr = 0;

wire alerta_alto = alerta_ff1 && !alerta_ff2;
wire uart_listo;

always @(posedge clk) begin
    alerta_ff1 <= alerta;
    alerta_ff2 <= alerta_ff1;
end
 

always @(posedge clk) begin
    if (reset_cntr == reset_cntr_max || estado_uart != reset_reg)
       reset_cntr <= 0;
    else
       reset_cntr <= reset_cntr + 1;
end

    
always @(posedge clk) begin
    case (estado_uart)
        reset_reg: begin
            if (reset_cntr == reset_cntr_max)
                estado_uart <= esp_alerta;
        end

        esp_alerta: begin
            if (alerta_alto)
                estado_uart <= ld_str;
        end

        ld_str: begin
            index_str <= 0;
            estado_uart <= mandar_char;
        end

        mandar_char: begin
            mandar_uart <= 1'b1;
            estado_uart <= listo_bajo;
        end

        listo_bajo: begin
            mandar_uart <= 1'b0;
            if (uart_listo == 1'b0)
                estado_uart <= esp_listo;
        end

        esp_listo: begin
            if (uart_listo == 1'b1) begin
                if (index_str == fin_str - 1)
                    estado_uart <= esp_alerta;
                else begin
                    index_str <= index_str + 1;
                    estado_uart <= mandar_char;
                end
            end
        end

        default: estado_uart <= reset_reg;
    endcase
end


always @(*) begin
    case (index_str)
        4'd0:  datos_uart = "A";
        4'd1:  datos_uart = "L";
        4'd2:  datos_uart = "E";
        4'd3:  datos_uart = "R";
        4'd4:  datos_uart = "T";
        4'd5:  datos_uart = "A";
        4'd6:  datos_uart = "_";
        4'd7:  datos_uart = "D";
        4'd8:  datos_uart = "D";
        4'd9:  datos_uart = "O";
        4'd10: datos_uart = "S";
        4'd11: datos_uart = 8'h0A;
        default: datos_uart = 8'h00;
    endcase
end

uart_tx tx_uart (
    .mandar_uart(mandar_uart),
    .datos_uart(datos_uart),
    .clk(clk),
    .uart_listo(uart_listo),
    .tx(tx)
);

endmodule